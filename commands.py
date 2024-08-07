import calendar
from datetime import datetime
import os
import logging
from telegram import Update
from telegram.ext import ContextTypes
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs

from restrictions import restricted
from settings import CREDENTIALS_FILE, SAMPLE_SPREADSHEET_ID, SCOPES
from spreadsheets import retrieve_summary_data
from charts import generate_pie_chart

# Store user credentials in memory for simplicity
user_credentials = {}

MONTHS_SPANISH = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
]

@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in user_credentials:
        await create_spreadsheet(update, context, user_credentials[chat_id])
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        flow.redirect_uri = 'http://localhost:8080/'
        auth_url, _ = flow.authorization_url(prompt='consent')
        context.user_data['flow'] = flow
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Hola {update.message.from_user.full_name} 👋! Soy Presupuesbot, tu asistente financiero.",
            parse_mode="Markdown"
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Primero, autoriza el acceso a tu cuenta de Google [dando click aqui]({auth_url}).\n"
                 f"\n- *Después de autorizar tu cuenta, serás redireccionado a una URL con un error (esto es normal y esperado).*\n"
                 f"\n- *Cuando pase esto, comparteme el link en este chat, y yo me encargaré de crear la hoja de cálculo en tu cuenta de Google.*",
            parse_mode="Markdown"
        )

async def handle_auth_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if 'flow' in context.user_data:
        flow = context.user_data['flow']
        full_url = update.message.text.strip()
        parsed_url = urlparse(full_url)
        auth_code = parse_qs(parsed_url.query).get('code', [None])[0]
        if auth_code:
            flow.fetch_token(code=auth_code)
            creds = flow.credentials
            user_credentials[chat_id] = creds
            await create_spreadsheet(update, context, creds)
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Link inválido. Asegrate de que estés enviando el link completo."
            )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Por favor, inicia el proceso de autorización enviando /start"
        )

async def create_spreadsheet(update: Update, context: ContextTypes.DEFAULT_TYPE, creds: Credentials):
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Create a new spreadsheet
        spreadsheet = {
            'properties': {
                'title': 'PRESUPUESTO'
            }
        }
        request = service.spreadsheets().create(body=spreadsheet)
        response = request.execute()

        # Get the ID of the default sheet
        default_sheet_id = response['sheets'][0]['properties']['sheetId']

        # Get the sheet ID by name from the template
        template_spreadsheet = service.spreadsheets().get(spreadsheetId=SAMPLE_SPREADSHEET_ID).execute()
        sheet_name = 'MES AÑO'  # Replace with your sheet name
        sheet_id = None
        for sheet in template_spreadsheet['sheets']:
            if sheet['properties']['title'] == sheet_name:
                sheet_id = sheet['properties']['sheetId']
                break

        if sheet_id is None:
            raise ValueError(f"Sheet with name '{sheet_name}' not found in template spreadsheet.")

        # Copy the content from the template
        copy_sheet_to_another_spreadsheet_request_body = {
            'destinationSpreadsheetId': response['spreadsheetId']
        }
        copied_sheet = service.spreadsheets().sheets().copyTo(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            sheetId=sheet_id,
            body=copy_sheet_to_another_spreadsheet_request_body
        ).execute()

        # Delete the default sheet
        delete_sheet_request = {
            'requests': [
                {
                    'deleteSheet': {
                        'sheetId': default_sheet_id
                    }
                }
            ]
        }
        service.spreadsheets().batchUpdate(
            spreadsheetId=response['spreadsheetId'],
            body=delete_sheet_request
        ).execute()
        
        # Get the current month and year in Spanish
        now = datetime.now()
        month_name = MONTHS_SPANISH[now.month - 1]
        year = now.year
        new_sheet_name = f"{month_name} {year}"

        # Rename the copied sheet to the desired name
        rename_sheet_request = {
            'requests': [
                {
                    'updateSheetProperties': {
                        'properties': {
                            'sheetId': copied_sheet['sheetId'],
                            'title': new_sheet_name
                        },
                        'fields': 'title'
                    }
                }
            ]
        }
        service.spreadsheets().batchUpdate(
            spreadsheetId=response['spreadsheetId'],
            body=rename_sheet_request
        ).execute()
        
        # Update the PERIODO INICIO and PERIODO FIN cells
        start_date = datetime(year, now.month, 1).strftime("%d/%m/%y")
        end_date = datetime(year, now.month, calendar.monthrange(year, now.month)[1]).strftime("%d/%m/%y")
        update_cells_request = {
            'valueInputOption': 'USER_ENTERED',
            'data': [
                {
                    'range': f"{new_sheet_name}!F2",
                    'values': [[start_date]]
                },
                {
                    'range': f"{new_sheet_name}!G2",
                    'values': [[end_date]]
                }
            ]
        }
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=response['spreadsheetId'],
            body=update_cells_request
        ).execute()

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"La hoja de cálculo ha sido creada en tu cuenta de Google Sheets como *PRESUPUESTO*.\n"
                 f"\nPuedes acceder a ella [dando click aquí]({response['spreadsheetUrl']}).\n"
                 f"\n*Todas las transacciones y consultas que realices en este chat estarán disponibles y se guardarán ahí.*",
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Error creating spreadsheet: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="No se ha podido crear la hoja de cálculo."
        )

@restricted
async def actual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sections: 
        - RESUMEN (CATEGORIA, GASTADO, RESTANTE, LIMITE)
        - TIPO DE PAGO (CATEGORIA, GASTADO)
        - AHORROS (PORTAFOLIO, INVERTIDO, RENDIMIENTO, TOTAL, FECHA DE CAPTURA)
        - ¿CUANTO GASTE ENTRE fecha1 Y fecha2?
    """

    summary_data, sheet_title = retrieve_summary_data(
        worksheet_name="BUDGETING", sheet_index=-1
    )

    summary_keys = list(summary_data.keys())[3:-1]
    summary_values = list(summary_data.values())[3:-1]

    pie_chart_filename = generate_pie_chart(
        keys=summary_keys, values=summary_values, chart_title=sheet_title
    )

    await context.bot.send_photo(
        chat_id=update.effective_chat.id, photo=open(pie_chart_filename, "rb")
    )

    os.remove(pie_chart_filename)
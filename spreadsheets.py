import calendar
from datetime import datetime
from telegram.ext import ContextTypes
from google.oauth2.credentials import Credentials

import logging
import gspread
from telegram import Update

from googleapiclient.discovery import build

from settings import SAMPLE_SPREADSHEET_ID

gc = gspread.service_account(filename=".config/gspread/service_account.json")

MONTHS_SPANISH = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
]

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

        template_spreadsheet = service.spreadsheets().get(spreadsheetId=SAMPLE_SPREADSHEET_ID).execute()
        sheet_name = 'MES AÑO'
        sheet_id = None
        for sheet in template_spreadsheet['sheets']:
            if sheet['properties']['title'] == sheet_name:
                sheet_id = sheet['properties']['sheetId']
                break

        if sheet_id is None:
            raise ValueError(f"Sheet with name '{sheet_name}' not found in template spreadsheet.")

        copy_sheet_to_another_spreadsheet_request_body = {
            'destinationSpreadsheetId': response['spreadsheetId']
        }
        copied_sheet = service.spreadsheets().sheets().copyTo(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            sheetId=sheet_id,
            body=copy_sheet_to_another_spreadsheet_request_body
        ).execute()

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
        
        now = datetime.now()
        month_name = MONTHS_SPANISH[now.month - 1]
        year = now.year
        new_sheet_name = f"{month_name} {year}"

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
        
        return response['spreadsheetUrl']  # Return the spreadsheet URL
    except Exception as e:
        logging.error(f"Error creating spreadsheet: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="No se ha podido crear la hoja de cálculo."
        )
        return None
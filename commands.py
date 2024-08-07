from telegram import Update
from telegram.ext import ContextTypes
from google_auth_oauthlib.flow import InstalledAppFlow
from urllib.parse import urlparse, parse_qs
import gspread

from restrictions import restricted
from settings import CREDENTIALS_FILE, SCOPES
from spreadsheets import create_spreadsheet
from storage import load_template_status, save_template_status, load_user_credentials, save_user_credentials

template_status = load_template_status()  # Load template status from file
user_credentials = {}

@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    if chat_id in template_status and template_status[chat_id].get('created'):
        spreadsheet_link = template_status[chat_id].get('link')
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"La hoja de cálculo ya ha sido creada en tu cuenta de Google. Accede a ella [aquí]({spreadsheet_link}).",
            parse_mode="Markdown"
        )
        return

    if chat_id in user_credentials:
        spreadsheet_link = await create_spreadsheet(update, context, user_credentials[chat_id])
        if spreadsheet_link:
            template_status[chat_id] = {'created': True, 'link': spreadsheet_link}
            save_template_status(template_status)  # Save status to file
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

@restricted
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
            save_user_credentials(chat_id, creds)  # Save credentials to file
            spreadsheet_link = await create_spreadsheet(update, context, creds)
            if spreadsheet_link:
                template_status[chat_id] = {'created': True, 'link': spreadsheet_link}  # Mark template as created and store link
                save_template_status(template_status)  # Save status to file
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

@restricted
async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    if chat_id not in template_status or not template_status[chat_id].get('created'):
        await context.bot.send_message(
            chat_id=chat_id,
            text="Primero debes crear la hoja de cálculo usando el comando /start."
        )
        return

    if len(context.args) < 2:
        await context.bot.send_message(
            chat_id=chat_id,
            text="""
            Por favor, proporciona el nombre de la categoría y el límite en pesos mexicanos.\n 
            Ejemplo: /agregar_categoria DESPENSA 5000
            """,
            parse_mode="Markdown"
        )
        return

    category_name = context.args[0].upper()
    limit = context.args[1]
    try:
        limit = float(limit)
    except ValueError:
        await context.bot.send_message(
            chat_id=chat_id,
            text="El límite debe ser un número válido. Ejemplo: /agregar_categoria DESPENSA 5000.50",
            parse_mode="Markdown"
        )
        return

    # Authenticate and open the spreadsheet
    creds = load_user_credentials(chat_id)
    if not creds:
        await context.bot.send_message(
            chat_id=chat_id,
            text="No se encontraron credenciales. Por favor, autoriza el acceso a tu cuenta de Google usando el comando /start."
        )
        return

    try:
        print(f"Using credentials for chat_id {chat_id}")
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_url(template_status[chat_id]['link'])
        worksheet = spreadsheet.sheet1

        # Check if category already exists
        existing_categories = [category for category in worksheet.col_values(6)[3:15] if category]  # F4 to F15
        print(f"Existing categories: {existing_categories}")
        if category_name in existing_categories:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"La categoría '{category_name}' ya existe."
            )
            return

        # Find the next available row
        next_row = 4 + len(existing_categories)
        print(f"Next row: {next_row}")
        if next_row > 15:
            await context.bot.send_message(
                chat_id=chat_id,
                text="No puedes agregar más de 12 categorías."
            )
            return

        # Add the category and limit to the sheet
        worksheet.update_cell(next_row, 6, category_name)  # Column F
        worksheet.update_cell(next_row, 9, limit)  # Column I

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Categoría '{category_name}' con límite {limit} ha sido agregada."
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Error al agregar la categoría: {e}"
        )

@restricted
async def modify_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    print(f"Chat ID: {chat_id}")
    print(f"Template status: {template_status}")
    print(f"Template status for chat_id {chat_id}: {template_status.get(chat_id)}")
    if chat_id not in template_status:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Primero debes crear la hoja de cálculo usando el comando /start."
        )
        return

    if len(context.args) < 2:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Por favor, proporciona el nombre de la categoria actual y al menos uno de los siguientes: el nuevo nombre o el nuevo límite en pesos mexicanos."
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text="""
            Ejemplos: 
            /modificar_categoria <nombre> <nuevo-nombre> <nuevo-limite>
            /modificar_categoria SALIDAS DESPENSA 6000
            /modificar_categoria SALIDAS 6000
            /modificar_categoria SALIDAS ALIMENTOS
            """
        )
        return

    old_category_name = context.args[0].upper()
    new_category_name = None
    new_limit = None

    if len(context.args) == 2:
        try:
            new_limit = float(context.args[1])
        except ValueError:
            new_category_name = context.args[1].upper()
    elif len(context.args) == 3:
        new_category_name = context.args[1].upper()
        try:
            new_limit = float(context.args[2])
        except ValueError:
            await context.bot.send_message(
                chat_id=chat_id,
                text="El límite debe ser un número válido. Ejemplo: /modificar_categoria DESPENSA ALIMENTOS 6000.50",
                parse_mode="Markdown"
            )
            return

    creds = load_user_credentials(chat_id)
    if not creds:
        await context.bot.send_message(
            chat_id=chat_id,
            text="No se encontraron credenciales. Por favor, autoriza el acceso a tu cuenta de Google usando el comando /start."
        )
        return

    try:
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_url(template_status[chat_id]['link'])
        worksheet = spreadsheet.sheet1

        existing_categories = [category for category in worksheet.col_values(6)[3:15] if category]  # F4 to F15
        if old_category_name not in existing_categories:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"La categoría '{old_category_name}' no existe."
            )
            return

        row_index = existing_categories.index(old_category_name) + 4  # Adjust for 0-based index and header rows

        if new_category_name:
            worksheet.update_cell(row_index, 6, new_category_name)  # Column F
        if new_limit is not None:
            worksheet.update_cell(row_index, 9, new_limit)  # Column I

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Categoría '{old_category_name}' ha sido modificada."
        )
        
        if new_category_name:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Categoría '{old_category_name}' ha sido modificada a '{new_category_name}'."
            )
        if new_limit and new_category_name:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Límite de la categoría '{old_category_name}' ha sido modificado a {new_limit}."
            )
        elif new_limit:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Límite de la categoría '{old_category_name}' ha sido modificado a {new_limit}."
            )
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Error al modificar la categoría: {e}"
        )
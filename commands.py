import gspread

from telegram import Update

from telegram.ext import ContextTypes

from restrictions import restricted


@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Bienvenido a Botgeting."
    )

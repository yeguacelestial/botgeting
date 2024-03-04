import os

from telegram import Update

from telegram.ext import ContextTypes

from restrictions import restricted
from spreadsheets import retrieve_summary_data
from charts import generate_pie_chart


@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Bienvenido a Botgeting."
    )


@restricted
async def actual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    summary_data, sheet_title = retrieve_summary_data(
        worksheet_name="BUDGETING", sheet_index=-2
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

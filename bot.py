import logging

from settings import TOKEN

from telegram.ext import (
    CommandHandler,
    ApplicationBuilder,
)

from commands import start

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

application = ApplicationBuilder().token(TOKEN).build()

start_handler = CommandHandler("start", start)
application.add_handler(start_handler)

application.run_polling()

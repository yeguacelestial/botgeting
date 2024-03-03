import logging
from settings import TOKEN

from telegram.ext import (
    CommandHandler,
    ApplicationBuilder,
)

from commands import start, actual

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

application = ApplicationBuilder().token(TOKEN).build()

# Handlers
start_handler = CommandHandler("start", start)
actual_handler = CommandHandler("actual", actual)

application.add_handler(start_handler)
application.add_handler(actual_handler)

application.run_polling()

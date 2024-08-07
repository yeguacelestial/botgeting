import logging
from settings import TOKEN

from telegram.ext import (
    CommandHandler,
    ApplicationBuilder,
    MessageHandler,
    filters
)

from commands import handle_auth_code, start

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

application = ApplicationBuilder().token(TOKEN).build()

# Handlers
start_handler = CommandHandler("start", start)
auth_code_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_auth_code)

application.add_handler(start_handler)
application.add_handler(auth_code_handler)

application.run_polling()
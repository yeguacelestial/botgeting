import logging
from settings import TOKEN

from telegram.ext import (
    CommandHandler,
    ApplicationBuilder,
    MessageHandler,
    filters
)

from telegram.ext import CallbackQueryHandler

from commands import add_category, edit_choice, handle_auth_code, modify_category, select_category, start, category_selected

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

application = ApplicationBuilder().token(TOKEN).build()

# Handlers
start_handler = CommandHandler("start", start)
auth_code_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_auth_code)
add_category_handler = CommandHandler("agregar_categoria", add_category)
modify_category_handler = CommandHandler("modificar_categoria", select_category)
category_selected_handler = CallbackQueryHandler(category_selected, pattern='^select_')
edit_choice_handler = CallbackQueryHandler(edit_choice, pattern='^edit_')

application.add_handler(start_handler)
application.add_handler(auth_code_handler)
application.add_handler(add_category_handler)
application.add_handler(modify_category_handler)
application.add_handler(category_selected_handler)
application.add_handler(edit_choice_handler)

application.run_polling()
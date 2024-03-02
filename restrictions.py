from functools import wraps
from dotenv import load_dotenv
from os import getenv

load_dotenv()
ADMIN_USER_ID = getenv("ADMIN_USER_ID", "")

LIST_OF_ADMINS = [
    ADMIN_USER_ID,
]


def restricted(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id = str(update.effective_user.id)
        if user_id not in LIST_OF_ADMINS:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text="Unauthorized access."
            )
            return
        return await func(update, context, *args, **kwargs)

    return wrapped

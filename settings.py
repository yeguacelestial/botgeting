from typing import Final
from dotenv import load_dotenv
from os import getenv

load_dotenv()

TOKEN: Final = getenv("TOKEN", "")
BOT_USERNAME = Final = getenv("BOT_USERNAME", "")

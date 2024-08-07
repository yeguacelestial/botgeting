from typing import Final
from dotenv import load_dotenv
from os import getenv

load_dotenv()

TOKEN: Final = getenv("TOKEN", "")
BOT_USERNAME = Final = getenv("BOT_USERNAME", "")

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = getenv("CREDENTIALS_FILE", "")
SAMPLE_SPREADSHEET_ID = getenv("SAMPLE_SPREADSHEET_ID", "")
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import hashlib
from src.constants import CREDENTIALS_FILE, SHEET_NAME, AUDIO_DIR


def get_data_from_google_sheet():
    # Authenticate using the Path object from constants
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    # helper: convert Path object to string for the library if it requires strings
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        str(CREDENTIALS_FILE), scope
    )
    client = gspread.authorize(creds)

    sheet = client.open(SHEET_NAME).sheet1
    records = sheet.get_all_records()

    notes = []

    for row in records:
        if not row["sw_word"]:
            continue

        sw_word = row["sw_word"].strip()
        safe_filename = "".join([c for c in sw_word if c.isalnum()])

        # Audio paths are now relative to the constant AUDIO_DIR
        audio_word_filename = f"se_{safe_filename}.mp3"

        # Full path for file checking (Path object)
        full_audio_path = AUDIO_DIR / audio_word_filename

        # ... rest of your logic ...

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import hashlib
from src.constants import CREDENTIALS_FILE, SHEET_NAME, AUDIO_DIR


def get_data_from_google_sheet():
    print(f"Connecting to Google Sheet: {SHEET_NAME}...")

    # 1. Authenticate using the path from constants
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        str(CREDENTIALS_FILE), scope
    )
    client = gspread.authorize(creds)

    # 2. Open Sheet and Get All Records
    try:
        sheet = client.open(SHEET_NAME).sheet1
        records = sheet.get_all_records()
    except Exception as e:
        print(f"ERROR: Could not open sheet. Check permissions. \nDetails: {e}")
        return []

    notes = []
    print(f"Fetched {len(records)} rows from Google Sheets.")

    for row in records:
        # Skip empty rows or rows without a Swedish word
        if not row.get("sw_word"):
            continue

        sw_word = row["sw_word"].strip()

        # Deterministic Filenames
        safe_filename = "".join([c for c in sw_word if c.isalnum()])
        audio_word_file = f"se_{safe_filename}.mp3"
        audio_sent_file = f"se_sent_{safe_filename}.mp3"

        # Create the Note Object
        note = {
            "guid": int(
                hashlib.sha256(
                    (sw_word + row.get("pos", "")).encode("utf-8")
                ).hexdigest()[:10],
                16,
            ),
            "fields": [
                row.get("sw_word", ""),
                row.get("en_definition", ""),
                row.get("context_hint", ""),
                row.get("pos", ""),
                row.get("gender", ""),
                row.get("sw_sentence", ""),
                row.get("en_sentence", ""),
                f"[sound:{audio_word_file}]",
                f"[sound:{audio_sent_file}]",
            ],
            "meta_audio_gen": {
                "word_text": row.get("sw_word", ""),
                "word_file": audio_word_file,
                "sent_text": row.get("sw_sentence", ""),
                "sent_file": audio_sent_file,
            },
        }
        notes.append(note)

    # CRITICAL FIX: This was missing!
    return notes

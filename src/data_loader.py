import gspread
from oauth2client.service_account import ServiceAccountCredentials
import hashlib
from src.constants import CREDENTIALS_FILE, SHEET_NAME, AUDIO_DIR


def get_data_from_google_sheet():
    print(f"Connecting to Google Sheet: {SHEET_NAME}...")

    # 1. Authenticate
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        str(CREDENTIALS_FILE), scope
    )
    client = gspread.authorize(creds)

    # 2. Open Sheet and Get Raw Values (NOT records)
    try:
        sheet = client.open(SHEET_NAME).sheet1
        # get_all_values returns a list of lists, ignoring header uniqueness rules
        all_rows = sheet.get_all_values()
    except Exception as e:
        print(f"ERROR: Could not open sheet. Check permissions. \nDetails: {e}")
        return []

    if not all_rows:
        print("Sheet is empty.")
        return []

    # 3. Parse Headers manually
    # Row 0 contains headers. We map 'sw_word' -> Column Index 0, etc.
    headers = [h.strip() for h in all_rows[0]]
    header_map = {name: index for index, name in enumerate(headers) if name}

    data_rows = all_rows[1:]  # Everything after the header
    notes = []

    print(f"Fetched {len(data_rows)} rows. Processing...")

    # Helper function to get data safely by column name
    def get_val(row_list, col_name):
        idx = header_map.get(col_name)
        # Return empty string if column doesn't exist or row is too short
        if idx is None or idx >= len(row_list):
            return ""
        return row_list[idx].strip()

    for row_values in data_rows:
        sw_word = get_val(row_values, "sw_word")

        # Skip empty rows
        if not sw_word:
            continue

        # Deterministic Filenames
        safe_filename = "".join([c for c in sw_word if c.isalnum()])
        audio_word_file = f"se_{safe_filename}.mp3"
        audio_sent_file = f"se_sent_{safe_filename}.mp3"

        # Create the Note Object using the helper
        note = {
            "guid": int(
                hashlib.sha256(
                    (sw_word + get_val(row_values, "pos")).encode("utf-8")
                ).hexdigest()[:10],
                16,
            ),
            "fields": [
                sw_word,  # WordSE
                get_val(row_values, "en_definition"),  # WordEN
                get_val(row_values, "context_hint"),  # ContextHint
                get_val(row_values, "pos"),  # POS
                get_val(row_values, "gender"),  # Gender
                get_val(row_values, "sw_sentence"),  # SentenceSE
                get_val(row_values, "en_sentence"),  # SentenceEN
                f"[sound:{audio_word_file}]",
                f"[sound:{audio_sent_file}]",
            ],
            "meta_audio_gen": {
                "word_text": sw_word,
                "word_file": audio_word_file,
                "sent_text": get_val(row_values, "sw_sentence"),
                "sent_file": audio_sent_file,
            },
        }
        notes.append(note)

    return notes

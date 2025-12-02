import gspread
from oauth2client.service_account import ServiceAccountCredentials
import hashlib
from src.constants import CREDENTIALS_FILE, SHEET_NAME


def get_data_from_google_sheet():
    print(f"Connecting to Google Sheet: {SHEET_NAME}...")

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        str(CREDENTIALS_FILE), scope
    )
    client = gspread.authorize(creds)

    try:
        sheet = client.open(SHEET_NAME).sheet1
        all_rows = sheet.get_all_values()
    except Exception as e:
        print(f"ERROR: Could not open sheet. {e}")
        return []

    if not all_rows:
        return []

    headers = [h.strip() for h in all_rows[0]]
    header_map = {name: index for index, name in enumerate(headers) if name}

    data_rows = all_rows[1:]
    notes = []

    print(f"Fetched {len(data_rows)} rows. Processing...")

    def get_val(row_list, col_name):
        idx = header_map.get(col_name)
        if idx is None or idx >= len(row_list):
            return ""
        return row_list[idx].strip()

    for row_values in data_rows:
        sw_word = get_val(row_values, "sw_word")
        if not sw_word:
            continue

        sw_sentence = get_val(row_values, "sw_sentence")
        pos = get_val(row_values, "pos")
        context_hint = get_val(row_values, "context_hint")

        # 1. Base Filename (Safe for OS)
        safe_word = "".join([c for c in sw_word if c.isalnum()])

        # 2. WORD Audio Filename
        # For homonyms (får vs får), the WORD sounds the same, so they can share this file.
        audio_word_file = f"se_{safe_word}.mp3"

        # 3. SENTENCE Audio Filename (THE FIX)
        # We append a hash of the sentence itself so "Jag får..." and "Får jag..." get different files.
        if sw_sentence:
            sent_hash = hashlib.md5(sw_sentence.encode("utf-8")).hexdigest()[:6]
            audio_sent_file = f"se_sent_{safe_word}_{sent_hash}.mp3"
        else:
            audio_sent_file = ""  # No audio tag if no sentence

        # 4. Unique ID Generation (THE FIX)
        # We add 'context_hint' to the hash so Anki treats the two "får" cards as unique.
        unique_string = sw_word + pos + context_hint
        note_guid = int(
            hashlib.sha256(unique_string.encode("utf-8")).hexdigest()[:10], 16
        )

        note = {
            "guid": note_guid,
            "fields": [
                sw_word,
                get_val(row_values, "en_definition"),
                context_hint,
                pos,
                get_val(row_values, "gender"),
                sw_sentence,
                get_val(row_values, "en_sentence"),
                f"[sound:{audio_word_file}]",
                f"[sound:{audio_sent_file}]" if audio_sent_file else "",
            ],
            "meta_audio_gen": {
                "word_text": sw_word,
                "word_file": audio_word_file,
                "sent_text": sw_sentence,
                "sent_file": audio_sent_file,
            },
        }
        notes.append(note)

    return notes

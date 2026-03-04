"""Google Sheets authentication and vocabulary row parsing."""

import hashlib

import gspread

from src.constants import CREDENTIALS_FILE, GUID_HASH_LENGTH, SENT_HASH_LENGTH

__all__ = ["get_data_from_google_sheet"]

_gspread_client: gspread.Client | None = None


def _get_gspread_client() -> gspread.Client:
    """Return the shared gspread client, initialising it on first call.

    Returns:
        An authenticated :class:`gspread.Client`.
    """
    global _gspread_client
    if _gspread_client is None:
        _gspread_client = gspread.service_account(filename=str(CREDENTIALS_FILE))
    return _gspread_client


def get_data_from_google_sheet(
    sheet_name: str | None = None,
) -> list[dict[str, object]]:
    """Fetch vocabulary rows from a Google Sheet and return structured note dicts.

    Authenticates via a service-account JSON key, reads all rows from the first
    worksheet, and converts each non-empty row into a note dict ready for audio
    generation and Anki packaging.

    Args:
        sheet_name: Title of the Google Sheet to open. Defaults to
            "Swedish Vocabulary Master" when ``None`` or empty.

    Returns:
        A list of note dicts, each containing ``guid``, ``fields``, and
        ``meta_audio_gen`` keys.  Returns an empty list when the sheet cannot
        be opened or contains no data rows.
    """
    if not sheet_name:
        sheet_name = "Swedish Vocabulary Master"
    print(f"Connecting to Google Sheet: {sheet_name}...")

    client = _get_gspread_client()

    try:
        sheet = client.open(sheet_name).sheet1
        all_rows = sheet.get_all_values()
    except (gspread.exceptions.SpreadsheetNotFound, gspread.exceptions.APIError) as e:
        print(f"ERROR: Could not open sheet. {e}")
        return []

    if not all_rows:
        return []

    headers = [h.strip() for h in all_rows[0]]
    header_map = {name: index for index, name in enumerate(headers) if name}

    data_rows = all_rows[1:]
    notes: list[dict[str, object]] = []

    print(f"Fetched {len(data_rows)} rows. Processing...")

    def get_val(row_list: list[str], col_name: str) -> str:
        """Return the stripped cell value for *col_name* in *row_list*.

        Args:
            row_list: A single data row from the worksheet.
            col_name: The header name to look up.

        Returns:
            The stripped string value, or ``""`` if the column is absent or the
            row is too short.
        """
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
        # Homonyms (e.g. "får" vs "får") sound the same, so they share this file.
        audio_word_file = f"se_{safe_word}.mp3"

        # 3. SENTENCE Audio Filename
        # Append a sentence hash so "Jag får..." and "Får jag..." get different files.
        if sw_sentence:
            sent_hash = hashlib.md5(
                sw_sentence.encode("utf-8"), usedforsecurity=False
            ).hexdigest()[:SENT_HASH_LENGTH]
            audio_sent_file = f"se_sent_{safe_word}_{sent_hash}.mp3"
        else:
            audio_sent_file = ""

        # 4. Unique ID Generation
        # Add 'context_hint' to the hash so Anki treats the two "får" cards as unique.
        unique_string = sw_word + pos + context_hint
        note_guid = int(
            hashlib.sha256(unique_string.encode("utf-8")).hexdigest()[
                :GUID_HASH_LENGTH
            ],
            16,
        )

        note: dict[str, object] = {
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

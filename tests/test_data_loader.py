"""Tests for src.data_loader."""

from unittest.mock import MagicMock, patch

import gspread

from src.data_loader import get_data_from_google_sheet

HEADERS = [
    "sw_word",
    "en_definition",
    "pos",
    "gender",
    "context_hint",
    "sw_sentence",
    "en_sentence",
]

SAMPLE_ROW = [
    "huset",
    "the house",
    "noun",
    "ett",
    "ett-word",
    "Det är ett hus.",
    "It is a house.",
]


def _make_sheet_mock(rows: list[list[str]]) -> MagicMock:
    sheet = MagicMock()
    sheet.get_all_values.return_value = rows
    return sheet


def _make_client_mock(sheet: MagicMock) -> MagicMock:
    client = MagicMock()
    client.open.return_value.sheet1 = sheet
    return client


class TestGetDataFromGoogleSheet:
    def test_parses_row_into_note_dict(self) -> None:
        """A valid data row should produce a note dict with correct field ordering."""
        rows = [HEADERS, SAMPLE_ROW]
        sheet = _make_sheet_mock(rows)
        client = _make_client_mock(sheet)

        with (
            patch("src.data_loader.ServiceAccountCredentials") as mock_creds,
            patch("src.data_loader.gspread.authorize", return_value=client),
        ):
            mock_creds.from_json_keyfile_name.return_value = MagicMock()
            notes = get_data_from_google_sheet("Swedish Vocabulary Master")

        assert len(notes) == 1
        note = notes[0]
        fields = note["fields"]
        assert fields[0] == "huset"  # WordSE
        assert fields[1] == "the house"  # WordEN
        assert fields[2] == "ett-word"  # ContextHint
        assert fields[3] == "noun"  # POS
        assert fields[4] == "ett"  # Gender
        assert "[sound:se_huset.mp3]" in fields[7]  # AudioWord

    def test_skips_rows_with_no_sw_word(self) -> None:
        """Rows where sw_word is empty should be omitted from the result."""
        rows = [HEADERS, ["", "no word", "noun", "", "", "", ""]]
        sheet = _make_sheet_mock(rows)
        client = _make_client_mock(sheet)

        with (
            patch("src.data_loader.ServiceAccountCredentials") as mock_creds,
            patch("src.data_loader.gspread.authorize", return_value=client),
        ):
            mock_creds.from_json_keyfile_name.return_value = MagicMock()
            notes = get_data_from_google_sheet()

        assert notes == []

    def test_returns_empty_on_spreadsheet_not_found(self) -> None:
        """SpreadsheetNotFound should be caught and return an empty list."""
        client = MagicMock()
        client.open.side_effect = gspread.exceptions.SpreadsheetNotFound

        with (
            patch("src.data_loader.ServiceAccountCredentials") as mock_creds,
            patch("src.data_loader.gspread.authorize", return_value=client),
        ):
            mock_creds.from_json_keyfile_name.return_value = MagicMock()
            notes = get_data_from_google_sheet("Missing Sheet")

        assert notes == []

    def test_empty_sheet_returns_empty_list(self) -> None:
        """A sheet with no rows should return an empty list."""
        sheet = _make_sheet_mock([])
        client = _make_client_mock(sheet)

        with (
            patch("src.data_loader.ServiceAccountCredentials") as mock_creds,
            patch("src.data_loader.gspread.authorize", return_value=client),
        ):
            mock_creds.from_json_keyfile_name.return_value = MagicMock()
            notes = get_data_from_google_sheet()

        assert notes == []

    def test_no_sentence_produces_empty_audio_sent_field(self) -> None:
        """Rows without sw_sentence should have an empty AudioSentence field."""
        row_no_sentence = ["huset", "the house", "noun", "ett", "ett-word", "", ""]
        rows = [HEADERS, row_no_sentence]
        sheet = _make_sheet_mock(rows)
        client = _make_client_mock(sheet)

        with (
            patch("src.data_loader.ServiceAccountCredentials") as mock_creds,
            patch("src.data_loader.gspread.authorize", return_value=client),
        ):
            mock_creds.from_json_keyfile_name.return_value = MagicMock()
            notes = get_data_from_google_sheet()

        assert notes[0]["fields"][8] == ""  # AudioSentence

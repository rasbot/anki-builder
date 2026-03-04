"""Tests for src.deck_builder."""

from unittest.mock import MagicMock, patch

import pytest

from src.deck_builder import build_anki_deck


def _make_note(sw_word: str = "huset") -> dict[str, object]:
    """Return a minimal note dict suitable for build_anki_deck."""
    return {
        "guid": 123456789,
        "fields": [
            sw_word,
            "the house",
            "ett-word",
            "noun",
            "ett",
            "",
            "",
            "[sound:se_huset.mp3]",
            "",
        ],
        "meta_audio_gen": {
            "word_text": sw_word,
            "word_file": "se_huset.mp3",
            "sent_text": "",
            "sent_file": "",
        },
    }


class TestBuildAnkiDeck:
    def test_raises_value_error_when_no_sheet_name(self) -> None:
        """build_anki_deck should raise ValueError when sheet_name is None."""
        with pytest.raises(ValueError, match="No sheet name passed"):
            build_anki_deck([_make_note()], sheet_name=None)

    def test_raises_value_error_when_empty_sheet_name(self) -> None:
        """build_anki_deck should raise ValueError when sheet_name is empty string."""
        with pytest.raises(ValueError, match="No sheet name passed"):
            build_anki_deck([_make_note()], sheet_name="")

    def test_raises_key_error_for_unknown_sheet(self) -> None:
        """build_anki_deck should raise KeyError for unknown sheet names."""
        with pytest.raises(KeyError):
            build_anki_deck([_make_note()], sheet_name="Unknown Sheet Name")

    def test_successful_build_calls_write_to_file(self) -> None:
        """A valid call should invoke genanki.Package.write_to_file exactly once."""
        with patch("src.deck_builder.genanki.Package") as mock_package_cls:
            mock_package = MagicMock()
            mock_package_cls.return_value = mock_package

            build_anki_deck(
                [_make_note()],
                output_file="test_output.apkg",
                sheet_name="Swedish Vocabulary Master",
            )

            mock_package.write_to_file.assert_called_once_with("test_output.apkg")

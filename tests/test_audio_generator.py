"""Tests for src.audio_generator."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import src.constants as c
from src.audio_generator import _get_client, generate_mp3, get_voice


class TestGetVoice:
    def test_short_text_returns_wavenet(self) -> None:
        """Text shorter than 4 chars should always use a Wavenet voice."""
        voice = get_voice("ab")
        assert voice in c.WAVENET_VOICES

    def test_slash_in_text_returns_wavenet(self) -> None:
        """Text containing '/' should always use a Wavenet voice."""
        voice = get_voice("och/eller")
        assert voice in c.WAVENET_VOICES

    def test_normal_text_returns_swe_voice(self) -> None:
        """Normal text (>= 4 chars, no slash) may return any Swedish voice."""
        voice = get_voice("huset")
        assert voice in c.SWE_VOICES


class TestGenerateMp3:
    def test_skips_when_file_exists(self, tmp_path: Path) -> None:
        """generate_mp3 should not call the TTS API when the file already exists."""
        existing = tmp_path / "se_test.mp3"
        existing.write_bytes(b"fake audio")

        with (
            patch.object(c, "AUDIO_DIR", tmp_path),
            patch("src.audio_generator._get_client") as mock_get_client,
        ):
            generate_mp3("test", "se_test.mp3")
            mock_get_client.assert_not_called()

    def test_calls_api_when_file_missing(self, tmp_path: Path) -> None:
        """generate_mp3 should call synthesize_speech when the file does not exist."""
        mock_client = MagicMock()
        mock_client.synthesize_speech.return_value = MagicMock(audio_content=b"audio")

        with (
            patch.object(c, "AUDIO_DIR", tmp_path),
            patch("src.audio_generator._get_client", return_value=mock_client),
        ):
            generate_mp3("huset", "se_huset.mp3")
            mock_client.synthesize_speech.assert_called_once()
            assert (tmp_path / "se_huset.mp3").exists()


class TestGetClient:
    def test_client_is_cached(self) -> None:
        """_get_client should return the same instance on repeated calls."""
        import src.audio_generator as ag

        original = ag._client
        try:
            mock_client = MagicMock()
            ag._client = mock_client
            assert _get_client() is mock_client
            assert _get_client() is mock_client
        finally:
            ag._client = original

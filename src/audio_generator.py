"""Google Cloud Text-to-Speech client and MP3 generation helpers."""

import random

from google.cloud import texttospeech
from google.oauth2 import service_account

import src.constants as c

__all__ = ["generate_mp3", "get_voice", "process_audio_for_notes"]

_client: texttospeech.TextToSpeechClient | None = None


def _get_client() -> texttospeech.TextToSpeechClient:
    """Return the shared TTS client, initialising it on first call.

    Returns:
        An authenticated :class:`texttospeech.TextToSpeechClient`.
    """
    global _client
    if _client is None:
        credentials = service_account.Credentials.from_service_account_file(
            str(c.CREDENTIALS_FILE)
        )
        _client = texttospeech.TextToSpeechClient(credentials=credentials)
    return _client


def get_voice(swe_text: str) -> str:
    """Return a Swedish TTS voice name appropriate for *swe_text*.

    Short texts (< 4 characters) and texts containing ``/`` use a Wavenet
    voice because Chirp voices can sound unnatural for very short inputs.

    Args:
        swe_text: The Swedish text that will be synthesised.

    Returns:
        A Google Cloud TTS voice name string.
    """
    if "/" in swe_text or len(swe_text) < 4:
        return random.choice(c.WAVENET_VOICES)
    return random.choice(c.SWE_VOICES)


def generate_mp3(text: str, filename: str) -> None:
    """Synthesise *text* to an MP3 file using Google Cloud TTS.

    Skips generation if the target file already exists in
    :data:`~src.constants.AUDIO_DIR`.

    Args:
        text: Swedish text to synthesise.
        filename: Output filename (basename only; written to ``AUDIO_DIR``).
    """
    output_path = c.AUDIO_DIR / filename
    if output_path.exists():
        print(f"   [Skipping] Already exists: {filename}")
        return

    print(f"   [Generating] {filename}...")

    input_text = texttospeech.SynthesisInput(text=text)
    v_name = get_voice(swe_text=text)
    voice = texttospeech.VoiceSelectionParams(language_code="sv-SE", name=v_name)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=c.SPEAKING_RATE
    )

    response = _get_client().synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    with open(output_path, "wb") as out:
        out.write(response.audio_content)


def process_audio_for_notes(notes: list[dict[str, object]]) -> None:
    """Generate word and sentence audio for every note that is missing files.

    Iterates through *notes* and calls :func:`generate_mp3` for both the word
    and sentence audio.  Existing files are skipped automatically.

    Args:
        notes: List of note dicts as returned by
            :func:`~src.data_loader.get_data_from_google_sheet`.  Each dict
            must contain a ``meta_audio_gen`` key with ``word_text``,
            ``word_file``, ``sent_text``, and ``sent_file`` entries.
    """
    print(f"--- Checking Audio for {len(notes)} notes ---")

    for note in notes:
        meta = note["meta_audio_gen"]

        if meta["word_text"]:
            generate_mp3(str(meta["word_text"]), str(meta["word_file"]))

        if meta["sent_text"]:
            generate_mp3(str(meta["sent_text"]), str(meta["sent_file"]))

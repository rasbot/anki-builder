import os
import random
from google.cloud import texttospeech
from google.oauth2 import service_account
import src.constants as c

# Initialize the client ONCE using your shared credentials
# This works for both Sheets and TTS because they are in the same project/json
credentials = service_account.Credentials.from_service_account_file(
    str(c.CREDENTIALS_FILE)
)
client = texttospeech.TextToSpeechClient(credentials=credentials)


def get_voice(swe_text: str) -> str:
    """Get a voice for swedish TTS based on some conditions.

    Args:
        swe_text (str): Swedish text.

    Returns:
        str: Voice name string.
    """
    if "/" in swe_text or len(swe_text) < 4:
        return random.choice(c.WAVENET_VOICES)
    return random.choice(c.SWE_VOICES)


def generate_mp3(text, filename):
    """
    Generates an MP3 using Google Wavenet (Neural) voices.
    """
    # 1. Safety Check: Don't re-generate if it exists
    output_path = c.AUDIO_DIR / filename
    if output_path.exists():
        print(f"   [Skipping] Already exists: {filename}")
        return

    print(f"   [Generating] {filename}...")

    # 2. Configure the API Request
    input_text = texttospeech.SynthesisInput(text=text)

    # "sv-SE-Wavenet-A" is a high-quality female voice.
    # Try "sv-SE-Wavenet-C" for male.
    # Or, use a random one
    v_name = get_voice(swe_text=text)
    voice = texttospeech.VoiceSelectionParams(language_code="sv-SE", name=v_name)

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=c.SPEAKING_RATE
    )

    # 3. Call the API
    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    # 4. Save the file
    with open(output_path, "wb") as out:
        out.write(response.audio_content)


def process_audio_for_notes(notes):
    """
    Iterates through the list of notes and generates audio for
    BOTH the word and the sentence if they are missing.
    """
    print(f"--- Checking Audio for {len(notes)} notes ---")

    for note in notes:
        meta = note["meta_audio_gen"]

        # 1. Generate the Word Audio
        # Example: "vårt" -> se_vart.mp3
        if meta["word_text"]:
            generate_mp3(meta["word_text"], meta["word_file"])

        # 2. Generate the Sentence Audio (The new feature!)
        # Example: "Det här är vårt hus." -> se_sent_vart.mp3
        if meta["sent_text"]:
            generate_mp3(meta["sent_text"], meta["sent_file"])

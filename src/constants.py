"""Project-wide constants: paths, IDs, voice lists, and audio config."""

from pathlib import Path

# 1. Determine the Project Root
SRC_DIR: Path = Path(__file__).parent
PROJECT_ROOT: Path = SRC_DIR.parent

# 2. Key Directories
CONFIG_DIR: Path = PROJECT_ROOT / "config"
DATA_DIR: Path = PROJECT_ROOT / "data"
AUDIO_DIR: Path = DATA_DIR / "audio"
DECKS_DIR: Path = DATA_DIR / "decks"

# 3. Ensure directories exist
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
DECKS_DIR.mkdir(parents=True, exist_ok=True)

# 4. Files
CREDENTIALS_FILE: Path = CONFIG_DIR / "google_credentials.json"

# 5. Anki Configuration
# Unique ID for the Model (Generated once, keep constant to allow updates)
MODEL_ID: int = 1607392319
# Unique ID for the Decks
DECK_ID_NAME_DICT: dict[str, dict[str, str | int]] = {
    # sheet name passed to main script as key
    "Swedish Vocabulary Master": {
        "deck_name": "Svenska: Vocab & Sentences",
        "deck_id": 2059400110,
    },
    "1000 Most Common Swedish Words": {
        "deck_name": "Svenska: 1000 Most Common Words",
        "deck_id": 2059400111,
    },
}

# 6. Audio hash lengths for filename generation
SENT_HASH_LENGTH: int = 6
GUID_HASH_LENGTH: int = 10

# 7. Robot voice
ROBOT_VOICE: str = "sv-SE-Chirp3-HD-Sulafat"
SPEAKING_RATE: float = 0.9
CHIRP_VOICES: list[str] = [
    "sv-SE-Chirp3-HD-Achernar",
    "sv-SE-Chirp3-HD-Achird",
    "sv-SE-Chirp3-HD-Callirrhoe",
    "sv-SE-Chirp3-HD-Despina",
    "sv-SE-Chirp3-HD-Kore",
    "sv-SE-Chirp3-HD-Laomedeia",
    "sv-SE-Chirp3-HD-Orus",
    "sv-SE-Chirp3-HD-Puck",
    "sv-SE-Chirp3-HD-Sulafat",
    "sv-SE-Chirp3-HD-Zephyr",
]
WAVENET_VOICES: list[str] = [
    "sv-SE-Wavenet-F",
    "sv-SE-Wavenet-G",
]
SWE_VOICES: list[str] = CHIRP_VOICES + WAVENET_VOICES

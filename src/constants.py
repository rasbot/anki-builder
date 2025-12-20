from pathlib import Path

# 1. Determine the Project Root
SRC_DIR = Path(__file__).parent
PROJECT_ROOT = SRC_DIR.parent

# 2. Key Directories
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"  # Explicit data root
AUDIO_DIR = DATA_DIR / "audio"
DECKS_DIR = DATA_DIR / "decks"  # <--- New Directory

# 3. Ensure directories exist
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
DECKS_DIR.mkdir(parents=True, exist_ok=True)  # <--- Auto-create

# 4. Files
CREDENTIALS_FILE = (
    "C:\\prog\\google-service-keys\\sincere-destiny-476600-q6-3844f4db997d.json"
)

# 5. Google Sheets Config
SHEET_NAME = "Swedish Vocabulary Master"

# 6. Anki Configuration
# Unique ID for the Model (Generated once, keep constant to allow updates)
MODEL_ID = 1607392319
# Unique ID for the Deck
DECK_ID = 2059400110
DECK_NAME = "Svenska: Vocab & Sentences"

# 7. Robot voice
ROBOT_VOICE = "sv-SE-Chirp3-HD-Sulafat"
SPEAKING_RATE = 0.9
CHIRP_VOICES = [
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
WAVENET_VOICES = [
    "sv-SE-Wavenet-F",
    "sv-SE-Wavenet-G",
]
SWE_VOICES = CHIRP_VOICES + WAVENET_VOICES

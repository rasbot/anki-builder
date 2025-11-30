from pathlib import Path

# 1. Determine the Project Root
# This file is in src/, so the root is two levels up (parent.parent)
SRC_DIR = Path(__file__).parent
PROJECT_ROOT = SRC_DIR.parent

# 2. Key Directories
CONFIG_DIR = PROJECT_ROOT / "config"
AUDIO_DIR = PROJECT_ROOT / "data" / "audio"

# 3. Ensure directories exist (Optional, but helpful safety check)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# 4. Files
CREDENTIALS_FILE = CONFIG_DIR / "google_credentials.json"

# 5. Google Sheets Config
SHEET_NAME = "Swedish Vocabulary Master"

# 6. Anki Configuration
# Unique ID for the Model (Generated once, keep constant to allow updates)
MODEL_ID = 1607392319
# Unique ID for the Deck
DECK_ID = 2059400110
DECK_NAME = "Svenska: Vocab & Sentences"

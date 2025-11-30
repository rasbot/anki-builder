from src.constants import DECKS_DIR  # <--- Import the new constant
from src.data_loader import get_data_from_google_sheet
from src.audio_generator import process_audio_for_notes
from src.deck_builder import build_anki_deck


def main():
    print("--- Starting Anki Build ---")

    # 1. Fetch Data
    notes = get_data_from_google_sheet()

    if not notes:
        print("No notes found. Exiting.")
        return

    # 2. Generate Assets
    process_audio_for_notes(notes)

    # 3. Build Deck
    # Define the full path for the output file
    output_path = DECKS_DIR / "swedish_vocab_master.apkg"

    # Pass the path object (or convert to str if genanki complains)
    build_anki_deck(notes, output_file=str(output_path))

    print("--- Done! ---")


if __name__ == "__main__":
    main()

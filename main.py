import argparse

from src.audio_generator import process_audio_for_notes
from src.constants import DECKS_DIR  # <--- Import the new constant
from src.data_loader import get_data_from_google_sheet
from src.deck_builder import build_anki_deck


def main(sheet_name: str) -> None:
    """Run the full fetch → audio → build pipeline for a given Google Sheet.

    Args:
        sheet_name: Title of the Google Sheet to source vocabulary from.
    """
    print("--- Starting Anki Build ---")

    # 1. Fetch Data
    notes = get_data_from_google_sheet(sheet_name=sheet_name)

    if not notes:
        print("No notes found. Exiting.")
        return

    # 2. Generate Assets
    process_audio_for_notes(notes)

    # 3. Build Deck
    # Define the full path for the output file
    save_file_name = sheet_name.replace(" ", "_")
    output_path = DECKS_DIR / f"{save_file_name}.apkg"

    # Pass the path object (or convert to str if genanki complains)
    build_anki_deck(notes, output_file=str(output_path), sheet_name=sheet_name)

    print("--- Done! ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sheetname",
        "-sn",
        type=str,
        default="Swedish Vocabulary Master",
        help="The google sheet name (title of the sheet at the top).",
    )
    args = parser.parse_args()
    main(sheet_name=args.sheetname)

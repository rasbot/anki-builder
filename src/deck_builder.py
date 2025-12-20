import genanki
from src.constants import MODEL_ID, DECK_ID, DECK_NAME, AUDIO_DIR

# 1. Define the "Ideal" Layout
# This CSS handles the Red/Blue gender coloring and the layout
CSS = """
.card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; }

/* Main Words */
.se-word { font-size: 36px; font-weight: bold; }
.en-word { font-size: 28px; color: #555; }

/* Gender Coloring */
.se-word.en { color: #2980b9; }  /* Blue for En-words */
.se-word.ett { color: #c0392b; } /* Red for Ett-words */

/* The Context Hint */
.hint { font-size: 18px; color: #888; font-style: italic; margin-top: 10px; }

/* Sentence Formatting */
.sentence-container { margin-top: 30px; padding: 15px; background-color: #f5f5f5; border-radius: 8px; text-align: left; }
.sent-se { font-size: 22px; margin-bottom: 5px; }
.sent-en { font-size: 18px; color: #666; font-style: italic; }

/* Dark Mode Support */
.nightMode .card { background-color: #2f2f31; color: #d7d7d7; }
.nightMode .sentence-container { background-color: #3a3a3c; }
.nightMode .se-word.en { color: #54a0ff; }
.nightMode .se-word.ett { color: #ff6b6b; }
"""

# 2. Define the Card Templates
SWEDISH_MODEL = genanki.Model(
    MODEL_ID,
    "Swedish Advanced Model",
    fields=[
        {"name": "WordSE"},
        {"name": "WordEN"},
        {"name": "ContextHint"},
        {"name": "POS"},
        {"name": "Gender"},
        {"name": "SentenceSE"},
        {"name": "SentenceEN"},
        {"name": "AudioWord"},
        {"name": "AudioSentence"},
    ],
    templates=[
        {
            # 1. RECOGNITION CARD (SE -> EN)
            "name": "Recognition (SE -> EN)",
            "qfmt": """
                {{AudioWord}}
                <br>
                <div class="se-word {{Gender}}">{{WordSE}}</div>
                
                {{#ContextHint}}
                    <div class="hint" style="font-size: 0.8em; color: #888;">
                        {{ContextHint}}
                    </div>
                {{/ContextHint}}
            """,
            "afmt": """
                {{FrontSide}}
                <hr id=answer>
                <div class="en-word">{{WordEN}}</div>
                <br>
                <div class="sentence-container">
                    <div class="sent-se">{{SentenceSE}} {{AudioSentence}}</div>
                    <div class="sent-en">{{SentenceEN}}</div>
                </div>
            """,
        },
        {
            # 2. PRODUCTION CARD (EN -> SE)
            "name": "Production (EN -> SE)",
            "qfmt": '<div class="en-word">{{WordEN}}</div><br>{{#ContextHint}}<div class="hint">({{ContextHint}})</div>{{/ContextHint}}',
            "afmt": """
                {{FrontSide}}
                <hr id=answer>
                <div class="se-word {{Gender}}">{{WordSE}}</div>
                {{AudioWord}}
                <br>
                <div class="sentence-container">
                    <div class="sent-se">{{SentenceSE}} {{AudioSentence}}</div>
                </div>
            """,
        },
    ],
    css=CSS,
)


def build_anki_deck(notes, output_file="swedish_deck.apkg"):
    print(f"--- Building Deck with {len(notes)} notes ---")

    # Create the Deck object
    deck = genanki.Deck(DECK_ID, DECK_NAME)

    media_files = []

    for note_data in notes:
        # 1. Create the Note
        # We assume note_data['fields'] is already sorted correctly from data_loader
        note = genanki.Note(
            model=SWEDISH_MODEL, fields=note_data["fields"], guid=note_data["guid"]
        )
        deck.add_note(note)

        # 2. Collect Audio Paths
        # genanki needs the FULL PATH to the file on disk to include it in the package
        meta = note_data["meta_audio_gen"]

        word_audio_path = AUDIO_DIR / meta["word_file"]
        if word_audio_path.exists():
            media_files.append(str(word_audio_path))

        sent_audio_path = AUDIO_DIR / meta["sent_file"]
        if sent_audio_path.exists():
            media_files.append(str(sent_audio_path))

    # 3. Create the Package
    package = genanki.Package(deck)
    package.media_files = media_files

    print(f"   [Packaging] Including {len(media_files)} audio files...")
    package.write_to_file(output_file)
    print(f"   [Success] Created {output_file}")

# anki-builder

A fully automated pipeline to generate high-quality Swedish Anki decks using Python.

This tool solves the "Ambiguity Problem" in language learning (e.g., distinguishing *our* as *vår* vs. *vårt*) by programmatically separating context hints, grammar, and sentences into a structured Anki Note Type. It treats **Google Sheets** as the source of truth and uses **Google Cloud TTS** to generate neural audio for every word and sentence.

## Features

* **Google Sheets Sync:** Edit your vocabulary on your phone or browser; run the script to sync locally.
* **Smart Audio:** Auto-generates MP3s using Google's Neural Wavenet voices. It checks for existing files to minimize API costs.
* **Dual-Card Generation:**
    * **Recognition (SE -> EN):** Hear the Swedish word and see the Swedish text.
    * **Production (EN -> SE):** See English plus *Context Hints* (e.g., "ett-word"), then type or say the Swedish.
* **Visual Grammar:** Auto-colors Swedish words based on gender (Red for `en`, Blue for `ett`) using custom Anki CSS.
* **AI Enrichment:** Automatically fills missing sentences, gender, and grammar hints using OpenAI.

## Project Structure

    swedish_anki_project/
    ├── config/
    │   ├── google_credentials.json   # GCP Service Account Key (GitIgnored)
    │   └── openai_key.txt            # OpenAI API Key (GitIgnored)
    ├── data/
    │   ├── audio/                    # Generated MP3 files
    │   └── decks/                    # Output .apkg files
    ├── src/
    │   ├── constants.py              # Paths and Configuration
    │   ├── data_loader.py            # Google Sheets logic
    │   ├── audio_generator.py        # Google TTS logic
    │   ├── deck_builder.py           # Genanki / HTML / CSS logic
    │   └── enricher.py               # OpenAI enrichment logic
    ├── main.py                       # Entry point
    └── README.md

## Prerequisites

1.  **Python 3.10+**
2.  **uv** (Python package manager)
3.  **Google Cloud Platform Account** (with Sheets API, Drive API, and Text-to-Speech API enabled)
4.  **OpenAI Account** (optional, required only for auto-generating sentences)

## Setup Guide

### 1. Install Dependencies
Run the following to install required libraries:

    uv add genanki gspread oauth2client google-cloud-texttospeech openai pydantic

### 2. Google Cloud Setup
1.  Create a Project in the Google Cloud Console.
2.  Enable **Google Sheets API**, **Google Drive API**, and **Cloud Text-to-Speech API**.
3.  Create a **Service Account** and download the JSON key.
4.  Rename the key to `google_credentials.json` and place it in the `config/` directory.
5.  Open your Google Sheet and **Share** it with the `client_email` address found inside the JSON file (set as Editor).

### 3. OpenAI Setup (Optional)
1.  Obtain an API Key from the OpenAI platform.
2.  Paste the key directly into a file named `config/openai_key.txt`.

### 4. Google Sheet Structure
Your Google Sheet must have the following headers in Row 1. The order does not matter, and empty columns to the right are ignored.

| Header | Description | Example |
| :--- | :--- | :--- |
| `sw_word` | The Swedish word (Target) | *vårt* |
| `en_definition` | English translation | *our* |
| `pos` | Part of Speech | *adj* |
| `gender` | `en`, `ett`, or `plural` (Cases CSS) | *ett* |
| `context_hint` | Hint shown on English card | *ett-word* |
| `sw_sentence` | Example sentence (SE) | *Det är vårt hus.* |
| `en_sentence` | Example sentence (EN) | *That is our house.* |

## Usage

### Standard Run
To sync data, generate missing audio, and build the deck:

    uv run main.py

The script performs the following operations:
1.  **AI Check:** Scans the sheet for rows with a word but no sentence. Calls OpenAI to fill in missing columns.
2.  **Audio Check:** Scans `data/audio/` and generates MP3s for any missing words or sentences via Google TTS.
3.  **Build:** Packages the data and media into `data/decks/swedish_vocab_master.apkg`.

### Importing to Anki
1.  Open Anki on your desktop.
2.  Select **File** -> **Import**.
3.  Select the `.apkg` file from `data/decks/`.

*Note: Because IDs are hashed based on the Swedish Word + POS, you can re-import updated decks to fix typos or add audio without losing your study progress.*

## Card Design Logic

The generator creates a custom Note Type named "**Swedish Advanced Model**".

* **Gender Coloring:** The CSS references the `gender` field.
    * `en` -> Red Text
    * `ett` -> Blue Text
* **Context Hints:**
    * On **English -> Swedish** cards, if `context_hint` exists (e.g., "(ett-word)"), it appears below the English word to resolve ambiguity.
    * This hint is hidden on **Swedish -> English** cards to prevent spoiling the answer.

## Troubleshooting

* **Audio sounds robotic:** Delete the specific `.mp3` file in `data/audio/` and run the script again. The script will regenerate it.
* **Google Sheets Error:** Ensure the Service Account email is added as an **Editor** to the sheet.
* **"Empty Header" Error:** The script handles empty columns automatically, but ensure Row 1 has valid headers for the data columns.
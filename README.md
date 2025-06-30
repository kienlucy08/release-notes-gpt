# FieldSync Release Notes Generator

A Flask web app to help teams generate, regenerate, and save professional release notes for sprints by transforming plain feature/bug descriptions into formatted summaries using OpenAI.

---

## Features

- Add multiple entries (Features or Bugs) with descriptions.
- Automatically generate readable and structured release notes using GPT.
- Save generated notes to a sprint-named folder under `static/saved_notes`.
- View and download past sprint notes.
- Handles long input by chunking into multiple GPT calls.
- Graceful error messaging if text is too long for a single request.
- Delete saved notes (only removes `.txt` files, and deletes the folder only if empty).

---

## Visual

![image](https://github.com/user-attachments/assets/c1b6742e-71ae-40d2-aac5-08662e2a9937)

---

## Tech Stack

- Python 3.10+
- Flask
- OpenAI API
- HTML/CSS (with animated gradient background)

---

## Project Structure

```bash
FieldSync-ReleaseNotes/
│
├── app.py # Main Flask app
├── generate_release_note.py # GPT generation & chunking logic
├── get_current_features_bugs.py # ClickUp API integration for sprint names
├── .env # Your OpenAI API key (not committed)
│
├── templates/
│ └── index.html # Main page template
│
├── static/
│ ├── styles.css # App styling
│ └── saved_notes/ # Auto-created sprint folders with .txt files
│
├── requirements.txt
└── README.md
```


---

## ⚙️ Setup Instructions

### 1. Clone this Repo & Navigate to it

```bash
git clone https://github.com/kienlucy08/release-notes-gpt.git
cd your_file_path/release-notes-gpt
```

### 2. Create `.env` file with your OpenAI Key, and ClickUp Token

```bash
touch .env
```
```env
OPENAI_API_KEY=YOUR_OPENAI_KEY
CLICK_UP_TOKEN=YOUR_CLICK_UP_TOKEN
```
This file lives in the `.gitignore` so no need to worry when saving a new change.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application!

Either:
```bash
flask run
```

Or:
```bash
python app.py
```

---

## Savging & Regeneration
- Notes are saved to: `static/saved_notes/<Sprint_Name>/release_notes_<timestamp>.txt`
- You can delete all saved .txt files for a sprint. If a folder becomes empty, it gets deleted too.
- Regeneration isn't working currently but will eventually delete old filesa in the sprint and replace with new ones.

---

## Warnings & Notes
- If your list is too long (over OpenAI’s token limit), the system automatically chunks the list and makes multiple API calls.
- You’ll see a message in the UI:
  - ⚠️ Heads up: Your notes were very long, so we split them into multiple chunks to generate properly.

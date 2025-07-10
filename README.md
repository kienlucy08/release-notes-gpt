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

Overall View:
<img width="1543" height="2036" alt="image" src="https://github.com/user-attachments/assets/0dc8151b-80b2-4166-8515-8c433c513b32" />

Task Selection:
<img width="1553" height="1963" alt="image" src="https://github.com/user-attachments/assets/4910d255-8094-4fc3-bad3-a614caa2ff3e" />

Generation View:
<img width="1458" height="1959" alt="image" src="https://github.com/user-attachments/assets/fbea8df6-21ed-4376-8afd-85ee90f7a090" />

Example File View:
<img width="1874" height="1380" alt="image" src="https://github.com/user-attachments/assets/92836271-e5db-4ae6-b974-9b4b90ce5a0f" />

---

## Tech Stack

- Python 3.10+
- Flask
- OpenAI API
- HTML/CSS (with animated gradient background)

---

## Project Structure

```bash
Release-Notes-GPT/
│
├── app.py # Main Flask app
├── generate_notes.py # GPT generation & chunking logic
├── fetch_clickup_folders_tasks.py # ClickUp API integration for sprint names and tasks for FieldSync Software Development Folders
├── .env # Your OpenAI API key (not committed)
│
├── templates/
│ └── index.html # Main page template
│
├── static/
│   ├── css/
│   │   └── styles.css # All styles go here
│   ├── js/
│   │   └── script.js # All frontend JS logic here
│   └── saved_notes/
│       └── <sprint_id>/ # All saved release notes organized by sprint ID   
│           └── notes.txt     
│
├── requirements.txt
├── README.md
└── constants.py
```


---

## Setup Instructions

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

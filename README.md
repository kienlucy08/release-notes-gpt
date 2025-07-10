# FieldSync Release Notes Generator

A Flask web app to help teams generate, regenerate, refine, and save professional release notes for sprints. It uses the OpenAI API to turn plain ClickUp task info or manual entries into polished summaries.

---

## Features

- Pull tasks automatically from ClickUp by sprint.
- Support for both manual and auto task entry.
- Tag tasks as Feature, Bug, Enhancement, DevOps, or a combination of two.
- Automatically generate readable and structured release notes using GPT.
- Save generated notes to a sprint-named folder under `static/saved_notes`.
- View and download past sprint notes.
- Handles large inputs by chunking into multiple GPT calls.
- Graceful error messaging if text is too long for a single request.
- Delete saved notes (only removes `.txt` files, and deletes the folder only if empty).
- Renaming individual notes without reloading the page.

---

## Visual

**Overall View**:
<img width="1543" height="2036" alt="image" src="https://github.com/user-attachments/assets/0dc8151b-80b2-4166-8515-8c433c513b32" />

**Task Selection**:
<img width="1553" height="1963" alt="image" src="https://github.com/user-attachments/assets/4910d255-8094-4fc3-bad3-a614caa2ff3e" />

**Generation View**:
<img width="1458" height="1959" alt="image" src="https://github.com/user-attachments/assets/fbea8df6-21ed-4376-8afd-85ee90f7a090" />

**Saved Notes List**:
<img width="1874" height="1380" alt="image" src="https://github.com/user-attachments/assets/92836271-e5db-4ae6-b974-9b4b90ce5a0f" />

---

## Tech Stack

- Python 3.10+
- Flask
- OpenAI API
- ClickUp API (v2)
- HTML/CSS (with animated gradient background) + JavaScript for frontend interactivity

---

## API Reference
Below is a table of all the used flask routes

| Route                 | Methods | Description                                                                 |
|-----------------------|---------|-----------------------------------------------------------------------------|
| `/`                   | GET/POST| Main page. GET shows form and past notes. POST processes input and generates notes. |
| `/get_tasks`          | GET     | Fetches tasks (and subtasks) for the selected sprint from ClickUp.         |
| `/save`               | POST    | Saves generated release notes to a timestamped file inside a sprint folder.|
| `/delete_entry`       | POST    | Deletes **all** `.txt` notes in a sprint folder and removes the folder if empty. |
| `/delete_single_note` | POST    | Deletes **a single** note file from a sprint folder.                        |
| `/delete_all_notes`   | POST    | Deletes **only `.txt` files** in a sprint folder (keeps other assets).     |
| `/rename_note`        | POST    | Renames a `.txt` note file inside a sprint folder.                         |                                      

---

## Project Structure

```bash
release-notes-gpt/
│
├── app.py # Main Flask app
├── constants.py # Reusable constants (e.g., folder ids, clickup api, openai api)
├── generate_notes.py # GPT generation & chunking logic
├── fetch_clickup_folders_tasks.py # ClickUp API integration for sprint names and tasks for 
│
├── templates/
│ └── index.html # Main page template
│
├── static/
│   ├── css/
│   │   └── styles.css # All styles go here
│   ├── scripts/
│   │   └── script.js # Frontend interactivity (toggle, rename, delete)
│   └── saved_notes/
│       └── <sprint_id>/ # All saved release notes organized by sprint ID   
│           └── <release_notes_name>.txt     
│
├── .env # Your OpenAI API and ClickUp tokens and keys
├── .gitignore
├── requirements.txt
├── setup.py # For packaging
├── pyproject.toml # Python build system
├── README.md
└── dist/ build/ egg-info/ # Generated during packaging
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
- You can rename notes and they will be updated real time.
- To regnerate notes simply delete the notes and generate again for the same sprint.

---

## Deployment
(coming soon)
Will include:
- Environment setup
- Static folder handling
- Reverse proxy guidance
- Security
- Backups
- Versioning

---

## Known Limitations
- If your list is too long (over OpenAI’s token limit), the system automatically chunks the list and makes multiple API calls.
- You’ll see a message in the UI:
  - Heads up: Your notes were very long, so we split them into multiple chunks to generate properly.

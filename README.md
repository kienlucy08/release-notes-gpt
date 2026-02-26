# FieldSync Release Notes Generator

A React + Express web app that helps teams generate, manage, and save professional release notes for sprints. It uses the Anthropic Claude API to turn ClickUp task data or manual entries into polished, structured summaries.

---

## Features

- Pull tasks automatically from ClickUp by sprint
- Support for both manual and auto task entry modes
- Tag tasks as Feature, Bug, Enhancement, DevOps, or a Combination of two
- Generate readable, structured release notes using Anthropic Claude
- Save generated notes to browser localStorage (persists across sessions)
- View, rename, and delete past sprint notes
- Handles large inputs by chunking into multiple API calls (rarely needed with Claude's 200K context)

---

## Tech Stack

- **Frontend**: React 19 (Vite)
- **Backend**: Node.js + Express
- **AI Model**: Anthropic Claude (claude-sonnet-4-20250514)
- **External API**: ClickUp API v2
- **Storage**: Browser localStorage

---

## Project Structure

```
release-notes-gpt/
├── client/                              # React frontend (Vite)
│   ├── index.html                       # HTML entry point
│   ├── package.json                     # Client dependencies
│   ├── vite.config.js                   # Vite config with API proxy
│   └── src/
│       ├── main.jsx                     # React entry point
│       ├── App.jsx                      # Root component (state management)
│       ├── App.css                      # All styles (animated gradient, indigo theme)
│       ├── api/
│       │   └── apiClient.js             # Fetch wrapper for /api calls
│       ├── components/
│       │   ├── SprintSelector.jsx       # Sprint dropdown
│       │   ├── EntryModeToggle.jsx      # Manual / Auto radio toggle
│       │   ├── TagSelect.jsx            # Tag dropdown (with Combination sub-selects)
│       │   ├── ManualEntryForm.jsx      # Manual tag + description entry rows
│       │   ├── AutoTaskSelect.jsx       # Auto task checklist + extra manual rows
│       │   ├── FileNameInput.jsx        # Custom filename input
│       │   ├── GenerateButton.jsx       # Submit button with loading state
│       │   ├── CurrentItems.jsx         # Displays submitted entries
│       │   ├── GeneratedNotes.jsx       # Output display with chunked warning
│       │   └── PastSprintNotes.jsx      # Saved notes list (view/rename/delete)
│       └── utils/
│           └── storage.js               # localStorage CRUD for saved notes
│
├── server/                              # Express API backend
│   ├── package.json                     # Server dependencies
│   ├── index.js                         # Express entry (CORS, JSON, route mounting)
│   ├── config/
│   │   └── constants.js                 # ClickUp IDs, sprint mappings, system prompt, token limits
│   ├── routes/
│   │   ├── clickup.js                   # GET /api/sprints, GET /api/tasks
│   │   └── generate.js                  # POST /api/generate
│   └── services/
│       ├── anthropic.js                 # Claude API calls (generation + chunking)
│       └── clickup.js                   # ClickUp API integration
│
├── .env.example                         # Template for environment variables
├── .gitignore
└── README.md
```

---

## API Endpoints

| Route | Method | Description |
|---|---|---|
| `/api/sprints` | GET | Returns list of sprints from ClickUp `[{id, name}]` |
| `/api/tasks?sprint_id=X` | GET | Returns tasks for a sprint with tags and descriptions |
| `/api/generate` | POST | Accepts `{entries[], sprintName}`, returns `{notes, wasChunked}` |

Note management (save, rename, delete) is handled entirely client-side via localStorage.

---

## Setup Instructions

### Prerequisites

- [Node.js](https://nodejs.org/) v18 or higher
- An [Anthropic API key](https://console.anthropic.com/)
- A [ClickUp API token](https://clickup.com/api)

### 1. Clone the Repo

```bash
git clone https://github.com/kienlucy08/release-notes-gpt.git
cd release-notes-gpt
```

### 2. Create the Server `.env` File

Create a file called `.env` inside the `server/` directory:

```env
ANTHROPIC_API_KEY=your-anthropic-api-key-here
CLICK_UP_TOKEN=your-clickup-token-here
```

This file is in `.gitignore` so your keys will not be committed.

### 3. Install Dependencies

Install both server and client dependencies:

```bash
cd server
npm install

cd ../client
npm install
```

### 4. Start the Application

You need **two terminals** running at the same time:

**Terminal 1 - Start the Express API server:**

```bash
cd server
npm run dev
```

The API server runs on `http://localhost:3001`.

**Terminal 2 - Start the React dev server:**

```bash
cd client
npm run dev
```

The React app runs on `http://localhost:5173`.

### 5. Open the App

Open your browser and go to:

```
http://localhost:5173
```

The Vite dev server automatically proxies all `/api` requests to the Express server, so everything works together seamlessly.

---

## How to Use

### Manual Entry Mode (default)

1. Select a sprint from the dropdown
2. Choose a tag type (Feature, Bug, Enhancement, DevOps, or Combination)
3. Enter a description of the work item
4. Click **Add Another** to add more entries
5. Optionally enter a custom filename
6. Click **Generate Release Notes**

### Auto Entry Mode (from ClickUp)

1. Select a sprint from the dropdown
2. Switch to **Auto from Sprint** mode
3. Tasks are automatically loaded from ClickUp with checkboxes
4. Check/uncheck tasks to include or exclude them
5. Optionally add extra manual entries below the task list
6. Click **Generate Release Notes**

### Managing Saved Notes

- Notes are automatically saved to your browser's localStorage after generation
- View past notes in the **Past Sprint Notes** section at the bottom
- Click a filename to expand and view its content
- Click **Edit** to rename a note
- Click **Delete** to remove a single note
- Click **Delete Notes** to remove all notes for a sprint

---

## Saving & Storage

- Notes are stored in your browser's `localStorage` under the key `releaseNotes`
- Data persists across browser sessions but is specific to the browser/device
- There is no server-side file storage; all persistence is client-side
- To export a note, you can copy the text from the view panel

---

## Environment Variables

| Variable | Location | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | `server/.env` | Your Anthropic API key for Claude |
| `CLICK_UP_TOKEN` | `server/.env` | Your ClickUp personal API token |
| `PORT` | `server/.env` (optional) | Express server port (default: 3001) |
| `CORS_ORIGIN` | `server/.env` (optional) | Allowed CORS origin (default: `http://localhost:5173`) |

---

## Production Build

To build the React app for production:

```bash
cd client
npm run build
```

This creates a `dist/` folder with optimized static files. The Express server is configured to serve these in production mode:

```bash
cd server
NODE_ENV=production node index.js
```

In production, the Express server serves both the API and the React app from a single port.

---

## Known Limitations

- If your input is extremely large (1,000+ tasks), the system will chunk it into multiple Claude API calls. You will see a warning banner in the UI. This is rare since Claude supports a 200K token context window.
- localStorage has a ~5-10MB limit per browser origin. This is more than enough for typical use (hundreds of saved notes), but very heavy usage could eventually hit this limit.
- Saved notes are browser-specific. Clearing browser data will remove saved notes.
- The ClickUp sprint mappings in `server/config/constants.js` include Sprints 1-22. To add new sprints, update the `FIELD_ID_TO_SPRINT` mapping in that file.

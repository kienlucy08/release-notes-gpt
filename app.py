# app.py
import os
from datetime import datetime
from flask import jsonify
from flask import Flask, render_template, request, redirect, url_for
from generate_release_note import generate_release_notes_chunked
from get_current_features_bugs import get_sprint_lists, get_all_tasks_associated_with_sprints, get_tasks_for_sprint_id

NOTES_BASE_DIR = "static/saved_notes"
FOLDER_ID = "90115096402"

app = Flask(__name__)

"""

Helper functions

"""

def save_release_notes(content, sprint_name, filename):
    """
    Saves release note content to a .txt file in a sprint-named folder.

    Args:
        content (str): Text content of the release note.
        sprint_name (str): Sprint used for naming the folder.
        filename (str): Sanitized filename to use.

    Returns:
        str: Relative path to the saved file.
    """
    folder_name = sprint_name.replace(" ", "_").replace("/", "-")
    folder_path = os.path.join(NOTES_BASE_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    full_path = os.path.join(folder_path, filename)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"{folder_name}/{filename}"


def get_saved_sprint_notes(sprint_options):
    """
    Retrieves saved .txt files for each sprint folder.

    Args:
        sprint_options (list): List of sprints with id/name from ClickUp.

    Returns:
        list[dict]: Sprint folder metadata with files.
    """
    sprint_folders = []
    if os.path.exists(NOTES_BASE_DIR):
        for sprint_folder in os.listdir(NOTES_BASE_DIR):
            path = os.path.join(NOTES_BASE_DIR, sprint_folder)
            if os.path.isdir(path):
                name = next((s["name"] for s in sprint_options if s["id"] == sprint_folder), sprint_folder)
                files = sorted(os.listdir(path), reverse=True)
                sprint_folders.append({
                    "name": name,
                    "folder": sprint_folder,
                    "files": sorted(files, reverse=True)
                })
    return sprint_folders

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main route for loading or submitting release notes.

    - GET: Loads page with past notes
    - POST: Generates release notes from form input and optionally saves
    """
    results = None
    entries = []
    saved_file_path = None
    was_chunked = False
    all_sprint_tasks = []

    # Get sprint options from ClickUp
    all_lists = get_sprint_lists(FOLDER_ID)
    sprint_options = [{"id": sprint["id"], "name": sprint["name"]}
                      for sprint in all_lists if "Sprint" in sprint["name"]]
    sprint_name =request.form.get("sprint")

    if request.method == "POST":
        types = request.form.getlist("type")
        descriptions = request.form.getlist("description")
        entries = [f"{t}: {d.strip()}" for t, d in zip(types, descriptions) if d.strip()]

        if entries and sprint_name:
            results, was_chunked = generate_release_notes_chunked(entries)
            # Fetch all sprint tasks once
            all_sprint_tasks = get_tasks_for_sprint_id(FOLDER_ID, sprint_name)
            # Determine file name
            custom_filename = request.form.get("custom_filename", "").strip()
            if custom_filename:
                # Sanitize input to avoid special characters or path issues
                safe_filename = "".join(c for c in custom_filename if c.isalnum() or c in ('_', '-')).rstrip()
                filename = f"{safe_filename}.txt"
            else:
                filename = f"release_notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            # Save note to file
            saved_file_path = save_release_notes(results, sprint_name, filename)

    saved_notes = get_saved_sprint_notes(sprint_options)

    return render_template(
        "index.html",
        entries=entries,
        results=results,
        was_chunked=was_chunked,
        sprints=sprint_options,
        saved_file_path=f"saved_notes/{saved_file_path}" if saved_file_path else None,
        saved_notes=saved_notes,
        sprint_name=sprint_name,
        sprint_tasks=all_sprint_tasks,
        show_save_option=False
    )

@app.route("/get_tasks", methods=["GET"])
def get_tasks():
    sprint_id = request.args.get("sprint_id")
    if not sprint_id:
        return jsonify([])

    tasks = get_tasks_for_sprint_id(FOLDER_ID, sprint_id)
    return jsonify([{"id": t["id"], "name": t["name"]} for t in tasks])


@app.route("/save", methods=["POST"])
def save_note():
    """Save a note after generation using fallback if needed"""
    content = request.form.get("results")
    sprint_name = request.form.get("sprint_name")
    if not content or not sprint_name:
        return redirect(url_for("index"))
    
    filename = f"release_notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = save_release_notes(content, sprint_name, filename)

    sprint_options = [{"id": l["id"], "name": l["name"]} for l in get_sprint_lists(FOLDER_ID) if "Sprint" in l["name"]]
    saved_notes = get_saved_sprint_notes(sprint_options)

    return render_template(
        "index.html",
        entries=[line.strip()
                    for line in content.splitlines() if line.strip()],
        results=content,
        sprints=sprint_options,
        saved_notes=saved_notes,
        sprint_name=sprint_name,
        saved_file_path=f"saved_notes/{path}",
        show_save_option=False
    )

@app.route("/delete_entry", methods=["POST"])
def delete_entry():
    """Delete an added entry"""
    sprint_name = request.form.get("sprint_name")
    if not sprint_name:
        return "Sprint name missing", 400

    sprint_id = next((s["id"] for s in get_sprint_lists(FOLDER_ID) if s["name"] == sprint_name), None)
    folder_name = sprint_id or sprint_name.replace(" ", "_").replace("/", "-")
    folder_path = os.path.join(NOTES_BASE_DIR, folder_name)

    try:
        if os.path.exists(folder_path):
            files = sorted(os.listdir(folder_path), reverse=True)
            for file in files:
                os.remove(os.path.join(folder_path, file))
            os.rmdir(folder_path)
        return redirect(url_for("index"))
    except Exception as e:
        return f"Error deleting note: {e}", 500

@app.route('/delete_single_note', methods=['POST'])
def delete_single_note():
    """Delete a single note file inside a sprint folder."""
    sprint_folder = request.form['sprint_folder']
    file_name = request.form['file_name']
    file_path = os.path.join(NOTES_BASE_DIR, sprint_folder, file_name)

    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('index'))  # or wherever your main view function is

@app.route("/delete_all_notes", methods=["POST"])
def delete_all_notes():
    """Deletes all notes within a sprint folder, preserving other assets"""
    sprint_folder = request.form.get("sprint_folder")
    folder_path = os.path.join(NOTES_BASE_DIR, sprint_folder)

    try:
        if os.path.exists(folder_path):
            # Delete sprint folder and all files in it
            for file in os.listdir(folder_path):
                if file.endswith(".txt"):
                    os.remove(os.path.join(folder_path, file))

            # If folder is empty after deletion, remove it
            if not os.listdir(folder_path):
                os.rmdir(folder_path)

        return redirect(url_for("index"))
    except Exception as e:
        return f"Error deleting release notes: {e}", 500


if __name__ == "__main__":
    app.run(debug=True)

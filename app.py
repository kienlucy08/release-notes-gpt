# app.py
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from generate_release_note import generate_release_notes_chunked
from get_current_features_bugs import get_lists_from_folder

NOTES_BASE_DIR = "static/saved_notes"
FOLDER_ID = "90115096402"

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_APP")


def save_release_notes(content, sprint_name):
    # Force folder name to always use the readable sprint name
    folder_name = sprint_name.replace(" ", "_").replace("/", "-")
    folder_path = os.path.join(NOTES_BASE_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    filename = f"release_notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    full_path = os.path.join(folder_path, filename)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

    return folder_name, filename


def get_saved_sprint_notes(sprint_options):
    sprint_folders = []
    if os.path.exists(NOTES_BASE_DIR):
        for sprint_folder in os.listdir(NOTES_BASE_DIR):
            path = os.path.join(NOTES_BASE_DIR, sprint_folder)
            if os.path.isdir(path):
                matching_sprint = next((s["name"] for s in sprint_options if s["id"] == sprint_folder), sprint_folder)
                files = os.listdir(path)
                sprint_folders.append({
                    "name": matching_sprint,
                    "folder": sprint_folder,
                    "files": sorted(files, reverse=True)
                })
    return sprint_folders


@app.route("/save", methods=["POST"])
def save_note():
    content = request.form.get("results")
    sprint_name = request.form.get("sprint_name")

    if content and sprint_name:
        folder_name, filename = save_release_notes(content, sprint_name)

        all_lists = get_lists_from_folder(FOLDER_ID)
        sprint_options = [{"id": l["id"], "name": l["name"]}
                          for l in all_lists if "Sprint" in l["name"]]
        saved_notes = get_saved_sprint_notes(sprint_options)
        return render_template(
            "index.html",
            entries=[line.strip()
                     for line in content.splitlines() if line.strip()],
            results=content,
            sprints=sprint_options,
            saved_notes=saved_notes,
            sprint_name=sprint_name,
            saved_file_path=f"saved_notes/{folder_name}/{filename}",
            show_save_option=False
        )
    return redirect(url_for("index"))

@app.route("/delete", methods=["POST"])
def delete_note():
    sprint_name = request.form.get("sprint_name")
    if not sprint_name:
        return "Sprint name missing", 400  # Or redirect with flash message

    sprint_id = next((s["id"] for s in get_lists_from_folder(FOLDER_ID) if s["name"] == sprint_name), None)
    folder_name = sprint_id or sprint_name.replace(" ", "_").replace("/", "-")
    folder_path = os.path.join(NOTES_BASE_DIR, folder_name)

    try:
        if os.path.exists(folder_path):
            # Optional: Only delete the latest file instead of whole folder
            files = sorted(os.listdir(folder_path), reverse=True)
            for file in files:
                os.remove(os.path.join(folder_path, file))
            os.rmdir(folder_path)
        return redirect(url_for("index"))
    except Exception as e:
        return f"Error deleting note: {e}", 500

@app.route("/delete_txts", methods=["POST"])
def delete_txt_files_only():
    sprint_folder = request.form.get("sprint_folder")
    folder_path = os.path.join(NOTES_BASE_DIR, sprint_folder)

    try:
        if os.path.exists(folder_path):
            # Delete only .txt files
            for file in os.listdir(folder_path):
                if file.endswith(".txt"):
                    os.remove(os.path.join(folder_path, file))

            # If folder is empty after deletion, remove it
            if not os.listdir(folder_path):
                os.rmdir(folder_path)

        return redirect(url_for("index"))
    except Exception as e:
        return f"Error deleting release notes: {e}", 500


@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    entries = []
    was_chunked = False
    saved_file_path = None
    show_save_option = False

    all_lists = get_lists_from_folder(FOLDER_ID)
    sprint_options = [{"id": sprint["id"], "name": sprint["name"]}
                      for sprint in all_lists if "Sprint" in sprint["name"]]

    sprint_name =request.form.get("sprint")

    if request.method == "POST":
        types = request.form.getlist("type")
        descriptions = request.form.getlist("description")
        sprint_name = request.form.get("sprint")

        # ✅ Only now try to get the sprint_id
        sprint_id = next((s["id"] for s in sprint_options if s["name"] == sprint_name), None)

        entries = [f"{t}: {d.strip()}" for t, d in zip(types, descriptions) if d.strip()]
        if entries:
            results, was_chunked = generate_release_notes_chunked(entries)
            if sprint_name:
                folder_name = sprint_id or sprint_name.replace(" ", "_").replace("/", "-")
                folder_path = os.path.join(NOTES_BASE_DIR, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                filename = f"release_notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                full_path = os.path.join(folder_path, filename)

                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(results)

                saved_file_path = f"saved_notes/{folder_name}/{filename}"

    saved_notes = get_saved_sprint_notes(sprint_options)

    return render_template(
        "index.html",
        entries=entries,
        results=results,
        was_chunked=was_chunked,
        sprints=sprint_options,
        saved_file_path=saved_file_path,
        saved_notes=saved_notes,
        sprint_name=sprint_name,
        show_save_option=show_save_option
    )



if __name__ == "__main__":
    app.run(debug=True)

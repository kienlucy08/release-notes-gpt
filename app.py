# app.py
from flask import Flask, render_template, request
from generate_release_note import generate_release_notes

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    entries = []
    if request.method == "POST":
        types = request.form.getlist("type")
        descriptions = request.form.getlist("description")
        entries = [f"{t}: {d.strip()}" for t, d in zip(types, descriptions) if d.strip()]
        if entries:
            results = generate_release_notes(entries)
    return render_template("index.html", entries=entries, results=results)

if __name__ == "__main__":
    app.run(debug=True)

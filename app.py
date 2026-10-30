from datetime import date, datetime
from pathlib import Path
import sqlite3
import os

from flask import Flask, abort, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "local-development-key-change-before-deploying")
BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "tracker.db"
STATUSES = ["Wishlist", "Applied", "Assessment", "Interview", "Offer", "Rejected"]


def connect_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_db():
    with connect_db() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Wishlist',
            deadline TEXT,
            applied_on TEXT,
            job_url TEXT,
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        count = db.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        if count == 0:
            db.executemany(
                "INSERT INTO applications (company, role, status, deadline, notes) VALUES (?, ?, ?, ?, ?)",
                [
                    ("Example Tech", "Python Intern", "Wishlist", "2026-11-15", "Replace this example with a real opportunity."),
                    ("Sample Systems", "Graduate Engineer Trainee", "Applied", "2026-11-05", "Prepare SQL and basic programming questions."),
                ],
            )


def get_application(application_id):
    with connect_db() as db:
        row = db.execute("SELECT * FROM applications WHERE id = ?", (application_id,)).fetchone()
    if row is None:
        abort(404)
    return row


@app.route("/")
def index():
    status_filter = request.args.get("status", "")
    query = request.args.get("q", "").strip()
    conditions, values = [], []
    if status_filter in STATUSES:
        conditions.append("status = ?")
        values.append(status_filter)
    if query:
        conditions.append("(company LIKE ? OR role LIKE ?)")
        values.extend([f"%{query}%", f"%{query}%"])
    where = (" WHERE " + " AND ".join(conditions)) if conditions else ""
    with connect_db() as db:
        applications = db.execute(
            f"SELECT * FROM applications{where} ORDER BY CASE WHEN deadline IS NULL OR deadline = '' THEN 1 ELSE 0 END, deadline, created_at DESC",
            values,
        ).fetchall()
        total = db.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        offers = db.execute("SELECT COUNT(*) FROM applications WHERE status = 'Offer'").fetchone()[0]
        interviews = db.execute("SELECT COUNT(*) FROM applications WHERE status = 'Interview'").fetchone()[0]
        active = db.execute("SELECT COUNT(*) FROM applications WHERE status IN ('Applied', 'Assessment', 'Interview')").fetchone()[0]
    today = date.today().isoformat()
    return render_template("index.html", applications=applications, statuses=STATUSES,
                           status_filter=status_filter, query=query, total=total, offers=offers,
                           interviews=interviews, active=active, today=today)


def read_form():
    company = request.form.get("company", "").strip()
    role = request.form.get("role", "").strip()
    status = request.form.get("status", "Wishlist")
    if not company or not role:
        raise ValueError("Company and role are required.")
    if status not in STATUSES:
        raise ValueError("Choose a valid application status.")
    deadline = request.form.get("deadline", "").strip()
    applied_on = request.form.get("applied_on", "").strip()
    for field in (deadline, applied_on):
        if field:
            datetime.strptime(field, "%Y-%m-%d")
    job_url = request.form.get("job_url", "").strip()
    if job_url and not job_url.startswith(("https://", "http://")):
        raise ValueError("Job link must start with http:// or https://.")
    notes = request.form.get("notes", "").strip()
    return (company, role, status, deadline, applied_on, job_url, notes)


@app.route("/add", methods=["POST"])
def add_application():
    try:
        values = read_form()
    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for("index"))
    with connect_db() as db:
        db.execute("INSERT INTO applications (company, role, status, deadline, applied_on, job_url, notes) VALUES (?, ?, ?, ?, ?, ?, ?)", values)
    flash("Application added.", "success")
    return redirect(url_for("index"))


@app.route("/edit/<int:application_id>", methods=["GET", "POST"])
def edit_application(application_id):
    application = get_application(application_id)
    if request.method == "POST":
        try:
            values = read_form()
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("edit_application", application_id=application_id))
        with connect_db() as db:
            db.execute("UPDATE applications SET company=?, role=?, status=?, deadline=?, applied_on=?, job_url=?, notes=? WHERE id=?", (*values, application_id))
        flash("Application updated.", "success")
        return redirect(url_for("index"))
    return render_template("form.html", application=application, statuses=STATUSES)


@app.route("/delete/<int:application_id>", methods=["POST"])
def delete_application(application_id):
    get_application(application_id)
    with connect_db() as db:
        db.execute("DELETE FROM applications WHERE id = ?", (application_id,))
    flash("Application deleted.", "success")
    return redirect(url_for("index"))


initialize_db()

if __name__ == "__main__":
    app.run(debug=True)

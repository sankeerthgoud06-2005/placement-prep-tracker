# Placement Prep Tracker

A small Flask and SQLite web app for tracking job opportunities, application stages, deadlines, and interview notes. It runs locally and needs no external service or API key.

## Features

- Dashboard counts for tracked roles, active applications, interviews, and offers
- Add, edit, and delete opportunities
- Track company, role, status, deadline, applied date, job link, and notes
- Search by company or role and filter by status
- Highlights missed deadlines
- SQLite database is created automatically with two clearly marked example entries
- Responsive layout for desktop and mobile

## Requirements

- Python 3.10 or newer
- Internet only for the optional Google Fonts styling; the app itself works offline

## Run on Windows

Open Command Prompt or the VS Code terminal in this project folder, then run:

```bat
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py app.py
```

Open **http://127.0.0.1:5000** in your browser. Stop the server with `Ctrl+C`.

## Run on macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000**.

## Database and sample data

The app creates `tracker.db` in the project folder on first run and inserts two example opportunities. Replace or delete those entries through the app. The database is excluded from Git by `.gitignore`, so personal application details will not be pushed by accident.

## Upload to GitHub

1. Create a new empty repository on GitHub, for example `placement-prep-tracker`.
2. Open this project folder in VS Code.
3. In the terminal, run:

```bash
git init
git add .
git commit -m "Build placement prep tracker"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/placement-prep-tracker.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. Do not upload `.venv` or `tracker.db`.

## Project structure

```text
placement-prep-tracker/
├── app.py                 # Flask routes and SQLite database
├── requirements.txt       # Python dependency
├── README.md              # Setup and GitHub instructions
├── .gitignore
├── .env.example
├── templates/
│   ├── index.html          # Dashboard and add form
│   └── form.html          # Edit application page
└── static/
    └── style.css          # Responsive styling
```

## Notes

This is a local portfolio project. Before deploying it publicly, set a strong `FLASK_SECRET_KEY` environment variable, add CSRF protection, and use a production WSGI server. The built-in Flask development server is intended for local use.

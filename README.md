# Study Revision Planner

A compact Flask app that creates spaced-repetition revision schedules from topics and an exam date. Built as a lightweight tool for students to plan study sessions using simple forgetting-curve intervals.

## Features

- Generate per-topic revision sessions using difficulty-based intervals (easy/medium/hard).
- Dashboard: today's tasks, overdue alerts, upcoming timeline, and per-subject progress.
- Mark sessions done (persisted to JSON) with immediate UI feedback.
- Export the full schedule as CSV for external use.

## Tech stack

- Python 3.10+ and Flask (see `requirements.txt`)
- Server-rendered HTML (Jinja2), CSS and a small JavaScript helper
- Storage: JSON file at `data/study_data.json`

## Quick start (development)

1. Create a virtual env and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the dev server (default port: 5001):

```bash
python app.py
# open http://127.0.0.1:5001
```

## Usage

- Open the app in your browser.
- Fill the form: `Subject name`, `Exam date`, and one topic per line in the format `Topic name | difficulty` (difficulty: `easy`, `medium`, or `hard`).
- Click **Generate schedule** to persist the subject and build review sessions.
- Use **Mark done** to record completion; export with **Export CSV**.

## Tests

Unit tests check the scheduler logic and exam-boundary edge cases.

Run all tests:

```bash
python -m unittest discover -v
```

Files with tests:

- `tests/test_scheduler.py`
- `tests/test_scheduler_edges.py`

## Project layout

- `app.py` - Flask app, scheduling functions, and routes (index, add subject, toggle/reset session, export CSV)
- `templates/index.html` - dashboard and form
- `static/styles.css`, `static/app.js` - UI and small client helpers
- `data/study_data.json` - persisted data (empty by default)
- `tests/` - unit tests

## Deployment notes

This repo uses the Flask development server for simplicity. For production:

1. Use a WSGI server such as `gunicorn` or `uWSGI`.
2. Persist data using a real datastore (SQLite/Postgres) or ensure `data/` is stored on a volume.
3. Ensure the app uses production data storage before publishing.

Example production run (quick):

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Repository**: https://github.com/Cletrix-Labs/study-revision-planner  
**Live Demo**: https://reviseo.onrender.com

Built for quick ⭐ , organized revision planning.
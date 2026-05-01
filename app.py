from __future__ import annotations

import csv
import json
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

from flask import Flask, redirect, render_template, request, send_file, url_for


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "study_data.json"


app = Flask(__name__)


DIFFICULTY_INTERVALS = {
    "easy": [1, 7, 21, 45],
    "medium": [1, 4, 10, 25],
    "hard": [1, 2, 5, 12, 25],
}


def ensure_storage() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps({"subjects": []}, indent=2), encoding="utf-8")


def load_data() -> dict:
    ensure_storage()
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"subjects": []}


def save_data(data: dict) -> None:
    ensure_storage()
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def today() -> date:
    return date.today()


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def parse_topics(raw_topics: str) -> list[dict]:
    topics: list[dict] = []
    for line in raw_topics.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue

        separator = "|" if "|" in cleaned else "," if "," in cleaned else None
        if separator:
            name_part, difficulty_part = [part.strip() for part in cleaned.split(separator, 1)]
        else:
            name_part, difficulty_part = cleaned, "medium"

        difficulty = difficulty_part.lower()
        if difficulty not in DIFFICULTY_INTERVALS:
            difficulty = "medium"

        topics.append(
            {
                "id": f"topic_{uuid.uuid4().hex[:8]}",
                "name": name_part,
                "difficulty": difficulty,
            }
        )
    return topics


def build_review_sessions(start_date: date, exam_date: date, difficulty: str) -> list[dict]:
    sessions = []
    for day_offset in DIFFICULTY_INTERVALS[difficulty]:
        review_date = start_date + timedelta(days=day_offset - 1)
        if review_date > exam_date:
            break
        sessions.append(
            {
                "id": f"session_{uuid.uuid4().hex[:8]}",
                "date": review_date.isoformat(),
                "label": f"Day {day_offset}",
                "completed": False,
            }
        )
    return sessions


def build_subject(name: str, exam_date: date, topics: list[dict]) -> dict:
    start_date = today()
    topic_payloads = []
    for topic in topics:
        sessions = build_review_sessions(start_date, exam_date, topic["difficulty"])
        topic_payloads.append(
            {
                **topic,
                "review_dates": [session["date"] for session in sessions],
                "sessions": sessions,
            }
        )

    return {
        "id": f"subject_{uuid.uuid4().hex[:8]}",
        "name": name,
        "exam_date": exam_date.isoformat(),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "topics": topic_payloads,
    }


def flatten_sessions(subjects: list[dict]) -> list[dict]:
    sessions = []
    current_day = today()

    for subject in subjects:
        exam_date = parse_date(subject["exam_date"])
        for topic in subject.get("topics", []):
            for session in topic.get("sessions", []):
                session_date = parse_date(session["date"])
                sessions.append(
                    {
                        "subject_id": subject["id"],
                        "subject_name": subject["name"],
                        "topic_id": topic["id"],
                        "topic_name": topic["name"],
                        "difficulty": topic["difficulty"],
                        "exam_date": exam_date.isoformat(),
                        "session_id": session["id"],
                        "date": session_date.isoformat(),
                        "label": session["label"],
                        "completed": bool(session.get("completed")),
                        "overdue": session_date < current_day and not session.get("completed"),
                        "due_today": session_date == current_day and not session.get("completed"),
                    }
                )

    sessions.sort(key=lambda item: (item["date"], item["subject_name"], item["topic_name"], item["label"]))
    return sessions


def enrich_subjects(subjects: list[dict]) -> list[dict]:
    enriched = []
    for subject in subjects:
        sessions = flatten_sessions([subject])
        completed = sum(1 for item in sessions if item["completed"])
        total = len(sessions)
        progress = round((completed / total) * 100, 1) if total else 0.0
        today_count = sum(1 for item in sessions if item["due_today"])
        overdue_count = sum(1 for item in sessions if item["overdue"])

        enriched.append(
            {
                **subject,
                "progress": progress,
                "completed_sessions": completed,
                "total_sessions": total,
                "today_count": today_count,
                "overdue_count": overdue_count,
                "topics": [
                    {
                        **topic,
                        "completed_sessions": sum(1 for session in topic.get("sessions", []) if session.get("completed")),
                        "total_sessions": len(topic.get("sessions", [])),
                    }
                    for topic in subject.get("topics", [])
                ],
            }
        )

    return enriched


def update_session_completion(data: dict, session_id: str, completed: bool) -> bool:
    for subject in data.get("subjects", []):
        for topic in subject.get("topics", []):
            for session in topic.get("sessions", []):
                if session["id"] == session_id:
                    session["completed"] = completed
                    return True
    return False


@app.route("/")
def index():
    data = load_data()
    subjects = enrich_subjects(data.get("subjects", []))
    all_sessions = flatten_sessions(data.get("subjects", []))
    today_sessions = [session for session in all_sessions if session["due_today"]]
    overdue_sessions = [session for session in all_sessions if session["overdue"]]
    upcoming_sessions = [session for session in all_sessions if not session["completed"] and session["date"] > today().isoformat()][:8]

    return render_template(
        "index.html",
        subjects=subjects,
        today_sessions=today_sessions,
        overdue_sessions=overdue_sessions,
        upcoming_sessions=upcoming_sessions,
    )


@app.post("/subjects")
def add_subject():
    subject_name = request.form.get("subject_name", "").strip()
    exam_date_raw = request.form.get("exam_date", "").strip()
    topics_raw = request.form.get("topics", "").strip()

    if not subject_name or not exam_date_raw or not topics_raw:
        return redirect(url_for("index"))

    exam_date = parse_date(exam_date_raw)
    topics = parse_topics(topics_raw)
    if not topics:
        return redirect(url_for("index"))

    data = load_data()
    data.setdefault("subjects", []).append(build_subject(subject_name, exam_date, topics))
    save_data(data)
    return redirect(url_for("index"))


@app.post("/sessions/<session_id>/toggle")
def toggle_session(session_id: str):
    data = load_data()
    if update_session_completion(data, session_id, True):
        save_data(data)
    return redirect(url_for("index"))


@app.post("/sessions/<session_id>/reset")
def reset_session(session_id: str):
    data = load_data()
    if update_session_completion(data, session_id, False):
        save_data(data)
    return redirect(url_for("index"))


@app.get("/export.csv")
def export_csv():
    data = load_data()
    sessions = flatten_sessions(data.get("subjects", []))
    csv_path = DATA_DIR / "revision_schedule.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["subject", "topic", "difficulty", "date", "label", "completed", "overdue"])
        for session in sessions:
            writer.writerow(
                [
                    session["subject_name"],
                    session["topic_name"],
                    session["difficulty"],
                    session["date"],
                    session["label"],
                    "yes" if session["completed"] else "no",
                    "yes" if session["overdue"] else "no",
                ]
            )

    return send_file(csv_path, as_attachment=True, download_name="revision_schedule.csv")


if __name__ == "__main__":
    ensure_storage()
    app.run(debug=True, port=5001)
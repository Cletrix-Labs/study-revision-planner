import unittest
from datetime import date, timedelta

from app import build_review_sessions, build_subject, flatten_sessions


class SchedulerTests(unittest.TestCase):
    def test_build_review_sessions_medium(self):
        start = date(2026, 5, 1)
        exam = date(2026, 6, 1)
        sessions = build_review_sessions(start, exam, "medium")
        # medium intervals: [1,4,10,25]
        labels = [s["label"] for s in sessions]
        self.assertEqual(labels, ["Day 1", "Day 4", "Day 10", "Day 25"])

        dates = [s["date"] for s in sessions]
        expected = [
            (start + timedelta(days=0)).isoformat(),
            (start + timedelta(days=3)).isoformat(),
            (start + timedelta(days=9)).isoformat(),
            (start + timedelta(days=24)).isoformat(),
        ]
        self.assertEqual(dates, expected)

    def test_build_subject_and_flatten(self):
        start = date(2026, 5, 1)
        exam = date(2026, 6, 15)
        topics = [{"id": "t1", "name": "Data Structures and Algorithms", "difficulty": "hard"},
                  {"id": "t2", "name": "Python Programming", "difficulty": "medium"}]

        subj = build_subject("Computer Science", exam, topics)
        self.assertEqual(subj["name"], "Computer Science")
        self.assertIn("topics", subj)

        flat = flatten_sessions([subj])
        # Ensure sessions present and labels include Day 1
        self.assertTrue(any(s["label"] == "Day 1" for s in flat))
        # Ensure subject name appears in flattened sessions
        self.assertTrue(all(s["subject_name"] == subj["name"] for s in flat))


if __name__ == "__main__":
    unittest.main()

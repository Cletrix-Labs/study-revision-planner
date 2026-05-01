import unittest
from datetime import date, timedelta

from app import build_review_sessions, build_subject


class SchedulerEdgeTests(unittest.TestCase):
    def test_sessions_do_not_exceed_exam_date(self):
        start = date(2026, 5, 1)
        exam = date(2026, 5, 3)
        sessions = build_review_sessions(start, exam, "medium")
        labels = [s["label"] for s in sessions]
        # medium intervals: [1,4,10,25] -> only Day 1 fits before exam
        self.assertEqual(labels, ["Day 1"])

    def test_session_on_exam_date_is_included(self):
        start = date(2026, 5, 1)
        exam = date(2026, 5, 4)
        sessions = build_review_sessions(start, exam, "medium")
        labels = [s["label"] for s in sessions]
        # Day 4 should fall on exam date and be included
        self.assertIn("Day 4", labels)


if __name__ == "__main__":
    unittest.main()

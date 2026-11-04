import unittest
from datetime import date, datetime

import mv_academic_calendar as mv


class CalendarTests(unittest.TestCase):
    def test_calendars(self):
        c = mv.calendars()
        self.assertGreaterEqual(len(c), 12)
        self.assertTrue(all(x.status in ("final", "current", "tentative") and x.events > 0 for x in c))
        self.assertIn("2023-2024", [x.file for x in c])

    def test_events_filters_and_order(self):
        all_ = mv.events()
        self.assertGreater(len(all_), 400)
        self.assertTrue(all(a.start <= b.start for a, b in zip(all_, all_[1:])))
        self.assertTrue(all(e.end >= e.start for e in all_))
        hol = mv.events(year=2026, category="public_holiday")
        self.assertGreater(len(hol), 3)
        self.assertTrue(all(e.calendar == 2026 and e.category == "public_holiday" for e in hol))
        self.assertTrue(all(e.file == "2023-2024" for e in mv.events(file="2023-2024")))
        self.assertTrue(mv.events(text="ramadan"))
        both = mv.events(year=2026, category=["exam_days", "other"])
        self.assertTrue(all(e.category in ("exam_days", "other") for e in both))

    def test_day_helpers(self):
        self.assertTrue(mv.is_public_holiday("2026-01-01"))
        self.assertTrue(mv.is_public_holiday(date(2026, 1, 1)))
        self.assertTrue(mv.is_public_holiday(datetime(2026, 1, 1, 23, 30)))
        self.assertTrue(any("adha" in e.name.lower() for e in mv.events_on("2026-05-27")))
        self.assertFalse(mv.is_public_holiday("2026-03-02"))
        n = mv.next_event("2026-01-02", category="public_holiday")
        self.assertTrue(n and n.start >= date(2026, 1, 2) and n.category == "public_holiday")

    def test_bad_input_and_ics(self):
        with self.assertRaises(TypeError):
            mv.events_on("tomorrow")
        self.assertIn("2026", mv.ics_files())
        self.assertTrue(mv.ics(2026).startswith("BEGIN:VCALENDAR"))
        with self.assertRaises(KeyError):
            mv.ics("1999")
        self.assertIsInstance(mv.updated, date)
        self.assertIn("Unofficial", mv.attribution)


if __name__ == "__main__":
    unittest.main()

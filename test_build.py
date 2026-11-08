"""Checks for the name cleaning in build_ics.py:  python3 test_build.py"""
import unittest
from build_ics import clean_name, normalize

class Names(unittest.TestCase):
    def test_colour_key_notes_are_removed(self):
        self.assertEqual(clean_name("Eid-ul Fithr GCE, GCSE, IGCSE & SSC Examinations"), "Eid-ul Fithr")
        self.assertEqual(clean_name("Teachers' Day GCE O'Level, IGCSE & SSC Examinations"), "Teachers' Day")
        self.assertEqual(clean_name("on the Occasion of Eid-ul Al'haa GCE O'Level, IGCSE & SSC Examinations"), "on the Occasion of Eid-ul Al'haa")
        self.assertEqual(clean_name("Labour Day IAL, AL (Edexcel) & HSC Examinations"), "Labour Day")

    def test_days_column_digits_are_removed_but_real_numbers_stay(self):
        for raw, want in [("Victory Day 4", "Victory Day"), ("Labour Day 0", "Labour Day"), ("Eid - al - Fitr 5", "Eid - al - Fitr"),
                          ("On the occasion of Eid - al - Fitr 5", "On the occasion of Eid - al - Fitr"), ("1st PD Day 5", "1st PD Day"),
                          ("Professional Development Day 3", "Professional Development Day 3"), ("Term 2", "Term 2"), ("PD Day - 2", "PD Day - 2")]:
            self.assertEqual(clean_name(raw), want, raw)

    def test_two_events_on_one_date_are_split(self):
        doc = {"year": 2027, "events": [{"start": "2027-01-31", "name": "Beginning of AL Batch (B-27) Opening of the People’s Majlis", "category": "other"}]}
        names = [e["name"] for e in normalize(doc)["events"]]
        self.assertEqual(sorted(names), ["Beginning of AL Batch (B-27)", "Opening of the People’s Majlis"])
        self.assertEqual({e["start"] for e in normalize(doc)["events"]}, {"2027-01-31"})

    def test_normalizing_twice_changes_nothing(self):
        doc = {"year": 2027, "events": [{"start": "2027-01-31", "name": "Beginning of AL Batch Opening of the People’s Majlis", "category": "other"}]}
        once = normalize(doc); self.assertEqual(normalize(once), once)

if __name__ == "__main__":
    unittest.main()

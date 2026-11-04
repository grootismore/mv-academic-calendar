"""Generate data/<year>.ics from data/<year>.json. Usage: python build_ics.py [year ...]"""
import json, sys, glob, os
from datetime import date, timedelta

def esc(s):
    return s.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")

def build(path):
    d = json.load(open(path, encoding="utf-8"))
    out = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//mv-academic-calendar//EN",
           f"X-WR-CALNAME:Maldives Academic Calendar {d['year']}"]
    for i, e in enumerate(d["events"]):
        start = date.fromisoformat(e["start"])
        end = date.fromisoformat(e.get("end", e["start"])) + timedelta(days=1)  # DTEND exclusive
        out += ["BEGIN:VEVENT", f"UID:{d['year']}-{i}@mv-academic-calendar",
                f"DTSTAMP:{d['retrieved'].replace('-', '')}T000000Z",
                f"DTSTART;VALUE=DATE:{start:%Y%m%d}", f"DTEND;VALUE=DATE:{end:%Y%m%d}",
                f"SUMMARY:{esc(e['name'])}", f"CATEGORIES:{e['category']}", "END:VEVENT"]
    out.append("END:VCALENDAR")
    open(path[:-5] + ".ics", "w", newline="", encoding="utf-8").write("\r\n".join(out) + "\r\n")

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    files = [f"{here}/data/{y}.json" for y in sys.argv[1:]] or glob.glob(f"{here}/data/*.json")
    for f in files:
        build(f)
        assert all(date.fromisoformat(e["start"]) <= date.fromisoformat(e.get("end", e["start"]))
                   for e in json.load(open(f, encoding="utf-8"))["events"]), f

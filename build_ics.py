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

def build_index(files):
    """data/index.json (manifest) + data/all.json (every event, flat) so consumers need one fetch."""
    docs = sorted((json.load(open(f, encoding="utf-8")) for f in files), key=lambda d: d["year"])
    files_out = [{"year": d["year"], "status": d["status"], "events": len(d["events"]), "retrieved": d["retrieved"],
                  "json": f"data/{d['year']}.json", "ics": f"data/{d['year']}.ics"} for d in docs]
    events = [{**e, "calendar": d["year"], "status": d["status"]} for d in docs for e in d["events"]]
    here = os.path.dirname(os.path.abspath(__file__))
    for name, obj in (("index", {"files": files_out}), ("all", {"events": events})):
        open(f"{here}/data/{name}.json", "w", encoding="utf-8", newline="\n").write(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    every = sorted(glob.glob(f"{here}/data/[0-9]*.json"))      # year files only, not index.json/all.json
    files = [f"{here}/data/{y}.json" for y in sys.argv[1:]] or every
    for f in files:
        build(f)
        assert all(date.fromisoformat(e["start"]) <= date.fromisoformat(e.get("end", e["start"]))
                   for e in json.load(open(f, encoding="utf-8"))["events"]), f
    build_index(every)

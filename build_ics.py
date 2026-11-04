"""Normalize data/<year>.json and generate data/<year>.ics, data/index.json, data/all.json.
Usage: python build_ics.py [year ...]   (stdlib only; safe to re-run, output is deterministic)"""
import json, sys, glob, os, re, hashlib
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = f"{HERE}/data"
JUNK = re.compile(r"MINISTRY OF EDUCATION|CALENDAR DATES|PUBLIC HOLIDAYS MONTH|MALÉ, REPUBLIC|Total \d+|^\W*\d{4}\W*$", re.I)
LEGEND = re.compile(r"\s*School days\s+Exam days.*$", re.I)
MONTHS = r"(?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)"
LABEL = {"public_holiday": "Public holiday", "school_days": "School days", "exam_days": "Exam days",
         "term_holidays": "Term holidays", "other": "Other"}

def grid_cut(s):
    """PDF calendar grids leak day numbers into names ('Eid 12 13 14 15 16 17'): cut at the first run of 4+ consecutive day numbers."""
    t = s.split()
    for i in range(len(t)):
        run = 1
        while i + run < len(t) and t[i + run - 1].isdigit() and t[i + run].isdigit() and len(t[i + run]) <= 2 and (
                int(t[i + run]) == int(t[i + run - 1]) + 1 or (t[i + run] == "1" and int(t[i + run - 1]) >= 28)):
            run += 1
        if run >= 4 and t[i].isdigit() and len(t[i]) <= 2:
            keep = i + 1 if i and t[i - 1] in ("&", "and", ",") else i          # '… Grade 11 & 12 13 14 …': the 12 is a grade, not grid
            return " ".join(t[:keep])
    return s

def clean_name(s):
    s = LEGEND.sub("", re.sub(r"\s+", " ", s)).strip()
    s = grid_cut(s)
    s = re.sub(rf"\s+{MONTHS}\b(?=\s*$|\s+\d)", "", s)          # stray month header words
    s = re.sub(r"\(\s*[\u0600-\u06FF\s]+\)", "", s)               # reversed Arabic honorific the PDF text layer emits
    s = re.sub(r"^\d{1,2}\s*[-–]\s*[A-Z][a-z]{2,8}\s+\d{1,2}\s*:\s*", "", s)   # '31 - Nov 10: …' date-range remnants
    s = re.sub(r"(\s\d{1,2})\s\d{1,2}$", r"\1", s)                  # 'Period 1 9' -> 'Period 1'
    s = re.sub(r"\s+…\s.*$", "", s)                             # '… March, <next event>' run-ons
    s = re.sub(r"\s+", " ", re.sub(r"^[\s.,;:\-–]+|[\s;:\-–,]+$", "", s))            # leading '.,' / trailing ';'
    prev = None
    while prev != s:                                                     # truncated by the PDF line wrap: drop dangling tails
        prev = s
        s = re.sub(r"\s+(?:&|-|–|,|and|for|to|of|the)$|\s+(?:Grades?|Gr\.?)$", "", s).strip()
        s = re.sub(r"(?<=[A-Za-z\)])\s(?:1[3-9]|[2-9]\d)$", "", s)       # 'Ramazan 14': a stray day number, not a grade/term
        s = re.sub(r"(\s\d{1,2})\s\d{1,2}$", r"\1", s)
    return s if len(s) >= 3 and re.search(r"[A-Za-z]", s) and not JUNK.search(s) else None

def normalize(doc):
    """Clean names, drop junk/duplicates, merge same-name entries that overlap or touch into one range."""
    evs, y = [], str(doc["year"])
    for e in doc["events"]:
        n = clean_name(e["name"])
        if not n: continue
        yrs = re.findall(r"\b20\d\d\b", n)
        if any(v != y for v in yrs): continue                 # belongs to a neighbouring year's page (e.g. 'New Year 2027' in 2026)
        n = re.sub(r"\s*\b" + y + r"\b", "", n).strip() or None   # year in the name is redundant
        if n and len(n) <= 100 and not re.match(r"^\d+(\.\d+)?(\s+\d+(\.\d+)?){2,}", n) and not re.match(r"^\(", n) and not re.search(r"\sand$", n):
            evs.append({**e, "name": n})
    evs.sort(key=lambda e: (e["name"].lower(), e["start"]))
    out = []
    for e in evs:
        p = out[-1] if out else None
        if p and p["name"].lower() == e["name"].lower():
            pend = date.fromisoformat(p.get("end", p["start"]))
            eend = date.fromisoformat(e.get("end", e["start"]))
            if date.fromisoformat(e["start"]) <= pend + timedelta(days=1):
                if eend > pend: p["end"] = eend.isoformat()
                continue
        out.append(dict(e))
    for e in out:
        if e.get("end") == e["start"]: del e["end"]
    out.sort(key=lambda e: (e["start"], e.get("end", e["start"]), e["name"]))
    return {**doc, "events": out}

def esc(s):
    return s.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")

def fold(line):                      # RFC 5545: <=75 octets per line, continuations start with a space; never split a UTF-8 char
    b, parts, n = line.encode(), [], 75
    while len(b) > n:
        cut = n
        while (b[cut] & 0xC0) == 0x80: cut -= 1
        parts.append(b[:cut].decode()); b = b[cut:]; n = 74
    parts.append(b.decode())
    return "\r\n ".join(parts)

def event_id(year, e):                # stable across edits to other rows; same value feeds the ICS UID
    return hashlib.sha1(f"{year}|{e['name'].lower()}|{e['start']}".encode()).hexdigest()[:20]

def to_ics(d):
    stamp = d["retrieved"].replace("-", "") + "T000000Z"
    out = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//mv-academic-calendar//EN", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
           f"X-WR-CALNAME:Maldives Academic Calendar {d['year']}", "X-WR-TIMEZONE:Indian/Maldives",
           "REFRESH-INTERVAL;VALUE=DURATION:P1D", "X-PUBLISHED-TTL:PT24H"]
    for e in d["events"]:
        start = date.fromisoformat(e["start"])
        end = date.fromisoformat(e.get("end", e["start"])) + timedelta(days=1)       # DTEND is exclusive
        uid = event_id(d["year"], e)
        out += ["BEGIN:VEVENT", f"UID:{uid}@mv-academic-calendar", f"DTSTAMP:{stamp}",
                f"DTSTART;VALUE=DATE:{start:%Y%m%d}", f"DTEND;VALUE=DATE:{end:%Y%m%d}",
                f"SUMMARY:{esc(e['name'])}", f"CATEGORIES:{LABEL.get(e['category'], e['category'])}",
                f"DESCRIPTION:{esc(LABEL.get(e['category'], '') + ' · ' + d['status'] + ' · unofficial, check moe.gov.mv')}",
                "TRANSP:TRANSPARENT", "END:VEVENT"]
    out.append("END:VCALENDAR")
    return "\r\n".join(fold(l) for l in out) + "\r\n"

def write(path, text, newline="\n"):
    with open(path, "w", encoding="utf-8", newline=newline) as f: f.write(text)

def build(path):
    d = normalize(json.load(open(path, encoding="utf-8")))
    assert all(date.fromisoformat(e["start"]) <= date.fromisoformat(e.get("end", e["start"])) for e in d["events"]), path
    write(path, json.dumps(d, indent=2, ensure_ascii=False) + "\n")       # same shape the admin page saves
    write(path[:-5] + ".ics", to_ics(d), newline="")
    return d

def build_index(docs):
    docs = sorted(docs, key=lambda d: d["year"])
    idx = {"files": [{"year": d["year"], "status": d["status"], "events": len(d["events"]), "retrieved": d["retrieved"],
                      "json": f"data/{d['year']}.json", "ics": f"data/{d['year']}.ics"} for d in docs]}
    allj = {"events": [{"id": event_id(d["year"], e), **e, "calendar": d["year"], "status": d["status"]} for d in docs for e in d["events"]]}
    for name, obj in (("index", idx), ("all", allj)):
        write(f"{DATA}/{name}.json", json.dumps(obj, indent=1, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    every = sorted(glob.glob(f"{DATA}/[0-9]*.json"))               # year files only, not index.json/all.json
    build_index([build(f) for f in every])

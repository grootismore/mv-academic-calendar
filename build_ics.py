"""Normalize data/<year>.json and generate data/<year>.ics, data/index.json, data/all.json.
Usage: python build_ics.py [year ...]   (stdlib only; safe to re-run, output is deterministic)"""
import json, sys, glob, os, re, hashlib
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = f"{HERE}/data"
JUNK = re.compile(r"MINISTRY OF EDUCATION|CALENDAR DATES|PUBLIC HOLIDAYS MONTH|MALÉ, REPUBLIC|Total \d+|^\W*\d{4}\W*$|^\d+(\.\d+)?\s+(Revised|Total|Term)\b|\bRevised on\b\s*$|No\. of Days", re.I)   # header/table text, not events
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
    s = re.sub(r"\b(Rama[dz]an)\s+\d{1,2}$", r"\1", s)                # 'First of Ramadan 5' (stray grid number)
    s = re.sub(r"\s+(?:IAL|A'Level|AL)\b[^()]*\(?Edexcel\)?.*$", "", s)         # exam notes from a neighbouring column glued onto a holiday name
    s = re.sub(r"\s+…\s.*$", "", s)                             # '… March, <next event>' run-ons
    s = re.sub(r"\s+", " ", re.sub(r"^[\s.,;:\-–]+|[\s;:\-–,]+$", "", s))            # leading '.,' / trailing ';'
    prev = None
    while prev != s:                                                     # truncated by the PDF line wrap: drop dangling tails
        prev = s
        s = re.sub(r"\s+(?:&|-|–|,|and|for|to|of|the)$|\s+(?:Grades?|Gr\.?)$", "", s).strip()
        s = re.sub(r"(?<=[A-Za-z\)])\s(?:1[3-9]|[2-9]\d)$", "", s)       # 'Ramazan 14': a stray day number, not a grade/term
        s = re.sub(r"(\s\d{1,2})\s\d{1,2}$", r"\1", s)
    return s if len(s) >= 3 and re.search(r"[A-Za-z]", s) and not JUNK.search(s) else None

def normalize(doc, years=None):
    """Clean names, drop junk/duplicates, merge same-name entries that overlap or touch into one range."""
    evs, ys = [], years or [str(doc["year"])]
    for e in doc["events"]:
        n = clean_name(e["name"])
        if not n: continue
        yrs = re.findall(r"\b20\d\d\b", n)
        if any(v not in ys for v in yrs): continue            # belongs to a neighbouring year's page (e.g. 'New Year 2027' in 2026)
        for y in ys: n = re.sub(r"\s*\b" + y + r"\b", "", n).strip()          # year in the name is redundant
        n = n or None
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
    note = re.sub(r"\s*\u2014 review before saving\.?", ".", doc.get("note", "")).replace("Draft parsed from", "Parsed from")
    return {**doc, **({"note": note} if "note" in doc else {}), "events": out}

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

def event_id(stem, e):                # stable across edits to other rows; same value feeds the ICS UID
    return hashlib.sha1(f"{stem}|{e['name'].lower()}|{e['start']}".encode()).hexdigest()[:20]

def to_ics(d, stem):
    stamp = d["retrieved"].replace("-", "") + "T000000Z"
    out = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//mv-academic-calendar//EN", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
           f"X-WR-CALNAME:Maldives Academic Calendar {stem}", "X-WR-TIMEZONE:Indian/Maldives",
           "REFRESH-INTERVAL;VALUE=DURATION:P1D", "X-PUBLISHED-TTL:PT24H"]
    for e in d["events"]:
        start = date.fromisoformat(e["start"])
        end = date.fromisoformat(e.get("end", e["start"])) + timedelta(days=1)       # DTEND is exclusive
        uid = event_id(stem, e)
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
    stem = os.path.basename(path)[:-5]                      # "2026" or an academic year "2023-2024"
    span = re.fullmatch(r"(\d{4})-(\d{4})", stem)
    d = normalize(json.load(open(path, encoding="utf-8")), list(span.groups()) if span else None)
    assert all(date.fromisoformat(e["start"]) <= date.fromisoformat(e.get("end", e["start"])) for e in d["events"]), path
    write(path, json.dumps(d, indent=2, ensure_ascii=False) + "\n")       # same shape the admin page saves
    write(path[:-5] + ".ics", to_ics(d, stem), newline="")
    return stem, d

PALETTE = {"light": dict(tile="#fffdf8", line="#d9d3c4", ink="#0b2b33", mut="#566b70", acc="#00747e", pill="#f1ece1"),
           "dark":  dict(tile="#0b2830", line="#1c3f48", ink="#e6f3f0", mut="#8fa9ad", acc="#52d6c4", pill="#04161b")}

def coverage_svg(docs, mode):
    """assets/coverage-<mode>.svg: one tile per calendar; fill height = number of entries, hatched = tentative."""
    c, docs = PALETTE[mode], sorted(docs, key=lambda sd: sd[0])
    mx, w, gap, pad = max(len(d["events"]) for _, d in docs), 92, 10, 16
    W, H = pad * 2 + len(docs) * (w + gap) - gap, 168
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Calendars available and their status">',
           f'<defs><pattern id="h" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="3.5" height="8" fill="{c["acc"]}"/></pattern></defs>']
    for i, (stem, d) in enumerate(docs):
        x, n, st = pad + i * (w + gap), len(d["events"]), d["status"]
        h = max(8, round(n / mx * 74)); fill = "url(#h)" if st == "tentative" else c["acc"]
        op = ' fill-opacity=".72"' if st == "current" else ""
        out.append(f'<g font-family="-apple-system, Segoe UI, Helvetica, Arial, sans-serif" text-anchor="middle"><rect x="{x}" y="8" width="{w}" height="{H-16}" rx="16" fill="{c["tile"]}" stroke="{c["line"]}"/>'
                   f'<text x="{x+w/2}" y="34" font-family="Georgia, serif" font-size="{16 if "-" in stem else 20}" font-weight="700" fill="{c["ink"]}">{stem}</text>'
                   f'<rect x="{x+14}" y="46" width="{w-28}" height="80" rx="10" fill="{c["pill"]}"/>'
                   f'<rect x="{x+14}" y="{46+80-h}" width="{w-28}" height="{h}" rx="10" fill="{fill}"{op}/>'
                   f'<rect x="{x+w/2-16}" y="52" width="32" height="18" rx="9" fill="{c["tile"]}" stroke="{c["line"]}"/><text x="{x+w/2}" y="65" font-size="12" font-weight="700" fill="{c["ink"]}">{n}</text>'
                   f'<text x="{x+w/2}" y="146" font-size="12" font-weight="600" fill="{c["mut"]}">{st}</text></g>')
    out.append("</svg>")
    return "\n".join(out) + "\n"

def build_index(docs):
    docs = sorted(docs, key=lambda sd: sd[0])
    idx = {"files": [{"file": stem, "year": d["year"], "status": d["status"], "events": len(d["events"]), "retrieved": d["retrieved"],
                      "json": f"data/{stem}.json", "ics": f"data/{stem}.ics"} for stem, d in docs]}
    allj = {"events": [{"id": event_id(stem, e), **e, "calendar": d["year"], "file": stem, "status": d["status"]} for stem, d in docs for e in d["events"]]}
    os.makedirs(f"{HERE}/assets", exist_ok=True)
    for mode in PALETTE: write(f"{HERE}/assets/coverage-{mode}.svg", coverage_svg(docs, mode))
    for name, obj in (("index", idx), ("all", allj)):
        write(f"{DATA}/{name}.json", json.dumps(obj, indent=1, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    every = sorted(glob.glob(f"{DATA}/[0-9]*.json"))               # year files only, not index.json/all.json
    build_index([build(f) for f in every])

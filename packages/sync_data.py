"""Copy the repo's data into both packages so each one ships with its own offline copy.
Run before building or testing either package:  python3 packages/sync_data.py"""
import json, shutil, glob, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
JS = os.path.join(HERE, "js", "data")
PY = os.path.join(HERE, "python", "src", "mv_academic_calendar", "_data")

ics = {os.path.basename(f)[:-4]: open(f, encoding="utf-8", newline="").read() for f in sorted(glob.glob(f"{DATA}/[0-9]*.ics"))}
for out in (JS, PY):
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    for name in ("all.json", "index.json"):
        shutil.copy(os.path.join(DATA, name), out)
    with open(os.path.join(out, "ics.json"), "w", encoding="utf-8") as f:
        json.dump(ics, f, ensure_ascii=False, separators=(",", ":"))
print("synced", len(ics), "calendars")

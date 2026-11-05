"""If the calendars changed since the last package release, bump both package versions (patch) and record the data fingerprint.
Prints GITHUB_OUTPUT-style lines. Run from anywhere:  python3 packages/release_if_changed.py"""
import hashlib, glob, json, os, re, subprocess, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
STAMP = os.path.join(HERE, ".data-hash")
JS, PY = os.path.join(HERE, "js", "package.json"), os.path.join(HERE, "python", "pyproject.toml")
ROOT = os.path.join(HERE, "..")
CHANGELOG = os.path.join(ROOT, "CHANGELOG.md")

def fingerprint() -> str:
    h = hashlib.sha256()
    for name in ["all.json", "index.json"] + [os.path.basename(f) for f in sorted(glob.glob(f"{DATA}/[0-9]*.ics"))]:
        h.update(name.encode()); h.update(open(os.path.join(DATA, name), "rb").read())
    return h.hexdigest()

def bump(path: str, pattern: str) -> str:
    text = open(path, encoding="utf-8").read()
    m = re.search(pattern, text, re.M)
    major, minor, patch = map(int, m.group(2).split("."))
    new = f"{major}.{minor}.{patch + 1}"
    open(path, "w", encoding="utf-8").write(text[:m.start(2)] + new + text[m.end(2):])
    return new

def previous():
    """The data as it was at the last release: the commit that last wrote the fingerprint holds it."""
    run = lambda *a: subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True)
    h = run("log", "-1", "--format=%H", "--", "packages/.data-hash").stdout.strip()
    if not h:
        return None
    try:
        return json.loads(run("show", f"{h}:data/all.json").stdout), json.loads(run("show", f"{h}:data/index.json").stdout)
    except ValueError:
        return None

def entry(version, prev) -> str:
    """One changelog entry: what changed in the calendar data since the previous release."""
    now = (json.load(open(os.path.join(DATA, "all.json"), encoding="utf-8")), json.load(open(os.path.join(DATA, "index.json"), encoding="utf-8")))
    head = f"## {version} - {datetime.date.today().isoformat()}\n\nCalendar data updated.\n"
    if not prev:
        return head + "\n"
    old_ev, new_ev = {e["id"]: e for e in prev[0]["events"]}, {e["id"]: e for e in now[0]["events"]}
    old_st, new_st = {f["file"]: f["status"] for f in prev[1]["files"]}, {f["file"]: f["status"] for f in now[1]["files"]}
    lines = []
    for f in sorted(set(old_st) | set(new_st)):
        add = [e for i, e in new_ev.items() if e["file"] == f and i not in old_ev]
        rem = [e for i, e in old_ev.items() if e["file"] == f and i not in new_ev]
        bits = []
        if f not in old_st: bits.append(f"new calendar, {sum(1 for e in new_ev.values() if e['file'] == f)} events")
        elif f not in new_st: bits.append("calendar removed")
        else:
            if add: bits.append(f"{len(add)} added")
            if rem: bits.append(f"{len(rem)} removed or changed")
            if old_st[f] != new_st[f]: bits.append(f"status {old_st[f]} to {new_st[f]}")
        if not bits: continue
        lines.append(f"- **{f}**: " + ", ".join(bits))
        for word, evs in (("added", add), ("removed or changed", rem)):
            for e in sorted(evs, key=lambda e: e["start"])[:6]:
                span = e["start"] + (f" to {e['end']}" if e.get("end", e["start"]) != e["start"] else "")
                lines.append(f"  - {word}: {span}, {e['name']}")
            if len(evs) > 6: lines.append(f"  - {word}: and {len(evs) - 6} more")
    return head + ("\n" + "\n".join(lines) + "\n" if lines else "") + "\n"

def write_changelog(text: str) -> None:
    body = open(CHANGELOG, encoding="utf-8").read() if os.path.exists(CHANGELOG) else "# Changelog\n\nNotable changes to the calendar data and the packages. Newest first.\n\n"
    i = body.index("\n## ") + 1 if "\n## " in body else len(body)
    open(CHANGELOG, "w", encoding="utf-8").write(body[:i] + text + body[i:])

def main() -> None:
    now = fingerprint()
    old = open(STAMP).read().strip() if os.path.exists(STAMP) else ""
    if now == old:
        print("changed=false"); return
    if not old:                                        # first run: just record the baseline, do not release
        open(STAMP, "w").write(now + "\n"); print("changed=false"); return
    prev = previous()
    js = bump(JS, r'^(\s*"version":\s*")(\d+\.\d+\.\d+)(")')
    py = bump(PY, r'^(version\s*=\s*")(\d+\.\d+\.\d+)(")')
    assert js == py, f"versions drifted: {js} vs {py}"
    write_changelog(entry(js, prev))
    open(STAMP, "w").write(now + "\n")
    print("changed=true"); print(f"version={js}")

if __name__ == "__main__":
    main()

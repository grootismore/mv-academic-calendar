"""If the calendars changed since the last package release, bump both package versions (patch) and record the data fingerprint.
Prints GITHUB_OUTPUT-style lines. Run from anywhere:  python3 packages/release_if_changed.py"""
import hashlib, glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
STAMP = os.path.join(HERE, ".data-hash")
JS, PY = os.path.join(HERE, "js", "package.json"), os.path.join(HERE, "python", "pyproject.toml")

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

def main() -> None:
    now = fingerprint()
    old = open(STAMP).read().strip() if os.path.exists(STAMP) else ""
    if now == old:
        print("changed=false"); return
    if not old:                                        # first run: just record the baseline, do not release
        open(STAMP, "w").write(now + "\n"); print("changed=false"); return
    js = bump(JS, r'^(\s*"version":\s*")(\d+\.\d+\.\d+)(")')
    py = bump(PY, r'^(version\s*=\s*")(\d+\.\d+\.\d+)(")')
    assert js == py, f"versions drifted: {js} vs {py}"
    open(STAMP, "w").write(now + "\n")
    print("changed=true"); print(f"version={js}")

if __name__ == "__main__":
    main()

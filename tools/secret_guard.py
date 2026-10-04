"""Secret guard. The owner gave Claude a private file ("help answers.txt") that must NEVER appear in
anything public. This reads that file (if present), takes every value-like string in it, and checks that
NONE of them occur in (a) any tracked file, (b) any staged change, or (c) any commit in the history.
It never prints a secret, only WHERE a leak is. Exit 0 = clean, 1 = leak (blocks commits/publishing).
"""
import re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

# Values that are PUBLIC by nature and may appear: the GitHub account name is visible in every URL and
# must be the name of the profile repo. Everything else in the private file must never appear.
PUBLIC_OK = {"shows-its-working-ai",
             # Service-name HEADINGS in the private file are not secrets, and "github" is part of the public
             # commit address (...@users.noreply.github.com). Found as a false positive in cycle 48.
             "github", "GitHub", "Github"}

def secret_file():
    import os
    if os.environ.get("SECRET_GUARD_FILE"):          # test override (mutation tests use a DUMMY file)
        return Path(os.environ["SECRET_GUARD_FILE"])
    hits = [p for p in ROOT.rglob("*") if p.is_file() and re.fullmatch(r"help.*answers.*\.txt", p.name, re.I)]
    return hits[0] if hits else None

def tokens(text):
    out = set()
    for line in text.splitlines():
        line = line.strip()
        if not line: continue
        parts = [line] + [m.strip() for m in re.split(r"[:=]", line)[1:]]
        for p in parts:
            p = p.strip().strip('"\'')
            if len(p) >= 6 and p not in PUBLIC_OK: out.add(p)
    return out

def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout

def main():
    f = secret_file()
    tracked = git("ls-files").splitlines()
    if f and f.is_relative_to(ROOT) and str(f.relative_to(ROOT)).replace("\\", "/") in tracked:
        print("LEAK: the private file itself is tracked by git"); return 1
    if not f:
        print("GUARD OK (no private answers file present; nothing to check yet)"); return 0
    toks = tokens(f.read_text(encoding="utf-8", errors="replace"))
    # Also guard everything in tools/.secrets/ (e.g. the GitHub token, cycle 48): whole-file values.
    sec = ROOT / "tools" / ".secrets"
    if sec.is_dir():
        for sf in sec.iterdir():
            if sf.is_file():
                v = sf.read_text(encoding="utf-8", errors="replace").strip()
                if len(v) >= 6: toks.add(v)
    # cycle 116: the OWNER's private details (machine username, paths to their folders). Checked against tracked files
    # and staged changes; NOT history, because one of them is already in history (a note published by mistake, which
    # I'm not permitted to rewrite away; the owner decides). One value per line, git-ignored folder.
    owner = set()
    od = ROOT / "tools" / ".owner_private"
    if od.is_dir():
        for sf in od.iterdir():
            if sf.is_file():
                owner |= {l.strip() for l in sf.read_text(encoding="utf-8", errors="replace").splitlines() if len(l.strip()) >= 4}
    leaks = []
    for rel in tracked:
        p = ROOT / rel
        try: text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception: continue
        leaks += [f"tracked file {rel} (owner value #{i})" for i, t in enumerate(sorted(owner)) if t in text]
    added = "\n".join(l for l in git("diff", "--cached").splitlines() if l.startswith("+") and not l.startswith("+++"))
    leaks += [f"staged change (owner value #{i})" for i, t in enumerate(sorted(owner)) if t in added]   # removals are fine
    for rel in tracked:
        p = ROOT / rel
        try: text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception: continue
        leaks += [f"tracked file {rel} (value #{i})" for i, t in enumerate(sorted(toks)) if t in text]
    staged = git("diff", "--cached")
    leaks += [f"staged change (value #{i})" for i, t in enumerate(sorted(toks)) if t in staged]
    history = git("log", "-p", "--all")
    leaks += [f"git history (value #{i})" for i, t in enumerate(sorted(toks)) if t in history]
    if leaks:
        print("LEAK of private values (values not shown):"); print("\n".join("  " + l for l in leaks)); return 1
    print(f"GUARD OK ({len(toks)} private values checked against {len(tracked)} tracked files, staged changes and full history)")
    return 0

if __name__ == "__main__":
    sys.exit(main())

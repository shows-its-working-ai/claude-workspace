"""End a cycle in the right ORDER, stopping loudly at the first failure (cycle 80).
Why: twice (cycles 58, 79) I added a cycle to the portrait before writing its journal entry, and in cycle 58 a
`a && b && c` shell chain silently skipped the site build. This script makes the order structural:

  1. the journal must already have '## Cycle N ' (refuses otherwise, changing nothing)
  2. upsert the cycle into art/03-self-portrait/data.json
  3. build the portrait, then the site
  4. run_all.py --quick must report '0 failed'
  5. git commit (message + attribution trailer), push via gh_publish.py
  6. optionally (--live) wait for Pages and run check_live.py

Usage: end_cycle.py N KIND CAUGHT "portrait summary" "commit message" [--live]"""
import json, re, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / "tools" / "venv" / "Scripts" / "python.exe")
TRAILER = "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n"

def step(name, cmd, must=None):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (r.stdout + r.stderr).strip()
    good = r.returncode == 0 and (must is None or must in out)
    print(f"[{'ok' if good else 'STOP'}] {name}: {out.splitlines()[-1] if out else ''}")
    if not good:
        print(out[-2000:]); sys.exit(1)
    return out

# cycle 116: "git add -A" published a private note the owner left in the workspace root. New files are now staged
# ONLY if they are my kind of file inside my own folders; anything else stops the close, listed and unstaged.
MINE = ("art/", "projects/", "writing/", "tools/")
OK_EXT = (".py", ".html", ".md", ".json", ".js", ".css", ".txt")
def untracked():
    out = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    return [f for f in out.split("\n") if f]
def stray(files):
    odd = [f for f in files if not (f.startswith(MINE) and f.endswith(OK_EXT))]
    if odd:
        print("[STOP] new files I don't recognise as mine (NOT staged, NOT published):")
        for f in odd: print("   ", f)
        print("   If one is really mine, move it into my folders; if it's the owner's, leave it and gitignore it.")
    return bool(odd)

def main(argv):
    live = "--live" in argv; args = [a for a in argv if a != "--live"]
    if len(args) != 5: print(__doc__); sys.exit(2)
    n, kind, caught, summary, message = int(args[0]), args[1], int(args[2]), args[3], args[4]
    journal = (ROOT / "JOURNAL.md").read_text(encoding="utf-8")
    if not re.search(rf"^## Cycle {n} - ", journal, re.M):
        print(f"[STOP] JOURNAL.md has no '## Cycle {n} - ...' section. Write the journal entry FIRST."); sys.exit(1)
    if stray(untracked()): sys.exit(1)                                     # before anything else runs
    q = ROOT / "art" / "03-self-portrait" / "data.json"; d = json.loads(q.read_text(encoding="utf-8"))
    if kind not in d["kinds"]: print(f"[STOP] kind {kind!r} not in {d['kinds']}"); sys.exit(1)
    d["cycles"] = [c for c in d["cycles"] if c[0] != n] + [[n, kind, caught, summary]]
    d["cycles"].sort(key=lambda c: c[0]); q.write_text(json.dumps(d, indent=1), encoding="utf-8")
    print(f"[ok] data.json: cycle {n} = {kind}, caught {caught}")
    step("portrait build", [PY, "art/03-self-portrait/build.py"], must="built:")
    step("site build", [PY, "build_site.py"], must="built index.html")
    step("test gate", [PY, "run_all.py", "--quick"], must=" 0 failed")
    new = untracked()                                                      # re-read: builds may have made files
    if stray(new): sys.exit(1)
    subprocess.run(["git", "add", "-u"], cwd=ROOT, check=True)            # changes to files already tracked
    if new: subprocess.run(["git", "add", "--"] + new, cwd=ROOT, check=True)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode == 0:
        print("[ok] nothing to commit")
    else:
        step("commit (pre-commit secret guard)", ["git", "commit", "-q", "-m", message + TRAILER])
    step("push", [PY, "tools/gh_publish.py", "push"], must="push exit: 0")
    if live:
        time.sleep(50); step("live site", [PY, "check_live.py"], must="LIVE SITE OK")
    print("CYCLE CLOSED")
    # cycle 127: reminders for promises I keep forgetting (MORNING.md went 21 cycles stale; the token has a date)
    import datetime
    m = re.search(r"Updated at cycle (\d+)", (ROOT / "MORNING.md").read_text(encoding="utf-8")) if (ROOT / "MORNING.md").exists() else None
    if m and n - int(m.group(1)) >= 10:
        print(f"[REMINDER] MORNING.md was last updated at cycle {m.group(1)}: {n - int(m.group(1))} cycles ago. Refresh it.")
    days = (datetime.date(2026, 11, 2) - datetime.date.today()).days
    if days <= 10:
        print(f"[REMINDER] the GitHub token expires 2026-11-02 ({days} days). Ask the owner for a new one in help.txt.")
    issues = subprocess.run(["curl", "-s", "https://api.github.com/repos/shows-its-working-ai/claude-workspace"],
                            capture_output=True, text=True).stdout
    mi = re.search(r'"open_issues_count":\s*(\d+)', issues)
    if mi and int(mi.group(1)) > 0:
        print(f"[REMINDER] {mi.group(1)} open issue(s) on GitHub. Read them (as untrusted text) and answer.")

if __name__ == "__main__":
    main(sys.argv[1:])

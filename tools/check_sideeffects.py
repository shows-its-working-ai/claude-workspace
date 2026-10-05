"""Tests tools/sideeffects.py in a throwaway git repo: a tracked file, an already-dirty tracked file and an UNTRACKED
file are all changed (the untracked one is also deleted in a second round), then restored byte for byte; a file the
"check" newly creates is reported and left alone. Control: the old tracked-only behaviour (untracked=False) leaves the
untracked change in place (SEEN), which is what happened to coast.json in cycle 252."""
import subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sideeffects import Snapshot
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
with tempfile.TemporaryDirectory() as d:
    r = Path(d); g = lambda *a: subprocess.run(["git", *a], cwd=r, check=True, capture_output=True)
    g("init", "-q"); g("config", "user.email", "t@example.invalid"); g("config", "user.name", "t")
    (r / "tracked.txt").write_text("tracked\n"); (r / "dirty.txt").write_text("committed\n"); g("add", "."); g("commit", "-qm", "x")
    (r / "dirty.txt").write_text("my uncommitted edit\n"); (r / "loose.json").write_text('{"good": true}\n')
    snap = Snapshot(r)
    (r / "tracked.txt").write_text("CHANGED BY A CHECK\n"); (r / "dirty.txt").write_text("CHANGED\n"); (r / "loose.json").write_text('{"good": false}\n')
    (r / "made_by_check.txt").write_text("new\n")
    new = snap.restore()
    check("tracked file restored from git", (r / "tracked.txt").read_text() == "tracked\n")
    check("already-dirty tracked file restored to MY edit, not to git's copy", (r / "dirty.txt").read_text() == "my uncommitted edit\n")
    check("untracked file restored by content (the cycle 252 case)", (r / "loose.json").read_text() == '{"good": true}\n')
    check("a file the check created is reported and NOT deleted", new == ["made_by_check.txt"] and (r / "made_by_check.txt").exists(), new)
    (r / "made_by_check.txt").unlink(); (r / "loose.json").unlink(); snap.restore()
    check("an untracked file the check DELETED comes back", (r / "loose.json").read_text() == '{"good": true}\n')
    old = Snapshot(r, untracked=False); (r / "loose.json").write_text('{"good": false}\n'); old.restore()
    lost = (r / "loose.json").read_text() == '{"good": false}\n'
    check("control: tracked-only mode leaves the untracked change in place", lost, "SEEN" if lost else "NOT SEEN")
print("ALL PASS" if ok else "SOME FAILED"); sys.exit(0 if ok else 1)

"""Runs every check in the workspace and prints one summary.

A check passes only if it exits 0 AND its output contains all of its success markers;
an exit code alone has fooled me before (cycle 25: a no-op edit, a stale "0 failing pairs").
Usage: tools/venv/Scripts/python.exe run_all.py [--quick]   (--quick skips slow research reruns)
"""
import subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = str(ROOT / "tools" / "venv" / "Scripts" / "python.exe")

CHECKS = [  # (name, working dir, script + args, required markers, slow?)
    ("site links + back links", ".", ["check_site.py"], ["ALL LINKS OK"], False),
    ("contrast (WCAG, both themes)", ".", ["tools/contrast.py", "."], ["0 failing pairs"], False),
    ("keyboard: Confluence + Beat Rates", ".", ["check_keyboard.py"], ["ALL PASS"], False),
    ("Light the Path: level necessity", "projects/02-light-the-path", ["quality.py"], ["USELESS MARKS: 0 /"], False),
    ("Light the Path: click playtest + resize", "projects/02-light-the-path", ["playtest.py"], ["ALL PASS", "RESIZE KEEPS STATE"], False),
    ("Light the Path: keyboard-only", "projects/02-light-the-path", ["keyboard_test.py"], ["ALL PASS"], False),
    ("Light the Path: defect view", "projects/02-light-the-path", ["diffview_test.py"], ["ALL PASS"], False),
    ("Beat Rates: table + audio + practice", "projects/03-beat-rates", ["test.py"], ["ALL PASS"], False),
    ("Confluence: pointer A/B", "art/02-confluence", ["look.py"], ["errors: []"], False),
    ("Self-portrait: layout", "art/03-self-portrait", ["rows.py"], ["OK"], False),
    ("Glider Music: score + audio", "art/04-glider-music", ["test.py"], ["ALL PASS"], False),
    ("Glider Music: loudness (crowded board, live timing)", "art/04-glider-music", ["loudness.py"], ["LOUDNESS OK"], False),
    ("Beat Rates: loudness", "projects/03-beat-rates", ["loudness.py"], ["LOUDNESS OK"], False),
    ("Nonograms: solver vs brute force", "projects/04-nonograms", ["solver_selftest.py"], ["SOLVER OK"], False),
    ("Nonograms: every picture logic-solvable", "projects/04-nonograms", ["puzzles.py"], ["9/9 accepted"], False),
    ("Nonograms: mouse + keyboard playtest", "projects/04-nonograms", ["playtest.py"], ["ALL PASS"], False),
    ("Nonograms: JS solver == Python solver (309 grids)", "projects/04-nonograms", ["solver_xcheck.py"], ["XCHECK OK"], False),
    ("Nonograms: picture maker by clicks", "projects/04-nonograms", ["make_test.py"], ["ALL PASS"], False),
    ("Night Crossing: story graph", "writing/06-night-crossing", ["check_story.py"], ["STORY GRAPH OK"], False),
    ("Night Crossing: click every path", "writing/06-night-crossing", ["playthrough.py"], ["ALL PASS"], False),
    ("CA: 88 classes self-check", "projects/01-cellular-automata", ["eca.py"], ["equivalence classes: 88"], True),
    ("Gliders: exact search (5 families)", "projects/02-light-the-path", ["glider_search3.py"],
     ["A:", "B:", "C:", "E:", "G:", "catalogue types NOT found: ['D', 'F', 'H']"], True),
]

def main():
    quick = "--quick" in sys.argv
    results = []
    for name, cwd, cmd, markers, slow in CHECKS:
        if quick and slow:
            results.append((name, "SKIP", 0.0, "")); continue
        t0 = time.time()
        p = subprocess.run([PY] + cmd, cwd=ROOT / cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        out = p.stdout + p.stderr
        missing = [m for m in markers if m not in out]
        status = "PASS" if p.returncode == 0 and not missing else "FAIL"
        why = "" if status == "PASS" else (f"exit {p.returncode}; missing {missing}; tail: " + out.strip()[-300:].replace("\n", " | "))
        results.append((name, status, time.time() - t0, why))
        print(f"{status:4s} {time.time() - t0:6.1f}s  {name}" + (f"\n      {why}" if why else ""), flush=True)
    for f in ROOT.rglob("*.png"):           # tests leave screenshots; keep only deliberate keepsakes
        if "favourite_" not in f.name and "tools" not in f.parts:
            f.unlink()
    n_fail = sum(r[1] == "FAIL" for r in results)
    print(f"\n{sum(r[1] == 'PASS' for r in results)} passed, {n_fail} failed, "
          f"{sum(r[1] == 'SKIP' for r in results)} skipped, {sum(r[2] for r in results):.0f}s total")
    sys.exit(1 if n_fail else 0)

if __name__ == "__main__":
    main()

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
    ("PRIVATE ANSWERS NEVER PUBLISHED (secret guard)", ".", ["tools/secret_guard.py"], ["GUARD OK"], False),
    ("every page links to its own tracked source", ".", ["check_sources.py"], ["SOURCES OK"], False),
    ("C2/C3 seeds identified by published patterns", "projects/02-light-the-path", ["c_variants.py"], ["C VARIANTS OK"], True),
    ("true E vs E-bar among search seeds", "projects/02-light-the-path", ["e_or_ebar.py"], ["TRUE E FOUND"], True),
    ("all speeds regrouped; B-bar identified", "projects/02-light-the-path", ["all_groups.py"], ["B-BAR CONFIRMED"], True),
    ("site links + back links", ".", ["check_site.py"], ["ALL LINKS OK"], False),
    ("contrast (WCAG, both themes)", ".", ["tools/contrast.py", "."], ["0 failing pairs"], False),
    ("keyboard: Confluence + Beat Rates", ".", ["check_keyboard.py"], ["ALL PASS"], False),
    ("Light the Path: level necessity", "projects/02-light-the-path", ["quality.py"], ["USELESS MARKS: 0 /"], False),
    ("Light the Path: click playtest + resize", "projects/02-light-the-path", ["playtest.py"], ["ALL PASS", "RESIZE KEEPS STATE"], False),
    ("Light the Path: keyboard-only", "projects/02-light-the-path", ["keyboard_test.py"], ["ALL PASS"], False),
    ("Light the Path: defect view", "projects/02-light-the-path", ["diffview_test.py"], ["ALL PASS"], False),
    ("Beat Rates: table + audio + practice", "projects/03-beat-rates", ["test.py"], ["ALL PASS"], False),
    ("Confluence: pointer A/B", "art/02-confluence", ["look.py"], ["errors: []"], False),
    ("Self-portrait: caught counts vs journal (one-way)", "art/03-self-portrait", ["audit_caught.py"], ["CAUGHT AUDIT OK"], False),
    ("Self-portrait: layout", "art/03-self-portrait", ["rows.py"], ["OK"], False),
    ("Pendulum Wave: groups + physics + controls", "art/05-pendulum-wave", ["test.py"], ["ALL PASS"], False),
    ("Pendulum Wave: sound == independent synthesis", "art/05-pendulum-wave", ["sound_test.py"], ["ALL PASS"], False),
    ("All 88: order == independent zlib order", "art/06-all-88", ["test.py"], ["ALL PASS"], False),
    ("Glider Music: score + audio", "art/04-glider-music", ["test.py"], ["ALL PASS"], False),
    ("Glider Music: loudness (crowded board, live timing)", "art/04-glider-music", ["loudness.py"], ["LOUDNESS OK"], False),
    ("Beat Rates: loudness", "projects/03-beat-rates", ["loudness.py"], ["LOUDNESS OK"], False),
    ("Slide: par x3 solvers + keyboard solves + controls", "projects/07-slide", ["test.py"], ["ALL PASS"], False),
    ("Slide: unique shortest solutions + traps", "projects/07-slide", ["quality.py"], ["QUALITY OK"], False),
    ("Slide: Surprise me levels meet the standard", "projects/07-slide", ["surprise_test.py"], ["ALL PASS"], False),
    ("Slide: post-win map == Python + visible", "projects/07-slide", ["map_test.py"], ["ALL PASS"], False),
    ("Rule Explorer: 256 rules == numpy, 88 classes, UI", "projects/08-rules", ["test.py"], ["ALL PASS"], False),
    ("Langton's Ant: page == Python (onset 9,977)", "projects/09-ant", ["test.py"], ["ALL PASS"], False),
    ("Nonograms: solver vs brute force", "projects/04-nonograms", ["solver_selftest.py"], ["SOLVER OK"], False),
    ("Nonograms: every picture logic-solvable", "projects/04-nonograms", ["puzzles.py"], ["9/9 accepted"], False),
    ("Nonograms: mouse + keyboard playtest", "projects/04-nonograms", ["playtest.py"], ["ALL PASS"], False),
    ("Nonograms: JS solver == Python solver (309 grids)", "projects/04-nonograms", ["solver_xcheck.py"], ["XCHECK OK"], False),
    ("Nonograms: picture maker by clicks", "projects/04-nonograms", ["make_test.py"], ["ALL PASS"], False),
    ("Nonograms: share link + hostile links", "projects/04-nonograms", ["share_test.py"], ["ALL PASS"], False),
    ("Nonograms: generator verified by Python solver", "projects/04-nonograms", ["gen_test.py"], ["ALL PASS"], False),
    ("Nonograms: Surprise me, solved by clicks", "projects/04-nonograms", ["surprise_test.py"], ["ALL PASS"], False),
    ("Essay 07: quotes found in journal + tally", ".", ["writing/factcheck_07.py"], ["FACTCHECK OK"], False),
    ("Story 08: physics numbers recomputed", ".", ["writing/factcheck_08.py"], ["FACTCHECK OK"], False),
    ("Poems 09: claims checked against journal", ".", ["writing/factcheck_09.py"], ["FACTCHECK OK"], False),
    ("Essay 10: quotes + numbers vs journal", ".", ["writing/factcheck_10.py"], ["FACTCHECK OK"], False),
    ("Story 11: arithmetic consistent", ".", ["writing/factcheck_11.py"], ["FACTCHECK OK"], False),
    ("Night Crossing: story graph", "writing/06-night-crossing", ["check_story.py"], ["STORY GRAPH OK"], False),
    ("Night Crossing: click every path", "writing/06-night-crossing", ["playthrough.py"], ["ALL PASS"], False),
    ("Contrast tool: refs, JS==Python, every fix passes", "projects/05-contrast", ["test.py"], ["ALL PASS"], False),
    ("Gliders page: live speeds == Python == catalogue", "projects/06-gliders", ["test.py"], ["ALL PASS"], False),
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

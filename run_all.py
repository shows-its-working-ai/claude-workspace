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
    ("Ant: 100 random starts all reach a highway", "projects/09-ant", ["random_starts.py"], ["CONTROL empty grid: 9977 OK", "100/100"], True),
    ("Ant survey: all 22 multi-colour rules", "art/07-ant-gallery", ["survey.py"], ["SURVEY DONE", "counting distinct behaviours FAILED (2)"], True),
    ("no blank canvases (as displayed, every page)", ".", ["check_canvases.py"], ["CANVASES OK"], False),
    ("tap targets >= 24 px at phone width (WCAG 2.5.8)", ".", ["tools/check_targets.py"], ["CONTROLS OK", "TARGETS OK"], False),
    ("no page freezes over 250 ms while loading", ".", ["tools/check_freezes.py", "--limit", "250"], ["CONTROLS OK", "FREEZES OK"], False),
    ("mutation run: every planted bug is caught", ".", ["tools/mutate.py"], ["MUTATION RUN DONE", " 0 survived"], True),
    ("Lights Out: rank 23, 1/4 solvable, 4 solutions each (brute force 2^25)", "projects/11-lights-out", ["lights.py"], ["PREDICTION HELD"], True),
    ("Lights Out: n x n nullity vs OEIS A075462", "projects/11-lights-out", ["sizes.py"], ["SIZES OK"], False),
    ("Quiet patterns: symmetric ones exist for every deficient n", "art/08-quiet-patterns", ["quiet.py"], ["PREDICTION HELD"], True),
    ("Quiet patterns: no chiral ones on a bounded board (n <= 100), torus control finds them", "art/08-quiet-patterns", ["chiral.py"], ["cross-checks OK", "chiral sizes: none", "TORUS CONTROL OK"], False),
    ("Quiet patterns on rectangles: half-turn-only ones exist (3x5 first), torus control", "art/08-quiet-patterns", ["rect.py"], ["half-turn-only (chiral) rectangles: [(3, 5, 3, 2), (3, 17,", "TORUS CONTROL OK"], False),
    ("Quiet patterns: polynomial model == solver on all 820 boards up to 40x40", "art/08-quiet-patterns", ["algebra.py"], ["q_k(T_k) == J_k verified", "820 boards compared; mismatches: none", "PREDICTION HELD"], False),
    ("Quiet patterns: chirality == leading-term cancellation at a prime (all 293 boards)", "art/08-quiet-patterns", ["valuations.py"], ["293 boards", "VALUATIONS OK"], False),
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
    ("Self-portrait: build (prediction labels count only at line start)", "art/03-self-portrait", ["build.py"], ["built:"], False),
    ("Pendulum Wave: groups + physics + controls", "art/05-pendulum-wave", ["test.py"], ["ALL PASS"], False),
    ("Pendulum Wave: sound == independent synthesis", "art/05-pendulum-wave", ["sound_test.py"], ["ALL PASS"], False),
    ("All 88: order == independent zlib order", "art/06-all-88", ["test.py"], ["ALL PASS"], False),
    ("Eleven Ants: page highways == Python survey", "art/07-ant-gallery", ["test.py"], ["ALL PASS"], False),
    ("Quiet Patterns: page == Python, every pattern quiet", "art/08-quiet-patterns", ["test.py"], ["ALL PASS"], False),
    ("Blue Line: rows == Python, schedule, audio level", "art/09-blue-line", ["test.py"], ["ALL PASS"], False),
    ("Nim: Bouton XOR rule == brute force (1,808 positions)", "projects/16-nim", ["nim.py"], ["disagreements: 0", "PREDICTION HELD"], False),
    ("Wythoff: losing positions == golden-ratio Beatty pairs (heaps <= 300)", "projects/16-nim", ["wythoff.py"], ["brute force 229, formula 229", "PREDICTION HELD"], False),
    ("Corner the Queen: safe squares == brute force, perfect replies, won by taps", "projects/17-queen", ["test.py"], ["ALL PASS"], False),
    ("Nim: perfect replies, XOR strategy wins by taps", "projects/16-nim", ["test.py"], ["ALL PASS"], False),
    ("Weave: drafts (plain = checkerboard, twill balanced, houndstooth period 8)", "art/13-weave", ["weave.py"], ["PREDICTION HELD", "checkerboard: True"], False),
    ("Weave: page == Python crossing for crossing", "art/13-weave", ["test.py"], ["ALL PASS"], False),
    ("Pegs: every start solvable; 13,935 one-peg positions (Python)", "projects/15-pegs", ["pegs.py"], ["13935 of 32767", "PREDICTION HELD"], False),
    ("Pegs: solvability == Python on all boards, every start won by taps", "projects/15-pegs", ["test.py"], ["ALL PASS"], False),
    ("Sandpile: order-independence, symmetry, conservation (Python)", "art/12-sandpile", ["sandpile.py"], ["PREDICTION HELD"], False),
    ("Sandpile: page == Python cell for cell, grains kept", "art/12-sandpile", ["test.py"], ["ALL PASS"], False),
    ("Knight's tours: 1728 on 5x5, none on 2-4", "projects/14-knights-tour", ["tours.py"], ["5x5: 1728 directed open tours", "PREDICTION HELD"], False),
    ("Knight's Tour: finishable == counts, tour by clicks, stuck, parity", "projects/14-knights-tour", ["test.py"], ["ALL PASS"], False),
    ("Window: rain sound audible, no clipping; sound toggle", "art/10-window", ["test.py"], ["ALL PASS"], False),
    ("Never Repeats: Penrose counts -> golden ratio, area kept", "art/11-penrose", ["penrose.py"], ["area kept at every generation: True", "PREDICTION HELD"], False),
    ("Never Repeats: page counts == Python, area kept, honest labels", "art/11-penrose", ["test.py"], ["ALL PASS"], False),
    ("Penrose vertex kinds: 7 (geometric), every interior angle sum 360", "art/11-penrose", ["vertices.py"], ["angle sums not 360: 0", "distinct vertex kinds: 7"], False),
    ("Ring Your Bell: rows == Python, scorer, robot ringer on time / 100 ms late", "projects/13-ring-your-bell", ["test.py"], ["ALL PASS"], False),
    ("Ring the Changes: rules == Python, every rule-mode extent wins by clicks", "projects/12-ring-the-changes", ["test.py"], ["ALL PASS"], True),
    ("Four-bell extents: 10,792 in all, 24 with no long places, 2 essentially different", "art/09-blue-line", ["extents.py"], ["extents from rounds (direction counted): 10792", "with no long places: 24", "Plain Bob Minimus found: True | has no long places: True", "essentially different: 2:", "repeat an 8-change lead: True"], True),
    ("Four-bell extents, independent DP count agrees (10,792 and 24)", "art/09-blue-line", ["extents_dp.py"], ["all extents from rounds: 10792", "no long places: 24", "AGREES WITH CYCLE 112"], False),
    ("Glider Music: score + audio", "art/04-glider-music", ["test.py"], ["ALL PASS"], False),
    ("Glider Music: loudness (crowded board, live timing)", "art/04-glider-music", ["loudness.py"], ["LOUDNESS OK"], False),
    ("Beat Rates: loudness", "projects/03-beat-rates", ["loudness.py"], ["LOUDNESS OK"], False),
    ("Slide: par x3 solvers + keyboard solves + controls", "projects/07-slide", ["test.py"], ["ALL PASS"], False),
    ("Slide: unique shortest solutions + traps", "projects/07-slide", ["quality.py"], ["QUALITY OK"], False),
    ("Slide: Surprise me levels meet the standard", "projects/07-slide", ["surprise_test.py"], ["ALL PASS"], False),
    ("Slide: post-win map == Python + visible", "projects/07-slide", ["map_test.py"], ["ALL PASS"], False),
    ("Rule Explorer: 256 rules == numpy, 88 classes, UI", "projects/08-rules", ["test.py"], ["ALL PASS"], False),
    ("Langton's Ant: page == Python (onset 9,977)", "projects/09-ant", ["test.py"], ["ALL PASS"], False),
    ("Ant colours: symmetry indicator == Python", "projects/09-ant", ["sym_test.py"], ["ALL PASS"], False),
    ("Ant Golf: par == browser search; clicks win", "projects/10-ant-golf", ["test.py"], ["ALL PASS"], False),
    ("Slide: daily level (365 days, all distinct, all meet the standard)", "projects/07-slide", ["daily_test.py"], ["ALL PASS"], False),
    ("Slide: #daily link + spoiler-free share of a daily result", "projects/07-slide", ["share_test.py"], ["ALL PASS"], False),
    ("Lights Out: page solver == Python; every level cleared in par", "projects/11-lights-out", ["test.py"], ["ALL PASS"], False),
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
    ("Essay 12: quotes in the right cycle sections", ".", ["writing/factcheck_12.py"], ["FACTCHECK OK"], False),
    ("Story 13: numbers consistent (outage >= 6 min)", ".", ["writing/factcheck_13.py"], ["FACTCHECK OK"], False),
    ("Story 15: ringing recomputed from place notation", ".", ["writing/factcheck_15.py"], ["FACTCHECK OK"], False),
    ("Essay 20: quotes in the right cycles, six sound pages, pages state the limit", ".", ["writing/factcheck_20.py"], ["FACTCHECK OK"], False),
    ("Essay 14: every number recomputed from the records", ".", ["writing/factcheck_14.py"], ["FACTCHECK OK"], False),
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
    # cycle 124: checks run in parallel (--jobs N, default 4), each browser test in a throwaway profile.
    import os
    from concurrent.futures import ThreadPoolExecutor
    jobs = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--jobs=")), "4"))
    env = {**os.environ, "CW_EPHEMERAL": "1", **({"CW_QUICK": "1"} if quick else {})}   # cycle 146: quick -> changed pages only
    def run(check):
        name, cwd, cmd, markers, slow = check
        if quick and slow: return (name, "SKIP", 0.0, "")
        t0 = time.time()
        p = subprocess.run([PY] + cmd, cwd=ROOT / cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
        out = p.stdout + p.stderr
        missing = [m for m in markers if m not in out]
        status = "PASS" if p.returncode == 0 and not missing else "FAIL"
        why = "" if status == "PASS" else (f"exit {p.returncode}; missing {missing}; tail: " + out.strip()[-300:].replace("\n", " | "))
        r = (name, status, time.time() - t0, why)
        if status != "SKIP": print(f"{status:4s} {r[2]:6.1f}s  {name}" + (f"\n      {why}" if why else ""), flush=True)
        return r
    t_wall = time.time()
    # the mutation run EDITS other projects' files while it works, so it must never overlap another check: run it alone,
    # after the pool. (Running it in parallel would make innocent checks fail, or worse, pass against a mutant.)
    # cycle 142: timing checks also run alone: under a 4-way CPU contention Gliders read 318 ms vs 185 ms alone
    alone = [c for c in CHECKS if "tools/mutate.py" in c[2] or "tools/check_freezes.py" in c[2]]
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        pooled = dict(zip([c[0] for c in CHECKS if c not in alone], ex.map(run, [c for c in CHECKS if c not in alone])))
    pooled.update({c[0]: run(c) for c in alone})
    results = [pooled[c[0]] for c in CHECKS]          # report in CHECKS order
    print(f"wall clock {time.time() - t_wall:.0f}s with {jobs} workers")
    for f in ROOT.rglob("*.png"):           # tests leave screenshots; keep only deliberate keepsakes
        if "favourite_" not in f.name and "tools" not in f.parts:
            f.unlink()
    n_fail = sum(r[1] == "FAIL" for r in results)
    if n_fail:   # cycle 90: name the failures at the END too, so a truncated tail can't hide which one it was
        print()
        print("FAILED CHECKS: " + "; ".join(r[0] for r in results if r[1] == "FAIL"))
        for r in results:   # cycle 109: a one-off failure's REASON was lost to truncation; repeat it at the end
            if r[1] == "FAIL": print(f"  WHY {r[0]}: {r[3]}")
    print(f"\n{sum(r[1] == 'PASS' for r in results)} passed, {n_fail} failed, "
          f"{sum(r[1] == 'SKIP' for r in results)} skipped, {sum(r[2] for r in results):.0f}s total")
    sys.exit(1 if n_fail else 0)

if __name__ == "__main__":
    main()

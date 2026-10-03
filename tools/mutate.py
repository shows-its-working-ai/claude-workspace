"""Mutation runner (cycle 94). Essay 12: a passing check proves little until you break the thing on purpose.
For each mutation: (1) the anchor must occur exactly once, (2) apply it and CONFIRM the file changed, (3) run the named
check exactly as run_all.py does, (4) the check must FAIL, (5) restore the original bytes and confirm they're identical.
A mutation the check doesn't catch is a SURVIVOR: a blind spot in that check.
Prediction (written first): at least one of my existing checks will NOT catch its mutation.
Usage: mutate.py [substring of a mutation label to run only some]"""
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from run_all import CHECKS, PY

# (label, file, find, replace, check name in run_all.CHECKS)
MUTATIONS = [
    ("pendulum: frequencies 51+k -> 52+k", "art/05-pendulum-wave/index.html",
     "const freq = k => (51 + k) / PERIOD;", "const freq = k => (52 + k) / PERIOD;", "Pendulum Wave: groups + physics + controls"),
    ("pendulum sound: gain 0.06 -> 0.09 (50% louder)", "art/05-pendulum-wave/index.html",
     "const VOICE = {gain: 0.06,", "const VOICE = {gain: 0.09,", "Pendulum Wave: sound == independent synthesis"),
    ("rule explorer: mirror() returns the rule unchanged", "projects/08-rules/index.html",
     "m |= bit(r, n) << (4 * c + 2 * b + a);", "m |= bit(r, n) << (4 * a + 2 * b + c);", "Rule Explorer: 256 rules == numpy, 88 classes, UI"),
    ("slide: rocks don't stop the slide", "projects/07-slide/index.html",
     "grid[r + dr][c + dc] !== '#'", "grid[r + dr][c + dc] !== 'X'", "Slide: par x3 solvers + keyboard solves + controls"),
    ("ant: turns reversed", "projects/09-ant/index.html",
     "d = (d + (right ? 1 : 3)) % 4", "d = (d + (right ? 3 : 1)) % 4", "Langton's Ant: page == Python (onset 9,977)"),
    ("ant golf: black cells turn right instead of left", "projects/10-ant-golf/index.html",
     "if (b.has(k)){ d = (d + 3) % 4;", "if (b.has(k)){ d = (d + 1) % 4;", "Ant Golf: par == browser search; clicks win"),
    ("contrast: green weight 0.7152 -> 0.7", "projects/05-contrast/index.html",
     "0.7152 * ch(g)", "0.7 * ch(g)", "Contrast tool: refs, JS==Python, every fix passes"),
    ("all 88: sorted most-compressible first", "art/06-all-88/index.html",
     "items.sort((a, b) => b.size - a.size || a.r - b.r);", "items.sort((a, b) => a.size - b.size || a.r - b.r);", "All 88: order == independent zlib order"),
    # (cycle 94: "window 6000 -> 600" survived but changed nothing visible: an equivalent mutant, not a blind spot)
    ("eleven ants: highway search only up to period 50", "art/07-ant-gallery/index.html",
     "function highway(rule, steps = 50000, win = 6000, pmax = 2000)", "function highway(rule, steps = 50000, win = 6000, pmax = 50)",
     "Eleven Ants: page highways == Python survey"),
    ("gliders page: G seed 18 -> 19", "projects/06-gliders/index.html",
     "{name: 'G', seed: [2, 18]", "{name: 'G', seed: [2, 19]", "Gliders page: live speeds == Python == catalogue"),
    ("essay 10: 1,735 seeds -> 1,753", "writing/10-what-the-summary-hid.md",
     "1,735 seeds made a glider", "1,753 seeds made a glider", "Essay 10: quotes + numbers vs journal"),
    ("story 08: seconds pendulum 99.4 cm -> 98.4 cm", "writing/08-the-rating-nut.md",
     "**99.4 cm**", "**98.4 cm**", "Story 08: physics numbers recomputed"),
    # --- cycle 95: six more checks ---
    ("night crossing: a choice points at a scene that doesn't exist", "writing/06-night-crossing/story.json",
     '["Try to sleep again", "sleep"]', '["Try to sleep again", "slep"]', "Night Crossing: story graph"),
    ("all 88: panels never draw their cells", "art/06-all-88/index.html",
     "row.forEach((v, x) => { if (v) ctx.fillRect(x, t, 1, 1); })", "row.forEach((v, x) => { if (v && false) ctx.fillRect(x, t, 1, 1); })",
     "no blank canvases (as displayed, every page)"),
    ("slide: source link points at a folder that doesn't exist", "projects/07-slide/index.html",
     "tree/main/projects/07-slide", "tree/main/projects/07-slider", "every page links to its own tracked source"),
    ("self-portrait: cycle 94's caught count typed as 0", "art/03-self-portrait/data.json",
     '   94,\n   "tool",\n   3,', '   94,\n   "tool",\n   0,', "Self-portrait: caught counts vs journal (one-way)"),
    ("ant colours: symmetry never reported", "projects/09-ant/index.html",
     "if (cnt < 100) return null;", "if (cnt < 100000) return null;", "Ant colours: symmetry indicator == Python"),
    ("slide: muted text made too pale to read", "projects/07-slide/index.html",
     "--muted:#5f5d57", "--muted:#c9c6bd", "contrast (WCAG, both themes)"),
]

def run_check(name):
    spec = next(c for c in CHECKS if c[0] == name)
    _, cwd, cmd, markers, _ = spec
    p = subprocess.run([PY] + cmd, cwd=ROOT / cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = p.stdout + p.stderr
    return p.returncode == 0 and all(m in out for m in markers)

only = sys.argv[1:]
caught, survivors, broken = [], [], []
for label, f, find, repl, check in MUTATIONS:
    if only and not any(o in label for o in only): continue
    path = ROOT / f; orig = path.read_bytes(); text = orig.decode("utf-8")
    if text.count(find) == 0 and "\n" in find and text.count(find.replace("\n", "\r\n")) == 1:
        find, repl = find.replace("\n", "\r\n"), repl.replace("\n", "\r\n")   # cycle 95: files with CRLF on disk
    if text.count(find) != 1:
        broken.append(label); print(f"ANCHOR MISSING ({text.count(find)}x)  {label}"); continue
    path.write_bytes(text.replace(find, repl).encode("utf-8"))
    try:
        assert path.read_bytes() != orig, "mutation did not change the file"
        passed = run_check(check)
    finally:
        path.write_bytes(orig)
    assert path.read_bytes() == orig, f"RESTORE FAILED for {f}"
    (survivors if passed else caught).append(label)
    print(f"{'SURVIVED' if passed else 'caught  '}  {label}   [{check}]", flush=True)
print(f"\n{len(caught)} caught, {len(survivors)} survived, {len(broken)} anchors missing")
if survivors: print("SURVIVORS (blind spots):", survivors)
print("MUTATION RUN DONE")

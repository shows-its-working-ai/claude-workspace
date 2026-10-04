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
     # cycle 178: cycle 144 replaced fillRect with a pixel buffer, so the old anchor vanished; plant it in the new code
     "    ctx.putImageData(img, 0, 0);", "",
     "no blank canvases (as displayed, every page)"),
    ("slide: source link points at a folder that doesn't exist", "projects/07-slide/index.html",
     "tree/main/projects/07-slide", "tree/main/projects/07-slider", "every page links to its own tracked source"),
    ("self-portrait: cycle 94's caught count typed as 0", "art/03-self-portrait/data.json",
     '   94,\n   "tool",\n   3,', '   94,\n   "tool",\n   0,', "Self-portrait: caught counts vs journal (one-way)"),
    ("ant colours: symmetry never reported", "projects/09-ant/index.html",
     "if (cnt < 100) return null;", "if (cnt < 100000) return null;", "Ant colours: symmetry indicator == Python"),
    ("slide: muted text made too pale to read", "projects/07-slide/index.html",
     "--muted:#5f5d57", "--muted:#c9c6bd", "contrast (WCAG, both themes)"),
    ("slide daily: the seed ignores the day (same level all month)", "projects/07-slide/index.html",
     "generate(y * 10000 + m * 100 + d)", "generate(y * 10000 + m * 100)", "Slide: daily level (365 days, all distinct, all meet the standard)"),
    ("lights out: a press also flips the diagonal neighbour", "projects/11-lights-out/index.html",
     "[[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1]]", "[[0, 0], [1, 0], [-1, 0], [0, 1], [1, 1]]",
     "Lights Out: page solver == Python; every level cleared in par"),
    ("essay 14: first-half mistake count 46 -> 47", "writing/14-a-hundred-cycles.md",
     "they caught 46", "they caught 47", "Essay 14: every number recomputed from the records"),
    # (cycle 103: "only the 4 rotations" survived but changed NOTHING: for these sizes every rotation-symmetric quiet
    #  pattern is also mirror-symmetric -- an equivalent mutant, and a fact worth noting. Replaced with an observable one.)
    # cycle 178: since cycle 141 the candidates come from symmetricBasis (symmetric by construction), so weakening the
    # one-by-one recheck to two mirrors changed nothing and survived: another equivalent mutant. Plant it where the
    # work now happens: the basis loses vectors, so symmetric patterns go missing.
    ("quiet patterns: symmetric basis keeps only its first vector", "art/08-quiet-patterns/index.html",
     "    if (!v) basis.push(pr);\n  }\n  return basis;\n}\nfunction toggles",               # 2 copies; this is symmetricBasis's
     "    if (!v && !basis.length) basis.push(pr);\n  }\n  return basis;\n}\nfunction toggles",
     "Quiet Patterns: page == Python, every pattern quiet"),
    ("chiral: rotation generator replaced by a transpose", "art/08-quiet-patterns/chiral.py",
     "rot = lambda r, c: (c, n - 1 - r)", "rot = lambda r, c: (c, r)",
     "Quiet patterns: no chiral ones on a bounded board (n <= 100), torus control finds them"),
    ("rect: half-turn replaced by a mirror", "art/08-quiet-patterns/rect.py",
     "HALF = lambda m, n, r, c: (m - 1 - r, n - 1 - c)", "HALF = lambda m, n, r, c: (r, n - 1 - c)",
     "Quiet patterns on rectangles: half-turn-only ones exist (3x5 first), torus control"),
    ("algebra: up-down mirror uses q_m(s) instead of q_m(s+1)", "art/08-quiet-patterns/algebra.py",
     "qm, qn = shift(q(m)), q(n)", "qm, qn = q(m), q(n)",
     "Quiet patterns: polynomial model == solver on all 820 boards up to 40x40"),
    ("valuations: cancellation test also counts equal valuations", "art/08-quiet-patterns/valuations.py",
     "val(u, p, e) == val(v, p, e) < val(u ^ v, p, e)", "val(u, p, e) == val(v, p, e) <= val(u ^ v, p, e)",
     "Quiet patterns: chirality == leading-term cancellation at a prime (all 293 boards)"),
    ("story 15: the kink sends the third DOWN (the error I first wrote)", "writing/15-the-extent.md",
     "hunting up, and the two at the back dodge", "hunting down, and the two at the back dodge",
     "Story 15: ringing recomputed from place notation"),
    ("blue line: swaps step one place instead of two", "art/09-blue-line/index.html",
     "[r[i], r[i + 1]] = [r[i + 1], r[i]]; i += 2;", "[r[i], r[i + 1]] = [r[i + 1], r[i]]; i += 1;",
     "Blue Line: rows == Python, schedule, audio level"),
    ("extents DP: the x change becomes a second 12", "art/09-blue-line/extents_dp.py",
     "(0, 1, 3, 2), (1, 0, 3, 2)]", "(0, 1, 3, 2), (1, 0, 2, 3)]",
     "Four-bell extents, independent DP count agrees (10,792 and 24)"),
    ("ant golf: phone board widening removed (cells back to 23 px)", "projects/10-ant-golf/index.html",
     "@media (max-width:420px){#board{margin:0 -12px}}", "@media (max-width:420px){#board{}}",
     "tap targets >= 24 px at phone width (WCAG 2.5.8)"),
    ("targets: inline rule back to cycle 120's (any other text)", "tools/check_targets.py",
     "(rest.match(/[A-Za-z]{2,}/g) || []).length >= 3", "ctx.length > own.length + 3",
     "tap targets >= 24 px at phone width (WCAG 2.5.8)"),
    ("slide: share text leaks the route (positions)", "projects/07-slide/index.html",
     "solved in ${moves}${mark}\\n", "solved in ${moves}${mark} ${hist.map(String).join('|')}\\n",
     "Slide: #daily link + spoiler-free share of a daily result"),
    ("penrose vertices: rim vertices let in", "art/11-penrose/vertices.py",
     "if math.hypot(*v) > inner: continue", "if math.hypot(*v) > 2: continue",
     "Penrose vertex kinds: 7 (geometric), every interior angle sum 360"),
    ("penrose page: corner ring read in triangle order, not angular order", "art/11-penrose/index.html",
     "const seq = c.sort((x, y) => x[0] - y[0]).map(x => x[1])", "const seq = c.map(x => x[1])",
     "Never Repeats: page counts == Python, area kept, honest labels"),
    ("knight's tour: colour-parity check removed", "projects/14-knights-tour/index.html",
     "  if (opp !== Math.ceil((opp + same) / 2) || same !== Math.floor((opp + same) / 2)) return false;", "",
     "Knight's Tour: finishable == counts, tour by clicks, stuck, parity"),
    ("sandpile: a toppling square forgets its southern neighbour", "art/12-sandpile/index.html",
     "h[i - size] += k; h[i + size] += k;", "h[i - size] += k;",
     "Sandpile: page == Python cell for cell, grains kept"),
    ("garden: diagonal moves forgotten in the mex", "art/14-wythoff/index.html",
     "  for (let k = 1; k <= Math.min(a, b); k++) seen[g[a - k][b - k]] = 1;", "",
     "Wythoff's Garden: page Grundy values == Python"),
    ("one stroke: the rule allows four odd points", "projects/21-stroke/index.html",
     "return {possible: odd.length === 0 || odd.length === 2, odd};", "return {possible: odd.length <= 4, odd};",
     "One Stroke: every figure's verdict == brute force; drawn or stuck by clicks"),
    ("hex: solver forgets to negate the opponent's answer", "projects/20-hex/index.html",
     "    b[i] = who; res = wins(b, who) || !canWin(b, 3 - who); b[i] = 0;", "    b[i] = who; res = wins(b, who) || canWin(b, 3 - who); b[i] = 0;",
     "Small Hex: verdicts == Python, games won/lost as solved, first move < 300 ms"),
    ("ant: on a dark square it turns right too", "art/18-ant/index.html",
     "if (black.has(k)){ d = (d + 3) % 4;", "if (black.has(k)){ d = (d + 1) % 4;",
     "The Ant: page grid == Python square for square; highway message at 9,977"),
    ("eight: hint takes any legal move, not a shortest one", "projects/19-eight/index.html",
     "dist.get(+slide(st, j)) === d - 1);", "dist.get(+slide(st, j)) !== undefined);",
     "Eight: page distances == Python, hardest solved in 31 by hints"),
    ("dragon: the mirrored half isn't flipped", "art/17-dragon/index.html",
     "[...s].reverse().map(c => c === 'L' ? 'R' : 'L').join('')", "[...s].reverse().join('')",
     "Paper Dragon: creases + corner counts == Python"),
    ("code breaker: solver forgets to prefer guesses that could be the code", "projects/18-mastermind/index.html",
     "const key = [worst, inC.has(g) ? 0 : 1, g];", "const key = [worst, 0, g];",
     "Code Breaker: page solver == Python on every code, won and lost by clicks, reverse mode + slips"),
    ("code breaker reverse: contradictory answers never noticed", "projects/18-mastermind/index.html",
     "  if (!rc.length){", "  if (false){",
     "Code Breaker: page solver == Python on every code, won and lost by clicks, reverse mode + slips"),
    ("against: the high drum's beats never scheduled", "art/16-against/index.html",
     "    for (let j = 0; j < q; j++) hit(ac, t0 + j * LOOP / q, false); }", "    }",
     "Against: merged rhythms == Python, beats counted in recordings"),
    # --- cycle 178: every writing fact-check gets a planted slip (9 had none) ---
    ("essay 07: a quoted figure 56 -> 65", "writing/07-the-scorecard.md",
     "391 -> **56**", "391 -> **65**", "Essay 07: quotes found in journal + tally"),
    ("poems 09: 30 steps -> 31", "writing/09-three-corrections.md",
     "moves 8 cells left every 30 steps", "moves 8 cells left every 31 steps", "Poems 09: claims checked against journal"),
    ("story 11: 32 counted -> 33", "writing/11-the-count.md",
     "32 counted, so 32 − 28 = 4 extra", "33 counted, so 32 − 28 = 4 extra", "Story 11: arithmetic consistent"),
    ("essay 12: about fifty checks -> ninety", "writing/12-break-it-on-purpose.md",
     "There are about fifty of them now.", "There are about ninety of them now.", "Essay 12: quotes in the right cycle sections"),
    ("story 13: 12 flashes a minute -> 10", "writing/13-the-log.md",
     "so 12 flashes a minute", "so 10 flashes a minute", "Story 13: numbers consistent (outage >= 6 min)"),
    ("essay 20: six sound pages -> five", "writing/20-what-a-test-cant-hear.md",
     "When I wrote this I had made six things", "When I wrote this I had made five things",
     "Essay 20: quotes in the right cycles, six sound pages then, every sound page says can't hear"),
    ("story 24: the teacher's taps grouped wrong again", "writing/24-three-against-two.md",
     "finger. Tap. Tap-tap-tap.", "finger. Tap-tap. Tap-tap.", "Story 24: the rhythm, the hands and the taps == against.json's 3 against 2"),
    ("poems 25: 28,555 corners -> 28,565", "writing/25-folds.md",
     "28,555 times", "28,565 times", "Poems 25: every fold/crease/corner number == dragon.json"),
    ("essay 27: a quote softened", "writing/27-the-check-that-checks.md",
     'that was a yes, "so it proved nothing"', 'that was a yes, "so it proved little"',
     "Essay 27: five quotes in the right cycles; 'about a hundred'; 'only the last on purpose'"),
    ("rhythm: Bjorklund drops the leftover hits", "art/15-rhythm/index.html",
     "    b = a.length > m ? a.slice(m) : b.slice(m); a = na;", "    b = b.slice(m); a = na;",
     "Even Beats: page patterns == Python, 2k clicks per two loops"),
    ("queen: safe squares use phi^2 off by one", "projects/17-queen/index.html",
     "const lo = (n + isqrt(5 * n * n)) >> 1, hi = lo + n;", "const lo = (n + isqrt(5 * n * n)) >> 1, hi = lo + n + 1;",
     "Corner the Queen: safe squares == brute force, perfect replies, won by taps"),
    ("nim: opponent ignores the XOR rule", "projects/16-nim/index.html",
     "  if (x) for (let i = 0; i < h.length; i++){ const t = h[i] ^ x; if (t < h[i]) return [i, h[i] - t]; }", "",
     "Nim: perfect replies, XOR strategy wins by taps"),
    ("weave: warp/weft colours swapped at crossings", "art/13-weave/index.html",
     "row.map((v, c) => v ? d.warp[c % d.warp.length] : d.weft[r % d.weft.length])",
     "row.map((v, c) => v ? d.weft[r % d.weft.length] : d.warp[c % d.warp.length])",
     "Weave: page == Python crossing for crossing"),
    ("pegs: diagonal jumps forgotten", "projects/15-pegs/index.html",
     "const DIRS = [[0, 1], [0, -1], [1, 0], [-1, 0], [1, 1], [-1, -1]]", "const DIRS = [[0, 1], [0, -1], [1, 0], [-1, 0]]",
     "Pegs: solvability == Python on all boards, every start won by taps"),
    ("quiet patterns: back to trying all 2^k patterns (the 3.9 s freeze)", "art/08-quiet-patterns/index.html",
     "const sb = symmetricBasis(n, cols), d = sb.length;", "const sb = kern, d = k;",
     "no page freezes over 250 ms while loading"),
    ("freeze check: blind to blocking during load", "tools/check_freezes.py",
     "    window.__long.push(performance.now() - t0);", "",
     "no page freezes over 250 ms while loading"),
    # (cycle 178: retired "gliders: speed measurement back to rolled copies". With the old code put back the page now
    #  blocks only 97 ms (other speedups since cycle 142), so it no longer plants a freeze; the freeze check passing it
    #  was correct. The check's own built-in controls (a planted 400 ms block, caught) prove it can see a freeze.)
    ("sandpile: settle on the page again (no worker)", "art/12-sandpile/index.html",
     "  if (worker) worker.postMessage(want); else draw({N: want, ...settle(want)});",
     "  draw({N: want, ...settle(want)});",
     "Sandpile: page == Python cell for cell, grains kept"),
    ("portrait: prediction label matched anywhere (quotes count)", "art/03-self-portrait/build.py",
     r'PRED = re.compile(r"^(?:- )?\*\*(', r'PRED = re.compile(r"(?:- )?\*\*(',
     "Self-portrait: build (prediction labels count only at line start)"),
]

def run_check(name):
    spec = next(c for c in CHECKS if c[0] == name)
    _, cwd, cmd, markers, _ = spec
    p = subprocess.run([PY] + cmd, cwd=ROOT / cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = p.stdout + p.stderr
    return p.returncode == 0 and all(m in out for m in markers)

# cycle 145: a killed run left a mutant in place (Pegs, diagonal jumps removed). Before mutating, the original bytes go
# to INFLIGHT; they're removed after the restore. A leftover INFLIGHT means a run died mid-mutation: restore first.
import json, base64, time
INFLIGHT = ROOT / "tools" / ".mutate_inflight.json"
if INFLIGHT.exists():
    rec = json.loads(INFLIGHT.read_text(encoding="utf-8"))
    Path(rec["path"]).write_bytes(base64.b64decode(rec["orig"])); INFLIGHT.unlink()
    print(f"RESTORED a mutant left by an interrupted run: {rec['path']}")
only = sys.argv[1:]
caught, survivors, broken, _baseline = [], [], [], {}
# cycle 125: a check run against a MUTANT can rewrite data files (rect.py rewrote rect.json from a broken copy, and
# that corrupted file survived the run). Snapshot every tracked file's state now; after each mutation, put back any
# tracked file the check changed.
def _changed():
    out = subprocess.run(["git", "diff", "--name-only"], cwd=ROOT, capture_output=True, text=True).stdout
    return {l for l in out.split("\n") if l}
_dirty_at_start = {g: (ROOT / g).read_bytes() for g in _changed()}
def restore_side_effects():
    for g in _changed():
        if g in _dirty_at_start: (ROOT / g).write_bytes(_dirty_at_start[g])
        else: subprocess.run(["git", "checkout", "--", g], cwd=ROOT, check=True)
    left = {g for g in _changed() if g not in _dirty_at_start}
    assert not left, f"side effects not restored: {left}"
for label, f, find, repl, check in MUTATIONS:
    if only and not any(o in label for o in only): continue
    path = ROOT / f; orig = path.read_bytes(); text = orig.decode("utf-8")
    if text.count(find) == 0 and "\n" in find and text.count(find.replace("\n", "\r\n")) == 1:
        find, repl = find.replace("\n", "\r\n"), repl.replace("\n", "\r\n")   # cycle 95: files with CRLF on disk
    if text.count(find) != 1:
        broken.append(label); print(f"ANCHOR MISSING ({text.count(find)}x)  {label}"); continue
    # cycle 178: a check that fails on the UNmutated code "catches" every mutant (a syntax error in factcheck_13 did
    # exactly that). Require the clean baseline to pass first, once per check.
    if check not in _baseline:
        _baseline[check] = run_check(check); restore_side_effects()
    if not _baseline[check]:
        broken.append(label); print(f"BASELINE FAILS (check broken without any mutant)  {label}   [{check}]"); continue
    INFLIGHT.write_text(json.dumps({"path": str(path), "orig": base64.b64encode(orig).decode()}), encoding="utf-8")
    path.write_bytes(text.replace(find, repl).encode("utf-8"))
    try:
        assert path.read_bytes() != orig, "mutation did not change the file"
        passed = run_check(check)
    finally:
        path.write_bytes(orig)
        restore_side_effects()
    assert path.read_bytes() == orig, f"RESTORE FAILED for {f}"
    INFLIGHT.unlink(missing_ok=True)
    (survivors if passed else caught).append(label)
    print(f"{'SURVIVED' if passed else 'caught  '}  {label}   [{check}]", flush=True)
print(f"\n{len(caught)} caught, {len(survivors)} survived, {len(broken)} anchors missing or baselines failing")
if survivors: print("SURVIVORS (blind spots):", survivors)
# cycle 178: the full run takes ~20 min and --quick skips it, so it rotted unnoticed (2 survivors, 1 lost anchor).
# A complete, clean run leaves a timestamp; end_cycle nags when it is missing or old.
if not only and not survivors and not broken:
    (ROOT / "tools" / ".mutate_full_ok").write_text(str(time.time()), encoding="utf-8"); print("full run clean: timestamp written")
print("MUTATION RUN DONE")

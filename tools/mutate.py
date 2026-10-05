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
    ("story 43: the daughter born too late for a grandchild at school in 2011", "writing/43-the-coat.md",
     "**1981.** A pencil in the pocket", "**1989.** A pencil in the pocket",
     "Story 43: years run backwards; funeral after 2011; daughter's age works; the pockets add up, button elsewhere"),
    ("story 41: Hen misreads the second marrow", "writing/41-the-marrow.md",
     '"Eleven point nine," of the second.', '"Eleven point seven," of the second.',
     "Story 41: the marrows add up (12 - 0.2, 12 - 0.1; second wins); five judges named; no backwards 'denser'"),
    ("essay 40: seven of thirteen", "writing/40-eight-of-thirteen.md",
     "Of the last thirteen things in my games-and-puzzles folder, eight were the same thing", "Of the last thirteen things in my games-and-puzzles folder, seven were the same thing",
     "Essay 40: the eight solved-opponent games among the thirteen (at the essay's commit); 213's note + The Lock correction"),
    ("story 39: five pots in the bin", "writing/39-notes-on-the-fridge.md",
     "Four of them, and a spoon.", "Five of them, and a spoon.",
     "Story 39: the yoghurt count (4 -> 3, 2, 1, 0; four pots found, four lids)"),
    ("poems 38: 27 takes one step fewer", "writing/38-three-small-poems.md",
     "a hundred and eleven steps", "a hundred and ten steps",
     "Poems 38: 27's climb, 169 circles + my 120 guess, Sim's 112,096 positions == the programs"),
    ("essay 37: three of seven were a year off", "writing/37-a-year-off.md",
     "Five were right. Two were a year off.", "Four were right. Three were a year off.",
     "Essay 37: the three old quotes in git, the two fixed dates, journal 217's counts, the cited phrase"),
    ("story 36: Priya's first-draft count (forty-six)", "writing/36-the-museum-of-lost-property.md",
     '"Forty-four. And the hamster ball."', '"Forty-six. And the hamster ball."',
     "Story 36: the lost-property box adds up (41 + 3 = 44, and the hamster ball); nine claimed; the recorder stays"),
    ("essay 35: the desktop canvas was 14% smaller", "writing/35-the-bug-that-changed-nothing.md",
     "the picture was only 4% smaller, and a tap that's 4% off", "the picture was only 14% smaller, and a tap that's 14% off",
     "Essay 35: equivalent mutant + replacement in cycle 210's journal, page/mutate/test/apollo agree"),
    ("essay 33: three issues in ten minutes", "writing/33-twenty-minutes.md",
     "a reader opened three issues in twenty minutes.", "a reader opened three issues in ten minutes.",
     "Essay 33: issue times, reader's words, counts as of writing, the four found bugs == journal"),
    ("notakto: stale computer replies land on a new game", "projects/23-notakto/index.html",
     "if (g === gen && !over && turn !== human) play(choose(m));", "if (!over) play(choose(m));",
     "Nobody Wins Noughts: verdicts == Python (230), games won/lost as solved"),
    ("four boxes: stale computer moves land on a new game", "projects/24-boxes/index.html",
     "if (g === gen && !over && mover === 1) draw(bestMove(m));", "if (!over) draw(bestMove(m));",
     "Four Boxes: value == Python (4,096), games as solved, extra move kept"),
    ("ring your bell: a second Start stacks a second ringing", "projects/13-ring-your-bell/index.html",
     "  if (bus){ bus.gain.setValueAtTime(0, ac.currentTime); bus.disconnect(); live--; }", "",
     "Ring Your Bell: rows == Python, scorer, robot ringer on time / 100 ms late"),
    ("against: Stop leaves the scheduled loop ringing", "art/16-against/index.html",
     "clearInterval(timer); timer = null; cut(); cur = -1;", "clearInterval(timer); timer = null; cur = -1;",
     "Against: merged rhythms == Python, beats counted in recordings"),
    ("masher: Small Hex's New game button throws", "projects/20-hex/index.html",
     "$('new').onclick = () => start(1);", "$('new').onclick = () => { start(1); null.x; };",
     "Button masher: 60 random actions on every page, no JS errors, still responsive"),
    ("portrait: issue #3 back (all cycles squeezed onto one row)", "art/03-self-portrait/index.html",
     "repeat(25,minmax(0,1fr));gap:8px 6px", "repeat(var(--n),minmax(0,1fr));gap:clamp(2px,0.6vw,6px)",
     "Self-portrait: layout"),
    ("queen: issue #2 back ('computer starts' just replies to the current position)", "projects/17-queen/index.html",
     "  over = false; q = fresh(); start = q.slice(); q = reply(...q);", "  if (over) return; start = q.slice(); q = reply(...q);",
     "Corner the Queen: safe squares == brute force, perfect replies, won by taps"),
    ("blue line: issue #1 back (a new ringing doesn't stop the old one)", "art/09-blue-line/index.html",
     "  if (bus) return stopRinging();\n", "",
     "Blue Line: rows == Python, schedule, audio level"),
    ("shepard: loudness bell narrowed to 0.3 octave (pitch wobbles)", "art/22-shepard/index.html",
     "const LOW = 27.5, K = 8, S = 1.2,", "const LOW = 27.5, K = 8, S = 0.3,",
     "Endless Staircase: rendered audio periodic, shifts +/-1/8 oct per 1/8 cycle, steady pitch, no clipping"),
    ("four boxes: closing a box no longer earns another move", "projects/24-boxes/index.html",
     "sc[mover] += k; if (m === 4095) over = true; else if (!k) mover = 1 - mover;", "sc[mover] += k; if (m === 4095) over = true; else mover = 1 - mover;",
     "Four Boxes: value == Python (4,096), games as solved, extra move kept"),
    ("spirograph: bumps stated as ring/wheel without dividing by g", "art/21-spirograph/index.html",
     "return {R, r, g, trips: r / g, lobes: R / g,", "return {R, r, g, trips: r / g, lobes: R,",
     "Gear Drawing: stated trips/bumps == r/g, R/g; bumps counted from page points; closes on time"),
    ("chomp: a stale computer move lands on the new game", "projects/25-chomp/index.html",
     "draw(); if (compFirst){ const g = gen; setTimeout(() => { if (g === gen) computer(); }, 400); }", "draw(); if (compFirst){ setTimeout(() => computer(), 400); }",
     "Poisoned Chocolate: winning moves == Python (27 boards), won/lost by clicks, double computer-start, poison"),
    ("chomp: eating a square leaves the rows below it short too", "projects/25-chomp/index.html",
     "out.push([[r, c], pos.map((l, i) => i >= r ? Math.min(l, c) : l)", "out.push([[r, c], pos.map((l, i) => Math.min(l, c))",
     "Poisoned Chocolate: winning moves == Python (27 boards), won/lost by clicks, double computer-start, poison"),
    ("notakto: the diagonals don't count as lines", "projects/23-notakto/index.html",
     "const LINES = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];",
     "const LINES = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8]];",
     "Nobody Wins Noughts: verdicts == Python (230), games won/lost as solved"),
    ("truchet: the band painted the cap's colour", "art/20-truchet/index.html",
     "ctx.fillStyle = col(ty === 0 ? 1 - p : p); ctx.fillRect(x, y, s + 0.5, s + 0.5);", "ctx.fillStyle = col(ty === 0 ? p : 1 - p); ctx.fillRect(x, y, s + 0.5, s + 0.5);",
     "Two-Colour Tiles: every piece's pixel colour == region parity; tap turns one square"),
    ("hanoi map: the corner swap forgotten (long lines across the map)", "projects/22-hanoi/index.html",
     "const o = [0, 1, 2].filter(p => p !== s[d]); [perm[o[0]], perm[o[1]]] = [perm[o[1]], perm[o[0]]];", "",
     "Towers and Map: moves == Python, 3^n distinct dots, equal-length lines, solved in 2^n-1 by clicks"),
    ("front page: 'at random' counts the five-minute picks twice", "index.html",   # the BUILT page: the check reads it, nothing rebuilds it
     "  const all = [...new Set([...document.querySelectorAll('main h2 ~ p > a')].map(a => a.href))];", "  const all = [...document.querySelectorAll('main h2 ~ p > a')].map(a => a.href);",
     "Front page 'at random': each listed piece once, all real, real clicks land where Math.random says"),
    ("loops check: Ring Your Bell's stacked loops, seen by the SITE-WIDE check alone", "projects/13-ring-your-bell/index.html",
     "  if (!run || run !== mine) return;", "  if (!run) return;",
     "No stacked animation loops: every button pressed 3x on every animated page (control seen)"),
    ("ring your bell: a superseded frame loop keeps running (stacked loops)", "projects/13-ring-your-bell/index.html",
     "  if (!run || run !== mine) return;", "  if (!run) return;",
     "Ring Your Bell: rows == Python, scorer, robot ringer on time / 100 ms late"),
    # cycle 239 audit (the cycle-238 class: does any sound test check PITCH independently of the page?): each page
    # mistuned by a semitone, against its own sound test
    ("pitch audit: Pendulum Wave a semitone sharp", "art/05-pendulum-wave/index.html",
     "const pitch = k => 261.63 * 2 **", "const pitch = k => 277.18 * 2 **",
     "Pendulum Wave: sound == independent synthesis"),
    ("pitch audit: Blue Line's bells a semitone sharp", "art/09-blue-line/index.html",
     "const f0 = 440 * SCALE[stage - 1] / SCALE[bell - 1];", "const f0 = 466.16 * SCALE[stage - 1] / SCALE[bell - 1];",
     "Blue Line: rows == Python, schedule, audio level"),
    ("pitch audit: Ring Your Bell's bells a semitone sharp", "projects/13-ring-your-bell/index.html",
     "const f0 = 440 * SCALE[3] / SCALE[bell - 1];", "const f0 = 466.16 * SCALE[3] / SCALE[bell - 1];",
     "Ring Your Bell: rows == Python, scorer, robot ringer on time / 100 ms late"),
    ("pitch audit: Glider Music a semitone sharp", "art/04-glider-music/index.html",
     "return {freq: 220 * 2 ** (semis / 12),", "return {freq: 233.08 * 2 ** (semis / 12),",
     "Glider Music: score + audio"),
    ("pig: a 1 doesn't wipe the turn", "projects/32-pig/index.html",
     "lose the ${t} from this turn.`; t = 0; n++; }", "lose the ${t} from this turn.`; n++; }",
     "Push Your Luck: pinned dice by real clicks (sum, bust, bank, finish), note numbers == pig.py"),
    ("pig: the note misquotes hold-at-20's average", "projects/32-pig/index.html",
     "Played to 100, it takes 12.64 turns on average.", "Played to 100, it takes 12.46 turns on average.",
     "Push Your Luck: pinned dice by real clicks (sum, bust, bank, finish), note numbers == pig.py"),
    ("fox: the fox may stay where it is overnight", "projects/31-fox/index.html",
     ".flatMap(i => [i - 1, i + 1])", ".flatMap(i => [i - 1, i, i + 1])",
     "Find the Fox: night-step == Python (2,000), shortest plans by real clicks catch on the last day, hint exact"),
    ("fox: the 'best possible' is miscounted", "projects/31-fox/index.html",
     "const best = n === 1 ? 1 : n === 2 ? 2 : 2 * (n - 2);", "const best = n === 1 ? 1 : n === 2 ? 2 : 2 * (n - 1);",
     "Find the Fox: night-step == Python (2,000), shortest plans by real clicks catch on the last day, hint exact"),
    ("mirror sketch: copies spaced for one more than asked", "art/31-kaleido/index.html",
     "ctx.rotate(2 * Math.PI * k / s.n);", "ctx.rotate(2 * Math.PI * k / (s.n + 1));",
     "Mirror Sketch: real mouse/touch strokes are n-fold + mirror symmetric in pixels; mirror-off control; undo, save, no network"),
    ("mirror sketch: the Mirror button is ignored (always mirrored)", "art/31-kaleido/index.html",
     "for (const flip of s.mirror ? [1, -1] : [1]){", "for (const flip of [1, -1]){",
     "Mirror Sketch: real mouse/touch strokes are n-fold + mirror symmetric in pixels; mirror-off control; undo, save, no network"),
    ("chimes: the F-sharp chime is tuned to G", "art/30-chimes/index.html",
     "const NOTES = [587.33, 659.26, 739.99, 880.0, 987.77]", "const NOTES = [587.33, 659.26, 783.99, 880.0, 987.77]",
     "Wind Chimes: page audio FFT'd (each strike its note), strike rate grows with wind, deterministic, one bus, can't hear"),
    ("chimes: the wind doesn't matter", "art/30-chimes/index.html",
     "if (rand() < wind * wind * 0.08) out.push({t: k * TICK, i});", "if (rand() < 0.01) out.push({t: k * TICK, i});",
     "Wind Chimes: page audio FFT'd (each strike its note), strike rate grows with wind, deterministic, one bus, can't hear"),
    ("day: the stars never leave (they shine at noon)", "art/29-day/index.html",
     "const night = m => m <= 300 || m >= 1200 ? 1 : m < 360 ? (360 - m) / 60 : m > 1140 ? (m - 1140) / 60 : 0;", "const night = m => 1;",
     "A Day in a Minute: sky brightness + stars from pixels, deterministic per seed, pause, slider keys, reduced motion"),
    ("day: reduced-motion is ignored (the day plays anyway)", "art/29-day/index.html",
     "playing = !matchMedia('(prefers-reduced-motion: reduce)').matches,", "playing = true,",
     "A Day in a Minute: sky brightness + stars from pixels, deterministic per seed, pause, slider keys, reduced motion"),
    ("clock patience: Play it out never retires the old ticker", "projects/30-clock/index.html",
     "const tick = () => { if (g !== gen || over) return;", "const tick = () => { if (over) return;",
     "Clock Patience: logic == Python (3,000), real-click games end right, one ticker, piles never overlap"),
    ("clock patience: the game ends at the third king", "projects/30-clock/index.html",
     "if (r === 12 && ++kings === 4){ over = true;", "if (r === 12 && ++kings === 3){ over = true;",
     "Clock Patience: logic == Python (3,000), real-click games end right, one ticker, piles never overlap"),
    ("folded poem: the fold leaks (every line shown while folded)", "projects/29-folded/index.html",
     "$('last').textContent = last ? last.text : 'The paper is blank. You start.';", "$('last').textContent = last ? lines.map(l => l.text).join(' / ') : 'The paper is blank. You start.';",
     "Folded Poem: stays folded (no earlier line visible), unfolds in order, no network, typed HTML stays text, overlap ~ 0.3555"),
    ("folded poem: your line is inserted as HTML", "projects/29-folded/index.html",
     "const p = document.createElement('p'); p.textContent = l.text;", "const p = document.createElement('p'); p.innerHTML = l.text;",
     "Folded Poem: stays folded (no earlier line visible), unfolds in order, no network, typed HTML stays text, overlap ~ 0.3555"),
    ("skittles: the Grundy table forgets two-pin moves", "projects/28-kayles/index.html",
     "for (let n = 1; n < 200; n++){ const o = new Set(); for (const t of [1, 2])", "for (let n = 1; n < 200; n++){ const o = new Set(); for (const t of [1])",
     "Skittles: Grundy == Python, won by real clicks (one + two modes), bad opening loses, double start, phone"),
    ("skittles: a stale computer move lands on the new game", "projects/28-kayles/index.html",
     "function later(f){ const g = gen; setTimeout(() => { if (g === gen) f(); }, 450); }", "function later(f){ setTimeout(f, 450); }",
     "Skittles: Grundy == Python, won by real clicks (one + two modes), bad opening loses, double start, phone"),
    # cycle 229: my first mutant here ("count tips over half a turn") SURVIVED because it was EQUIVALENT: a negative-r
    # tip in [0, pi) lands at the direction of one in [pi, 2 pi), so half a turn already holds every tip (essay 35 again)
    ("rose lines: tips counted ignoring the sign of r", "art/28-maurer/index.html",
     "  for (let k = 0; k < 4 * n; k++){ const t = (2 * k + 1) * Math.PI / (2 * n), r = Math.sin(n * t);", "  for (let k = 0; k < 4 * n; k++){ const t = (2 * k + 1) * Math.PI / (2 * n), r = Math.abs(Math.sin(n * t));",
     "Rose Lines: petals + closing steps == Python; real slider keys update drawing and caption"),
    ("rose lines: closing steps use 180 instead of 360", "art/28-maurer/index.html",
     "closes = d => 360 / gcd(360, d);", "closes = d => 180 / gcd(180, d);",
     "Rose Lines: petals + closing steps == Python; real slider keys update drawing and caption"),
    ("first digits: Benford's dots use log10(1 + d) instead of log10(1 + 1/d)", "art/27-first-digits/index.html",
     "const BEN = [1, 2, 3, 4, 5, 6, 7, 8, 9].map(d => Math.log10(1 + 1 / d))", "const BEN = [1, 2, 3, 4, 5, 6, 7, 8, 9].map(d => Math.log10(1 + d) / 10)",
     "First Digits: page snapshot == digits.json, bars + Benford dots drawn right, note from the snapshot"),
    ("overtones: a new play doesn't stop the old one (stacked runs)", "art/26-overtones/index.html",
     "  stop(); ac = ac || new (window.AudioContext", "  ac = ac || new (window.AudioContext",
     "Hidden Notes: notes == Python; the page's own audio FFT'd (peaks, ladder, period); one live bus; can't hear"),
    ("overtones: the low C is a semitone off (C#2)", "art/26-overtones/index.html",
     "C2 = 440 * 2 ** (-33 / 12)", "C2 = 440 * 2 ** (-32 / 12)",
     "Hidden Notes: notes == Python; the page's own audio FFT'd (peaks, ladder, period); one live bus; can't hear"),
    ("lander: position updated before speed (explicit Euler)", "projects/27-lander/index.html",
     "function step(on){ s.v += (G - (on ? A : 0)) * DT; s.h -= s.v * DT;", "function step(on){ s.h -= s.v * DT; s.v += (G - (on ? A : 0)) * DT;",
     "Last Burn: page physics == Python, real-time autopilot exact, real held key/mouse burn, crash control"),
    ("lander: releasing the mouse doesn't stop the engine", "projects/27-lander/index.html",
     "['pointerup', 'pointercancel', 'lostpointercapture'].forEach(ev => $('burn').addEventListener(ev, () => press(false)));", "",
     "Last Burn: page physics == Python, real-time autopilot exact, real held key/mouse burn, crash control"),
    ("hilbert: the quadrant flip forgotten", "art/25-hilbert/index.html",
     "if (rx){ x = s - 1 - x; y = s - 1 - y; } [x, y] = [y, x];", "[x, y] = [y, x];",
     "One Long Line: path == Python, real click/tap lights the right cells, Hilbert blob vs row stripe"),
    ("hilbert: a tap reads the cell with x and y swapped", "art/25-hilbert/index.html",
     "picked = [Math.min(n - 1, Math.floor((e.clientX - r.left) / r.width * n)), Math.min(n - 1, Math.floor((e.clientY - r.top) / r.height * n))];",
     "picked = [Math.min(n - 1, Math.floor((e.clientY - r.top) / r.height * n)), Math.min(n - 1, Math.floor((e.clientX - r.left) / r.width * n))];",
     "One Long Line: path == Python, real click/tap lights the right cells, Hilbert blob vs row stripe"),
    ("sim: some triangles forgotten", "projects/26-sim/index.html",
     "for (let c = b + 1; c < 6; c++) T.push(", "for (let c = b + 2; c < 6; c++) T.push(",
     "No Triangles: verdicts == Python (700), won as 2nd by real clicks, lost as 1st, every line clickable, touch"),
    ("sim: a stale computer move lands on the new game", "projects/26-sim/index.html",
     "function later(f){ const g = gen; setTimeout(() => { if (g === gen) f(); }, 450); }", "function later(f){ setTimeout(f, 450); }",
     "No Triangles: verdicts == Python (700), won as 2nd by real clicks, lost as 1st, every line clickable, touch"),
    ("wythoff: a tap on a phone shows nothing (hover only, the bug found at cycle 212)", "art/14-wythoff/index.html",
     "cv.addEventListener('pointermove', readout); cv.addEventListener('pointerdown', readout);", "cv.addEventListener('pointermove', readout);",
     "Wythoff's Garden: page Grundy values == Python"),
    ("kissing circles: the new circle's centre forgets to double", "art/24-apollonian/index.html",
     "n = [0, 1, 2].map(t => 2 * (o[0][t] + o[1][t] + o[2][t]) - q[i][t]);", "n = [0, 1, 2].map(t => t ? (o[0][t] + o[1][t] + o[2][t]) - q[i][t] : 2 * (o[0][t] + o[1][t] + o[2][t]) - q[i][t]);",
     "Kissing Circles: curvatures == Python, tangent on canvas to 1,000, taps + caption arithmetic"),
    ("kissing circles: a tap forgets the canvas is scaled on screen", "art/24-apollonian/index.html",
     "pick((e.clientX - r.left) * W / r.width, (e.clientY - r.top) * W / r.height)", "pick(e.clientX - r.left, e.clientY - r.top)",
     "Kissing Circles: curvatures == Python, tangent on canvas to 1,000, taps + caption arithmetic"),
    ("collatz: the page counts the starting number as a step", "art/23-collatz/index.html",
     "window.coralApi = {steps: n => path(n).length - 1,", "window.coralApi = {steps: n => path(n).length,",
     "Collatz Coral: page steps 1..3000 == Python, 27 caption, red only when shown, phone 0"),
    ("collatz: 27 drawn in ink, not red", "art/23-collatz/index.html",
     "ctx.strokeStyle = css('--hot');", "ctx.strokeStyle = css('--ink');",
     "Collatz Coral: page steps 1..3000 == Python, 27 caption, red only when shown, phone 0"),
    ("spiral: winds the wrong way after the first turn", "art/19-spiral/index.html",
     "const D = [[1, 0], [0, -1], [-1, 0], [0, 1]];", "const D = [[1, 0], [0, 1], [-1, 0], [0, -1]];",
     "Prime Spiral: positions + primes == Python, Euler's 40 on a diagonal, 40 red pixels"),
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
    ("essay 31: red wins 32,768 -> 32,769", "writing/31-why-hex-cant-draw.md",
     "32,768 red wins and 32,768 blue", "32,769 red wins and 32,767 blue", "Essay 31: Hex walk numbers == walk.py; first version's failure in the journal"),
    ("hex walk: steps back into the triangle it left (cycle 194's own bug)", "projects/20-hex/walk.py",
     "if w != (a if t == 1 else b)]", "if w != (b if t == 1 else a)]",
     "Hex maze walk: always exits bottom-left/top-right, agrees with chain search (all 2x2..4x4)"),
    ("poems 29: forty primes -> thirty-nine", "writing/29-four-results.md",
     "forty times in a row.", "thirty-nine times in a row.", "Poems 29: Hex, Euler's forty, the ant, the crossed box == their pages' data"),
    ("story 28: the best round 2,200 -> 2,100", "writing/28-the-round.md",
     "Two thousand two hundred. That was", "Two thousand one hundred. That was",
     "Story 28: every distance == the town's map; odd corners; the walked route is real"),
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
# cycle 218: I ran "mutate.py --full", which this script read as a label FILTER; it matched nothing and printed
# "0 caught, 0 survived ... MUTATION RUN DONE", a clean-looking run that tested nothing. Flags don't exist here, and a
# filter that matches no mutant is an error, not a pass.
if any(o.startswith("-") for o in only): sys.exit(f"mutate.py takes label filters, not flags: {only} (no args = the full run)")
if only and not any(any(o in m[0] for o in only) for m in MUTATIONS): sys.exit(f"NO MUTANTS MATCHED {only}: nothing was tested")
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

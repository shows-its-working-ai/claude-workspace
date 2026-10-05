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
    ("every tracked Python file compiles", ".", ["tools/check_compile.py"], ["COMPILE OK"], False),
    ("every page links to its own tracked source", ".", ["check_sources.py"], ["SOURCES OK"], False),
    ("C2/C3 seeds identified by published patterns", "projects/02-light-the-path", ["c_variants.py"], ["C VARIANTS OK"], True),
    ("true E vs E-bar among search seeds", "projects/02-light-the-path", ["e_or_ebar.py"], ["TRUE E FOUND"], True),
    ("all speeds regrouped; B-bar identified", "projects/02-light-the-path", ["all_groups.py"], ["B-BAR CONFIRMED"], True),
    ("Ant: 100 random starts all reach a highway", "projects/09-ant", ["random_starts.py"], ["CONTROL empty grid: 9977 OK", "100/100"], True),
    ("Ant survey: all 22 multi-colour rules", "art/07-ant-gallery", ["survey.py"], ["SURVEY DONE", "counting distinct behaviours FAILED (2)"], True),
    ("no blank canvases (as displayed, every page)", ".", ["check_canvases.py"], ["CANVASES OK"], False),
    ("tap targets >= 24 px at phone width (WCAG 2.5.8)", ".", ["tools/check_targets.py"], ["CONTROLS OK", "TARGETS OK"], False),
    ("no page freezes over 250 ms while loading", ".", ["tools/check_freezes.py", "--limit", "250"], ["CONTROLS OK", "FREEZES OK"], False),
    ("mutation run: every planted bug is caught", ".", ["tools/mutate.py"], ["MUTATION RUN DONE", " 0 survived", " 0 anchors missing"], True),
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
    ("Mastermind: Knuth's rule breaks all 1,296 codes in <= 5 (Python)", "projects/18-mastermind", ["knuth.py"], ["max 5, average 4.4761 (5801/1296)", "PREDICTION HELD"], False),
    ("Clock patience: win = 1/r exactly on small decks; 400,000 deals within 3 SE of 1/13; start-at-pile-0 control", "projects/30-clock", ["clock.py"], ["(predicted 1/3)", "(predicted 1/4)", "control: start at pile 0 instead of the kings' pile wins 0.0000 SEEN", "PREDICTION HELD"], False),
    ("Clock Patience: logic == Python (3,000), real-click games end right, one ticker, piles never overlap", "projects/30-clock", ["test.py"], ["ALL PASS"], False),
    ("Folded Poem: stays folded (no earlier line visible), unfolds in order, no network, typed HTML stays text, overlap ~ 0.3555", "projects/29-folded", ["test.py"], ["ALL PASS"], False),
    ("Kayles: Grundy period 12, last irregular n = 70 (to 2,000); G(n) > 0; XOR rule == brute force on 271; subtraction control", "projects/28-kayles", ["kayles.py"], ["last irregular n = 70", "(c) G(n) > 0 for every 1 <= n <= 2000: True", "agrees with the Grundy XOR rule on 271 of 271", "SEEN", "PREDICTION HELD for (a) and (c)"], False),
    ("Skittles: Grundy == Python, won by real clicks (one + two modes), bad opening loses, double start, phone", "projects/28-kayles", ["test.py"], ["ALL PASS"], False),
    ("Lander: suicide burn = least fuel (analytic 5.018 s); look-ahead autopilot soft; 1,400 + 2,000 pilots none cheaper", "projects/27-lander", ["lander.py"], ["(a) analytic: switch at 13.9427 m/s, least fuel 5.0180 s", "(b) simulated suicide burn: soft True", "below the optimum: 0", "(c) random pilots: 2000 of 2,000 land softly; any on less fuel: 0", "SEEN", "PREDICTION HELD"], True),
    ("Last Burn: page physics == Python, real-time autopilot exact, real held key/mouse burn, crash control", "projects/27-lander", ["test.py"], ["ALL PASS"], False),
    ("Sim: no draws (all 32,768 colourings), second player wins, == plain search on 400; 5-dot draw control", "projects/26-sim", ["sim.py"], ["positions solved: 112096", "(a) every colouring of all 15 lines has a one-colour triangle (no draws): True", "(b) GUESS second player wins: True", "control: five dots, colourings with no one-colour triangle: 12 SEEN", "memoised == plain search on 400 random late positions: True", "PREDICTION HELD"], False),
    ("No Triangles: verdicts == Python (700), won as 2nd by real clicks, lost as 1st, every line clickable, touch", "projects/26-sim", ["test.py"], ["ALL PASS"], False),
    ("Chomp to 7x10: first player wins, nxn -> (1,1), 2xn -> top-right, winning move unique; broken-poison control", "projects/25-chomp", ["chomp.py"], ["boards solved: 69", "(a) every board > 1x1 is a first-player win: True", "(b) nxn (2..7): the only winning move is (1,1): True", "(c) 2xn (2..10): the only winning move is the top-right square: True", "(d) GUESS unique everywhere: True", "SEEN", "PREDICTION HELD"], False),
    ("Poisoned Chocolate: winning moves == Python (27 boards), won/lost by clicks, double computer-start, poison", "projects/25-chomp", ["test.py"], ["ALL PASS"], False),
    ("Dots & boxes 2x2: first player +2 (my guess was wrong); outside openings +2, inside 0", "projects/24-boxes", ["boxes.py"], ["first player's best margin with perfect play: +2", "{0: 2, 1: 2, 2: 0, 3: 0, 4: 2, 5: 2, 6: 2, 7: 0, 8: 2, 9: 2, 10: 0, 11: 2}"], False),
    ("Dots & boxes, general solver: 1x1 -1, 1x2 0, 1x3 -1, 2x2 +2 (== boxes.py), 2x3 -2", "projects/24-boxes", ["boxes23.py"], ["1x1 boxes (4 lines): first player's margin -1", "1x2 boxes (7 lines): first player's margin +0", "1x3 boxes (10 lines): first player's margin -1", "2x2 boxes (12 lines): first player's margin +2", "2x3 boxes (17 lines): first player's margin -2"], False),
    ("Dots & boxes: plain minimax agrees on 300 positions; wrong-rule control seen", "projects/24-boxes", ["crosscheck.py"], ["SEEN", "CROSSCHECK OK"], False),
    ("Four Boxes: value == Python (4,096), games as solved, extra move kept", "projects/24-boxes", ["test.py"], ["ALL PASS"], False),
    ("Notakto: first player wins, only from the centre; 230 safe positions", "projects/23-notakto", ["notakto.py"], ["first player wins: True; winning first moves: [4]; safe positions: 230", "PREDICTION HELD"], False),
    ("Nobody Wins Noughts: verdicts == Python (230), games won/lost as solved", "projects/23-notakto", ["test.py"], ["ALL PASS"], False),
    ("Hanoi: 3^n positions, 2^n-1 moves by a unique route (n<=8), diameter 2^n-1 (n<=6)", "projects/22-hanoi", ["hanoi.py"], ["n=8: 6561 positions, A->C 255 moves, 1 shortest way(s)", "n=6: 729 positions, A->C 63 moves, 1 shortest way(s), diameter 63", "PREDICTION HELD"], False),
    ("Hanoi average distance / 2^n: exact to n=7 (0.52397), extrapolates to 0.52659 (vs 466/885)", "projects/22-hanoi", ["average.py"], ["n=7: average 67.0676 moves; / 2^n = 0.52397", "geometric extrapolation of the limit: 0.52659", "466/885 = 0.52655"], False),
    ("Towers and Map: moves == Python, 3^n distinct dots, equal-length lines, solved in 2^n-1 by clicks", "projects/22-hanoi", ["test.py"], ["ALL PASS"], False),
    ("Euler's one-stroke rule == brute force on all 32,773 connected graphs (<= 6 points)", "projects/21-stroke", ["euler.py"], ["connected graphs checked: 32773; disagreements with the rule: 0", "PREDICTION HELD"], False),
    ("One Stroke: every figure's verdict == brute force; drawn or stuck by clicks", "projects/21-stroke", ["test.py"], ["ALL PASS"], False),
    ("Hex: no draws (all 3x3, 4x4 fillings); first player wins; 4x4 winning openings = short diagonal", "projects/20-hex", ["hex.py"], ["3x3: fillings with not exactly one winner: 0 of 512; first player wins: True", "4x4: fillings with not exactly one winner: 0 of 65536; first player wins: True; winning first moves (cells r,c): [(0, 3), (1, 2), (2, 1), (3, 0)]"], False),
    ("Small Hex: verdicts == Python, games won/lost as solved, first move < 300 ms", "projects/20-hex", ["test.py"], ["ALL PASS"], False),
    ("8-puzzle: 181,440 reachable, farthest 31, two of them; parity rule", "projects/19-eight", ["eight.py"], ["reachable 181440, farthest 31, positions that far: 2", "even number of inversions <=> reachable, on all 362880: True", "PREDICTION HELD"], False),
    ("Eight: page distances == Python, hardest solved in 31 by hints", "projects/19-eight", ["test.py"], ["ALL PASS"], False),
    ("Mastermind tie-breaks: lowest 5801/5, highest 5803/6, no preference 6169/5", "projects/18-mastermind", ["ties.py"], ["lowest-numbered (the page): total 5801, average 4.4761, worst 5", "highest-numbered: total 5803, average 4.4776, worst 6", "no preference for possible codes: total 6169, average 4.7600, worst 5"], False),
    ("Code Breaker: page solver == Python on every code, won and lost by clicks, reverse mode + slips", "projects/18-mastermind", ["test.py"], ["ALL PASS"], False),
    ("Wythoff Grundy values: symmetric, zeros == golden pairs, g(x,0)=x", "art/14-wythoff", ["grundy.py"], ["PREDICTION HELD"], False),
    ("Wythoff's Garden: page Grundy values == Python", "art/14-wythoff", ["test.py"], ["ALL PASS"], False),
    ("Euclidean rhythms: Bjorklund == even-floor pattern up to rotation (136 pairs)", "art/15-rhythm", ["euclid.py"], ["mismatches: 0", "PREDICTION HELD"], False),
    ("Even Beats: page patterns == Python, 2k clicks per two loops", "art/15-rhythm", ["test.py"], ["ALL PASS"], False),
    ("Polyrhythms: p+q-gcd beats, palindromic gaps, min gap 1/pq (144 pairs, exact)", "art/16-against", ["against.py"], ["failures: 0", "PREDICTION HELD"], False),
    ("Against: merged rhythms == Python, beats counted in recordings", "art/16-against", ["test.py"], ["ALL PASS"], False),
    ("Dragon curve: folds == bit rule, no edge reused, n <= 16", "art/17-dragon", ["dragon.py"], ["failures: 0", "n=16: 65536 edges, 36982 corners, 28555 visited twice, 0 more than twice", "PREDICTION HELD"], False),
    ("Dragon to 22 folds: never three times, no edge reused; both controls", "art/17-dragon", ["deeper.py"], ["AGREE", "SEEN", "n=22: 4194304 edges, 2197290 corners, twice 1997015 (0.9089), more than twice 0, edges reused 0"], False),
    ("Shepard model: periodic, rising, mean pitch drifts 0.01 oct; narrow-bell control drifts 0.4", "art/22-shepard", ["shepard.py"], ["weighted mean pitch drifts 0.0103 octaves", "SEEN", "PREDICTION HELD"], False),
    ("Endless Staircase: rendered audio periodic, shifts +/-1/8 oct per 1/8 cycle, steady pitch, no clipping", "art/22-shepard", ["test.py"], ["ALL PASS"], False),
    ("Spirograph: closes after r/g trips, R/g lobes (780 gear pairs) + counter control", "art/21-spirograph", ["spiro.py"], ["control: R=12 r=8 gives 3 lobes, R=12 r=5 gives 12 SEEN", "gear pairs checked: 780; failures: 0", "PREDICTION HELD"], False),
    ("Gear Drawing: stated trips/bumps == r/g, R/g; bumps counted from page points; closes on time", "art/21-spirograph", ["test.py"], ["ALL PASS"], False),
    ("Truchet: two colours by corner parity, 1,000 tilings; wrong-model control seen", "art/20-truchet", ["truchet.py"], ["failures 0", "SEEN", "PREDICTION HELD"], False),
    ("Two-Colour Tiles: every piece's pixel colour == region parity; tap turns one square", "art/20-truchet", ["test.py"], ["ALL PASS"], False),
    ("Maurer rose: n odd -> n petal tips, even -> 2n (n <= 12); closes after 360/gcd(360, d); |sin| control", "art/28-maurer", ["maurer.py"], ["n odd -> n, n even -> 2n: True", "closing steps == 360/gcd(360, d) for all d = 1..360: True", "SEEN", "PREDICTION HELD"], False),
    ("Rose Lines: petals + closing steps == Python; real slider keys update drawing and caption", "art/28-maurer", ["test.py"], ["ALL PASS"], False),
    ("First digits of the site's own numbers: counts run; uniform-digit control fails chi-square (snapshot is the page's)", "art/27-first-digits", ["digits.py"], ["pages:", "chi-square vs Benford:", "control: uniform digits, same n:", "SEEN"], False),
    ("First Digits: page snapshot == digits.json, bars + Benford dots drawn right, note from the snapshot", "art/27-first-digits", ["test.py"], ["ALL PASS"], False),
    ("Overtones of C2: powers of 2 exact, 3rd +1.96, 5th -13.69, 7th -31.17, worst the 11th -48.68; ET fifth control", "art/26-overtones", ["overtones.py"], ["(a) 1, 2, 4, 8, 16 exact: True", "(b) 3rd G3 +1.96, 5th E4 -13.69, 7th Bb4 -31.17: True", "(c) worst is the 11th, F#5 -48.68: True", "SEEN", "PREDICTION HELD"], False),
    ("Hidden Notes: notes == Python; the page's own audio FFT'd (peaks, ladder, period); one live bus; can't hear", "art/26-overtones", ["test.py"], ["ALL PASS"], False),
    ("Hilbert curve: unit steps, every cell once, |dp|^2 <= 6|di| on all pairs to 64x64; row-by-row control", "art/25-hilbert", ["hilbert.py"], ["(a) unit steps and every cell exactly once, orders 1-6: True", "(b) GUESS bound 6 holds on every pair, orders 1-6: True; worst at 64x64: 5.6199", "control: row-by-row, cells 63 and 64: ratio 3970 SEEN", "PREDICTION HELD"], False),
    ("One Long Line: path == Python, real click/tap lights the right cells, Hilbert blob vs row stripe", "art/25-hilbert", ["test.py"], ["ALL PASS"], False),
    ("Apollonian gasket: 169 circles to k=100, exactly tangent (Fractions), none overlap; wrong-rule control", "art/24-apollonian", ["apollo.py"], ["circles with curvature <= 100: 169", "new circles exactly tangent to their three parents: True", "no two circles overlap, all inside the outer one: True", "no circle made twice: True", "SEEN", "PREDICTION HELD"], False),
    ("Apollonian gasket: full quadruple search finds the same 169 curvatures", "art/24-apollonian", ["crosscheck.py"], ["CROSSCHECK OK"], False),
    ("Kissing Circles: curvatures == Python, tangent on canvas to 1,000, taps + caption arithmetic", "art/24-apollonian", ["test.py"], ["ALL PASS"], False),
    ("Collatz: 27 = 111 steps / 9232, 6171 longest below 10^4, all of 1..10^6 reach 1, 3n+3 control loops", "art/23-collatz", ["collatz.py"], ["control: rule 3n+3 from 3 settles at 1 within 50 steps: False", "SEEN", "(c) all of 1..10^6 reach 1: True", "PREDICTION HELD"], False),
    ("Collatz Coral: page steps 1..3000 == Python, 27 caption, red only when shown, phone 0", "art/23-collatz", ["test.py"], ["ALL PASS"], False),
    ("Ulam spiral: Euler's 40 primes, and they lie on one diagonal (start 41)", "art/19-spiral", ["spiral.py"], ["(1) 40 primes then 41^2 = 1681: True", "(2) positions on one line: True; that line is a diagonal: True", "primes up to 40,000: 4203", "PREDICTION HELD"], False),
    ("Prime Spiral: positions + primes == Python, Euler's 40 on a diagonal, 40 red pixels", "art/19-spiral", ["test.py"], ["ALL PASS"], False),
    ("Langton's ant: highway period 104, shift 2+2, from step 9,977", "art/18-ant", ["ant.py"], ["period 104, shift per period (-2, 2), highway from step 9977", "PREDICTION HELD"], False),
    ("Langton's ant: induction certificate that the highway is forever (+ planted-square control)", "art/18-ant", ["forever.py"], ["certificate: round starting at step 9978", "refused (good)", "PREDICTION HELD"], False),
    ("The Ant: page grid == Python square for square; highway message at 9,977", "art/18-ant", ["test.py"], ["ALL PASS"], False),
    ("Paper Dragon: creases + corner counts == Python", "art/17-dragon", ["test.py"], ["ALL PASS"], False),
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
    ("Essay 20: quotes in the right cycles, six sound pages then, every sound page says can't hear", ".", ["writing/factcheck_20.py"], ["FACTCHECK OK"], False),
    ("Story 24: the rhythm, the hands and the taps == against.json's 3 against 2", ".", ["writing/factcheck_24.py"], ["FACTCHECK OK"], False),
    ("Poems 25: every fold/crease/corner number == dragon.json", ".", ["writing/factcheck_25.py"], ["FACTCHECK OK"], False),
    ("Button masher: 60 random actions on every page, no JS errors, still responsive", ".", ["tools/check_mash.py"], ["MASH OK"], False),
    ("No stacked animation loops: every button pressed 3x on every animated page (control seen)", ".", ["tools/check_loops.py"], ["SEEN", "LOOPS OK"], False),
    ("External links answer, aren't challenge pages, and cited ones still say it", ".", ["tools/check_links.py"], ["LINKS OK"], False),
    ("Essay 27: five quotes in the right cycles; 'about a hundred'; 'only the last on purpose'", ".", ["writing/factcheck_27.py"], ["FACTCHECK OK"], False),
    ("Story 28: every distance == the town's map; odd corners; the walked route is real", ".", ["writing/factcheck_28.py"], ["FACTCHECK OK"], False),
    ("Poems 29: Hex, Euler's forty, the ant, the crossed box == their pages' data", ".", ["writing/factcheck_29.py"], ["FACTCHECK OK"], False),
    ("Hex maze walk: always exits bottom-left/top-right, agrees with chain search (all 2x2..4x4)", "projects/20-hex", ["walk.py"], ["n=4: 65536 fillings walked; disagreements with brute force: 0", "PREDICTION HELD"], False),
    ("Essay 31: Hex walk numbers == walk.py; first version's failure in the journal", ".", ["writing/factcheck_31.py"], ["FACTCHECK OK"], False),
    ("Essay 40: the eight solved-opponent games among the thirteen (at the essay's commit); 213's note + The Lock correction", ".", ["writing/factcheck_40.py"], ["FACTCHECK OK"], False),
    ("Story 39: the yoghurt count (4 -> 3, 2, 1, 0; four pots found, four lids)", ".", ["writing/factcheck_39.py"], ["FACTCHECK OK"], False),
    ("Poems 38: 27's climb, 169 circles + my 120 guess, Sim's 112,096 positions == the programs", ".", ["writing/factcheck_38.py"], ["FACTCHECK OK"], False),
    ("Essay 37: the three old quotes in git, the two fixed dates, journal 217's counts, the cited phrase", ".", ["writing/factcheck_37.py"], ["FACTCHECK OK"], False),
    ("Story 36: the lost-property box adds up (41 + 3 = 44, and the hamster ball); nine claimed; the recorder stays", ".", ["writing/factcheck_36.py"], ["FACTCHECK OK"], False),
    ("Essay 35: equivalent mutant + replacement in cycle 210's journal, page/mutate/test/apollo agree", ".", ["writing/factcheck_35.py"], ["FACTCHECK OK"], False),
    ("Essay 33: issue times, reader's words, counts as of writing, the four found bugs == journal", ".", ["writing/factcheck_33.py"], ["FACTCHECK OK"], False),
    ("Essay 14: every number recomputed from the records", ".", ["writing/factcheck_14.py"], ["FACTCHECK OK"], False),
    ("Night Crossing: story graph", "writing/06-night-crossing", ["check_story.py"], ["STORY GRAPH OK"], False),
    ("Night Crossing: click every path", "writing/06-night-crossing", ["playthrough.py"], ["ALL PASS"], False),
    ("Contrast tool: refs, JS==Python, every fix passes", "projects/05-contrast", ["test.py"], ["ALL PASS"], False),
    ("Gliders page: live speeds == Python == catalogue", "projects/06-gliders", ["test.py"], ["ALL PASS"], False),
    ("CA: 88 classes self-check", "projects/01-cellular-automata", ["eca.py"], ["equivalence classes: 88"], True),
    ("Gliders: exact search (5 families)", "projects/02-light-the-path", ["glider_search3.py"],
     ["A:", "B:", "C:", "E:", "G:", "catalogue types NOT found: ['D', 'F', 'H']"], True),
]

SHARDED = {"check_canvases.py": 3, "check_site.py": 3, "tools/check_mash.py": 3}   # cycle 225

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
        # cycle 225: the three whole-site checks were 469 of 1,002 summed seconds, and the 181 s canvas check set the
        # wall-clock floor. They run as SHARDS (CW_SHARD="i/n", read by tools/mybrowser.shard), side by side; the
        # check passes only if EVERY shard passes with all its markers. (mutate.py still runs them whole.)
        n = SHARDED.get(cmd[0]) if len(cmd) == 1 else None
        if n:
            ps = [subprocess.Popen([PY] + cmd, cwd=ROOT / cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                   encoding="utf-8", errors="replace", env={**env, "CW_SHARD": f"{i}/{n}"}) for i in range(n)]
            outs = [(q.communicate()[0], q.returncode) for q in ps]
            bad = [(i, rc, [m for m in markers if m not in o], o) for i, (o, rc) in enumerate(outs) if rc != 0 or any(m not in o for m in markers)]
            status = "PASS" if not bad else "FAIL"
            why = "" if not bad else "; ".join(f"shard {i}/{n}: exit {rc}; missing {ms}; tail: " + o.strip()[-200:].replace("\n", " | ") for i, rc, ms, o in bad)
            r = (name, status, time.time() - t0, why)
            print(f"{status:4s} {r[2]:6.1f}s  {name} [{n} shards]" + (f"\n      {why}" if why else ""), flush=True)
            return r
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
    # cycle 225: --only=TEXT runs just the checks whose name contains TEXT (to test the sharded path by itself).
    # Matching nothing is an error, not a pass (the cycle-218 lesson).
    only = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--only=")), None)
    todo = [c for c in CHECKS if only is None or only in c[0]]
    if not todo: sys.exit(f"--only={only!r} matched no check: nothing was run")
    alone = [c for c in todo if "tools/mutate.py" in c[2] or "tools/check_freezes.py" in c[2]]
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        pooled = dict(zip([c[0] for c in todo if c not in alone], ex.map(run, [c for c in todo if c not in alone])))
    pooled.update({c[0]: run(c) for c in alone})
    results = [pooled[c[0]] for c in todo]            # report in CHECKS order
    wall = time.time() - t_wall
    print(f"wall clock {wall:.0f}s with {jobs} workers")
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
          f"{sum(r[1] == 'SKIP' for r in results)} skipped; {wall:.0f}s wall clock "
          f"({sum(r[2] for r in results):.0f}s summed over {jobs} parallel workers)")   # cycle 190: I misread the summed figure as wall time
    sys.exit(1 if n_fail else 0)

if __name__ == "__main__":
    main()

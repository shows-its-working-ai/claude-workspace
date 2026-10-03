"""Glider Music self-test. (1) An independent Python score must match the page's score().
(2) The rendered audio must PLAY that score: per step, each intended pitch is present in the
spectrum and the strongest peak is one of them; empty steps are silent. (3) Keyboard + no errors.
Note: this verifies the sound matches the score. It can't verify the music is any good."""
import sys
from pathlib import Path
import numpy as np
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright

TILE = [0,0,0,1,0,0,1,1,0,1,1,1,1,1]; NT = 8; W = 14 * NT; STEPS = 40; DT = 0.25; SR = 44100
SEEDS = {"A": [0, 5], "B": [7, 14], "C": [6, 23], "E": [6], "G": [2, 18]}; SCALE = [0, 2, 4, 7, 9]
base = np.array([TILE[i % 14] for i in range(W)])
def step(r): return np.array([(110 >> (4 * r[(x - 1) % W] + 2 * r[x] + r[(x + 1) % W])) & 1 for x in range(W)])
shift = next(d for d in range(W) if np.array_equal(np.roll(base, d), step(base)))
def py_score():
    r = base.copy()
    for g, k in (("A", 1), ("E", 4)):
        for o in SEEDS[g]: r[(14 * k + o) % W] ^= 1
    out = []
    for t in range(STEPS):
        d = [x for x in range(W) if r[x] != np.roll(base, shift * t)[x]]
        groups = []
        for x in d:
            if groups and x - groups[-1][-1] <= 8: groups[-1].append(x)
            else: groups.append([x])
        if len(groups) > 1 and groups[0][0] + W - groups[-1][-1] <= 8: groups[0] = groups.pop() + groups[0]
        notes = []
        for g in groups[:4]:
            idx = min(14, int(np.floor(np.mean(g) / W * 15)))
            notes.append(round(220 * 2 ** ((12 * (idx // 5) + SCALE[idx % 5]) / 12), 3))
        out.append(notes); r = step(r)
    return out

ok = True
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri())
    js = [[round(n["freq"], 3) for n in step_notes] for step_notes in pg.evaluate(f"score({STEPS})")]
    same = js == py_score(); ok &= same
    print(f"(1) JS score == independent Python score over {STEPS} steps: {same}  "
          f"(notes per step: {[len(s) for s in js[:12]]}...)")
    audio = np.array(pg.evaluate(f"renderScore({STEPS}, {DT}).then(a => Array.from(a))"))
    good = silent_ok = 0
    for i, notes in enumerate(js):
        seg = audio[int((i * DT + 0.015) * SR): int((i * DT + 0.2) * SR)]
        spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))); f = np.fft.rfftfreq(len(seg), 1 / SR)
        band = (f > 150) & (f < 2000)
        if not notes:
            silent_ok += spec[band].max() < 1e-3; continue
        floor = np.median(spec[band])
        present = all(spec[np.argmin(abs(f - n))] > 20 * floor for n in set(notes))
        peak = f[band][np.argmax(spec[band])]
        top_ok = any(abs(peak - n) / n < 0.03 for n in notes)
        good += present and top_ok
    sounding = sum(1 for s in js if s); quiet = STEPS - sounding
    print(f"(2) audio plays the score: {good}/{sounding} sounding steps correct, {silent_ok}/{quiet} empty steps silent")
    ok &= good == sounding and silent_ok == quiet
    two = [len(s) for s in js]
    print(f"    notes per step with gliders A + E: min {min(two)}, max {max(two)} (expect 2 while apart)")
    empty = pg.evaluate(f"score({STEPS}, [])"); quiet_audio = np.array(pg.evaluate(f"renderScore({STEPS}, {DT}, []).then(a => Array.from(a))"))
    silent = all(len(s) == 0 for s in empty) and np.abs(quiet_audio).max() < 1e-6
    print(f"    empty board: no notes and silent audio: {silent}"); ok &= silent
    pg.focus("[data-g='G']"); pg.keyboard.press("Enter"); pg.keyboard.press("Tab"); pg.keyboard.press("Enter")
    pg.screenshot(path=str(D / "look.png"))
    print("(3) js errors:", errs); ok &= not errs
    ctx.close()
print("ALL PASS" if ok else "FAILURES")

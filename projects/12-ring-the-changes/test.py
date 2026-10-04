"""Ring the Changes: the page's move rules == Python's (art/09-blue-line/extents.py), played through the real UI.
- every one of the 24 no-long-places extents wins by CLICKS in ringers'-rule mode;
- 40 random extents (of 10,792) win by KEYBOARD in free mode; in rule mode each of them is blocked somewhere;
- along 300 random walks, the page's legal/illegal verdict for every change matches Python's;
- a dead end is reported as stuck; undo works; phone overflow 0; no JS errors."""
import random, sys
from pathlib import Path
D = Path(__file__).resolve().parent
ROOT = D.parents[1]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "art" / "09-blue-line"))
from extents import all_extents, no_long_places, do
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
ext = all_extents(); good = [s for s in ext if no_long_places(s)]
rng = random.Random(116)
KEY = {"12": "1", "23": "2", "34": "3", "x": "x"}

def still(a, b, c): return any(a[p] == b[p] == c[p] for p in range(4))
def py_legal(rows, ch, hard):
    nxt = do(rows[-1], ch); n = len(rows)
    if n == 24:
        return nxt == "1234" and not (hard and (still(rows[22], rows[23], nxt) or still(rows[23], nxt, rows[1])))
    if n > 24 or nxt in rows: return False
    return not (hard and n >= 2 and still(rows[-2], rows[-1], nxt))

with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.rtc !== undefined")
    def reset(hard):
        if pg.is_checked("#hard") != hard: pg.click("#hard")
        pg.click("#reset")
    wins = 0
    for s in good:
        reset(True)
        for ch in s: pg.click(f'button[data-ch="{ch}"]')
        wins += pg.evaluate("rtc.won")
    check(f"all {len(good)} no-long-places extents win by clicks in rule mode", wins == len(good) == 24)
    sample = rng.sample([s for s in ext if s not in good], 40); kw = 0; blocked = 0
    for s in sample:
        reset(False)
        for ch in s: pg.keyboard.press(KEY[ch])
        kw += pg.evaluate("rtc.won")
        reset(True)
        for ch in s: pg.keyboard.press(KEY[ch])
        blocked += not pg.evaluate("rtc.won")
    check("40 random extents win by keyboard in free mode", kw == 40)
    check("...and every one of them is blocked in rule mode", blocked == 40)
    mism = 0; checked = 0; stuck_seen = False
    for walk in range(300):
        hard = walk % 2 == 1; reset(hard); rows = ["1234"]
        while True:
            verdicts = pg.evaluate("Object.keys(rtcApi.CHANGES).map(c => rtcApi.legal(c).ok)")
            want = [py_legal(rows, ch, hard) for ch in ("12", "23", "34", "x")]
            checked += 4; mism += sum(a != b for a, b in zip(verdicts, want))
            choices = [ch for ch, w in zip(("12", "23", "34", "x"), want) if w]
            if not choices:
                stuck_seen |= pg.evaluate("rtc.stuck") and len(rows) < 25; break
            ch = rng.choice(choices); pg.click(f'button[data-ch="{ch}"]'); rows.append(do(rows[-1], ch))
            if len(rows) == 25: break
    check(f"page legality == Python on {checked} (row, change) verdicts over 300 random walks", mism == 0, f"mismatches {mism}")
    check("random walks reach a dead end, reported as stuck", stuck_seen)
    reset(False); pg.click('button[data-ch="x"]'); pg.click('button[data-ch="23"]'); pg.click("#undo")
    check("undo removes the last row", pg.evaluate("rtc.rows") == ["1234", "2143"])
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    pg.set_viewport_size({"width": 900, "height": 900}); pg.screenshot(path=str(D / "look.png"), full_page=True)
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")

"""Push Your Luck: dice pinned via Math.random; REAL clicks: rolls add up, a 1 wipes the turn and moves to the next
turn, Hold banks and moves on, Hold is disabled with nothing to bank; finishing at >= 100 reports the turn count;
the note's numbers (8.14, 12.64, 12.55, the 20/21 tie) == pig.py's exact results; control: a game played with
pinned dice ends in exactly the number of turns worked out here by hand; phone 0; no JS errors."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
py = json.loads((D / "pig.json").read_text(encoding="utf-8"))
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
def pin(pg, faces): pg.evaluate("fs => { let i = 0; Math.random = () => (fs[i++ % fs.length] - 1) / 6 + 0.01; }", faces)
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.pig !== undefined")
    note = " ".join(pg.inner_text(".note").split())
    check("note numbers == pig.py (8.14 per turn, 20 and 21 tie, 12.64, 12.55)", f"{py['pts20']:.2f}" in note and py["best_thresholds"] == [20, 21]
          and "holding at 21 banks exactly the same" in note and f"{py['turns20']:.2f}" in note and f"{py['turns_opt']:.2f}" in note)
    check("Hold is disabled with nothing to bank", pg.is_disabled("#hold"))
    pin(pg, [6, 5, 1]); pg.click("#roll"); pg.click("#roll")
    check("two rolls (6, 5) add up to 11 this turn", pg.evaluate("pig.t") == 11)
    pg.click("#roll"); s = pg.evaluate("window.pig")
    check("a 1 wipes the turn and moves to turn 2, nothing banked", s == {"s": 0, "t": 0, "n": 2, "done": False} and "lose the 11" in pg.inner_text("#msg"))
    pin(pg, [4]); pg.click("#roll"); pg.click("#hold"); s = pg.evaluate("window.pig")
    check("Hold banks 4 and moves to turn 3", s["s"] == 4 and s["t"] == 0 and s["n"] == 3)
    # control: a whole fresh game with pinned dice. Each turn rolls 6,6,6,6 (= 24) and holds: banked 24, 48, 72, 96,
    # then 120 on turn 5, so it must say "Done in 5 turns" (worked out by hand, not taken from the page)
    pg.click("#new"); pin(pg, [6]); turns = 0
    while not pg.evaluate("pig.done") and turns < 20:
        for _ in range(4): pg.click("#roll")
        pg.click("#hold"); turns += 1
    s = pg.evaluate("window.pig"); msg = pg.inner_text("#msg")
    check("control: 24 a turn reaches 100 in exactly 5 turns (96 after 4, 120 after 5), and says so", s["done"] and s["n"] == 5 and s["s"] == 120 and "Done in 5 turns" in msg, f"{s} {msg[:30]}")
    check("finished: Roll and Hold disabled", pg.is_disabled("#roll") and pg.is_disabled("#hold"))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 700, "height": 950}); pg.click("#new"); pin(pg, [5, 3, 6]); [pg.click("#roll") for _ in range(3)]
    pg.screenshot(path=str(D.parents[1] / "tools" / "_pig_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")

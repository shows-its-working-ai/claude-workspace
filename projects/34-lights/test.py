"""Lights Out: REAL clicks flip exactly the cell and its neighbours (== lights.py's masks, all 25 cells); 200 'New
puzzle' boards are all solvable by an INDEPENDENT test (the press matrix is symmetric, so a board can be switched off
iff it has an even overlap with each of lights.py's quiet patterns); the page's own solver, pressed out by real
clicks, turns a board fully off and says so; Hint marks a light in a solution; Start again restores the board; the
note's 'one in four' and 'three ways' == lights.py; phone; no JS errors. Control: a single lit corner fails the
independent test and the page's Hint says it can't be switched off."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
L = json.loads((D / "lights.json").read_text(encoding="utf-8"))
solvable = lambda b: all(bin(b & q).count("1") % 2 == 0 for q in L["quiets"])
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.lights !== undefined")
    wrong = []
    for i in range(25):
        pg.evaluate("setBoard(0)"); pg.click(f"#board button:nth-child({i + 1})")
        if pg.evaluate("lights.board") != L["cols"][i]: wrong.append(i)
    check("a real click flips exactly the cell and its neighbours, on all 25 cells", not wrong, wrong)
    boards = []
    for _ in range(200):
        pg.click("#new"); boards.append(pg.evaluate("lights.board"))
    check("200 'New puzzle' boards are all solvable (independent test) and not all the same", all(map(solvable, boards)) and len(set(boards)) > 100, f"{len(set(boards))} different")
    b = boards[-1]; presses = pg.evaluate(f"solveLights({b})")
    for i in range(25):
        if presses >> i & 1: pg.click(f"#board button:nth-child({i + 1})")
    check("the page's solution, pressed by real clicks, turns it all off", pg.evaluate("lights.board") == 0 and "All off" in pg.inner_text("#msg"), pg.inner_text("#msg"))
    pg.click("#reset"); check("Start again puts the same board back", pg.evaluate("lights.board") == b and pg.evaluate("lights.moves") == 0)
    pg.click("#hint"); h = pg.evaluate("lights.hintAt")
    # cycle 267: this first read "... and (presses >> h & 1 or solvable(b))", and the "or" made it always true
    check("Hint marks a light that's in the solution for this board", h >= 0 and pg.locator("#board button.hint").count() == 1 and presses >> h & 1, h)
    pg.evaluate("setBoard(1)"); pg.click("#hint")
    check("control: one lit corner fails the independent test, and Hint says it can't be done", not solvable(1) and "can’t be switched off" in pg.inner_text("#msg"), "SEEN" if not solvable(1) else "NOT SEEN")
    note = pg.inner_text(".note")
    note = " ".join(note.split())
    check("the note's 'one time in four' and 'three ways' == lights.py", 2 ** (25 - L["rank"]) == 4 and "one time in four" in note and len(L["quiets"]) == 3 and "exactly three ways" in note)
    pg.set_viewport_size({"width": 390, "height": 800})
    check("phone width: no sideways scroll", pg.evaluate("document.documentElement.scrollWidth - innerWidth") == 0)
    check("no JS errors", not errs, errs)
    ctx.close()
print("ALL PASS" if ok else "SOME FAILED"); sys.exit(0 if ok else 1)

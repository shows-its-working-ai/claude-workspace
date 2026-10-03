"""Slide, tested in Claude's own browser.
Prediction (written first): for all 12 levels the browser's own BFS par equals the generator's par, and playing the
generator's solution by KEYBOARD wins in exactly par moves. Also: no solution text in the page; a blocked move
doesn't count; undo restores; buttons + swipe move; phone overflow 0; no JS errors.
An independent third check: a brute-force search here (iterative deepening, no BFS) confirms each par is minimal."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
from make_levels import slide

ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
levels = json.loads((D / "levels.json").read_text(encoding="utf-8"))
KEY = {"U": "ArrowUp", "D": "ArrowDown", "L": "ArrowLeft", "R": "ArrowRight"}

def iddfs_par(L, limit=20):                                     # no BFS: exhaustive depth-limited search
    goal = tuple(L["goal"])
    def dfs(p, depth, seen):
        if p == goal: return True
        if depth == 0: return False
        for d in "UDLR":
            n = slide(L["grid"], *p, d)
            if n != p and n not in seen and dfs(n, depth - 1, seen | {n}): return True
        return False
    for k in range(limit + 1):
        if dfs(tuple(L["start"]), k, {tuple(L["start"])}): return k
html = (D / "index.html").read_text(encoding="utf-8")
check("no solutions shipped", all(L["solution"] not in html for L in levels) and '"solution"' not in html)
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.set_viewport_size({"width": 800, "height": 1000})
    pg.goto((D / "index.html").as_uri())
    for i, L in enumerate(levels):
        pg.click(f'#pick button[data-i="{i}"]')
        live = pg.evaluate(f"slideGame.bfsPar(slideGame.LEVELS[{i}])"); idd = iddfs_par(L)
        for d in L["solution"]: pg.keyboard.press(KEY[d])
        st = pg.evaluate("slideGame.state()")
        good = live == L["par"] == idd and st["won"] and st["moves"] == L["par"]
        check(f"{L['name']}: par {L['par']} = browser BFS {live} = brute force {idd}; keyboard solve wins in {st['moves']}", good)
    # blocked move doesn't count; undo restores; buttons and swipe move
    pg.click('#pick button[data-i="0"]'); L = levels[0]
    s0 = pg.evaluate("slideGame.state()")
    # walk the solution until some direction is blocked (a wall or rock right next to us), then press it
    pos, k = tuple(L["start"]), 0
    while not any(slide(L["grid"], *pos, d) == pos for d in "UDLR"):
        pos = slide(L["grid"], *pos, L["solution"][k]); pg.keyboard.press(KEY[L["solution"][k]]); k += 1
    blocked = next(d for d in "UDLR" if slide(L["grid"], *pos, d) == pos)
    pg.keyboard.press(KEY[blocked]); st = pg.evaluate("slideGame.state()")
    check(f"blocked move ({blocked} after {k} moves) is not counted", st["moves"] == k and st["pos"] == list(pos))
    pg.click("#restart")
    d0 = L["solution"][0]; pg.click(f'.pad button[data-d="{d0}"]'); s1 = pg.evaluate("slideGame.state()")
    check("on-screen button moves", s1["moves"] == 1 and s1["pos"] == list(slide(L["grid"], *L["start"], d0)))
    pg.click("#undo"); s2 = pg.evaluate("slideGame.state()")
    check("undo restores start", s2["pos"] == s0["pos"] and s2["moves"] == 0)
    box = pg.locator("#board").bounding_box(); cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    dx, dy = {"U": (0, -80), "D": (0, 80), "L": (-80, 0), "R": (80, 0)}[d0]
    pg.mouse.move(cx, cy); pg.mouse.down(); pg.mouse.move(cx + dx, cy + dy); pg.mouse.up()
    check("swipe moves", pg.evaluate("slideGame.state()")["moves"] == 1)
    # cycle 68: walk into a trap (found by Python BFS) -> the page must say there's no way out
    from quality import analyse
    from collections import deque
    tl = next(i for i, L in enumerate(levels) if analyse(L)["traps"] > 0); L = levels[tl]
    prev = {tuple(L["start"]): None}; q = deque([tuple(L["start"])]); trap_path = None
    def reach_goal(p):
        seen = {p}; qq = deque([p])
        while qq:
            x = qq.popleft()
            if x == tuple(L["goal"]): return True
            for d in "UDLR":
                n = slide(L["grid"], *x, d)
                if n not in seen: seen.add(n); qq.append(n)
        return False
    while q:
        x = q.popleft()
        if not reach_goal(x):
            path = []; y = x
            while prev[y]: y, d = prev[y]; path.append(d)
            trap_path = "".join(reversed(path)); break
        for d in "UDLR":
            n = slide(L["grid"], *x, d)
            if n != x and n not in prev: prev[n] = (x, d); q.append(n)
    pg.click(f'#pick button[data-i="{tl}"]')
    for d in trap_path: pg.keyboard.press(KEY[d])
    msg = pg.inner_text("#status")
    check(f"trap on level {tl + 1} (path {trap_path}) -> 'No way out' shown", "No way out" in msg, f"[{msg}]")
    pg.keyboard.press("u"); check("undo clears the trap message", "No way out" not in pg.inner_text("#status"))
    # progress survives a reload (levels solved above are remembered)
    before = pg.evaluate("slideGame.best()"); pg.reload(); after = pg.evaluate("slideGame.best()")
    done = pg.locator("#pick button.done").count()
    check("solved levels remembered after reload", before == after and len(after) == 12 and done == 12, f"{len(after)} saved, {done} marked")
    pg.screenshot(path=str(D / "look.png"))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")

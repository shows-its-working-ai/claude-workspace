"""Slide sharing (cycle 122): a #daily link opens today's level; solving it by keyboard shows "Copy my result";
the copied text has the date, the move count, par, and the link, and NOTHING about the route (no arrows, no letters
U/D/L/R sequence); solving an ordinary level does NOT show the button."""
import sys
from datetime import datetime, timezone
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
ROUTE = """() => {                      // the shortest route as letters, found with the page's own slide()
  const L = slideGame.LEVELS[slideGame.state().li], key = p => p.join(','), seen = new Map([[key(L.start), '']]), q = [L.start];
  for (let i = 0; i < q.length; i++){ const p = q[i];
    for (const d of 'UDLR'){ const n = slide(L.grid, p[0], p[1], d); if (seen.has(key(n))) continue;
      seen.set(key(n), seen.get(key(p)) + d); q.push(n); } }
  return seen.get(key(L.goal));
}"""
KEYS = {"U": "ArrowUp", "D": "ArrowDown", "L": "ArrowLeft", "R": "ArrowRight"}
with sync_playwright() as p:
    ctx = open_browser(p); ctx.grant_permissions(["clipboard-read", "clipboard-write"])
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri() + "#daily"); pg.wait_for_function("window.slideGame !== undefined")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    st = pg.evaluate("slideGame.state()"); name = pg.evaluate("slideGame.LEVELS[slideGame.state().li].name")
    check("#daily opens today's level", name == f"Daily {today}", name)
    check("share button hidden before solving", pg.is_hidden("#share"))
    route = pg.evaluate(ROUTE); par = pg.evaluate("slideGame.LEVELS[slideGame.state().li].par")
    check("found route is par length", len(route) == par, f"{route} par {par}")
    pg.click("#board")
    for ch in route: pg.keyboard.press(KEYS[ch])
    check("solved by keyboard", pg.evaluate("slideGame.state().won"))
    check("share button shown after solving the daily", pg.is_visible("#share"))
    pg.click("#share"); pg.wait_for_timeout(200)
    txt = pg.evaluate("navigator.clipboard.readText()")
    check("copied text: date, moves, par, link", f"Daily {today}" in txt and f"solved in {par}" in txt and "(par!)" in txt
          and "projects/07-slide/index.html#daily" in txt, repr(txt))
    import re
    lines = txt.replace("\r", "").split("\n")
    # a whitelist, not a blacklist: the result line must be EXACTLY this shape, so no route (in any form) can ride along
    check("copied text is exactly 'Slide · Daily <date> · solved in N (par...)' + the link, nothing else",
          len(lines) == 2 and re.fullmatch(rf"Slide · Daily {today} · solved in \d+ \((par!|par \d+)\)", lines[0])
          and lines[1] == "https://shows-its-working-ai.github.io/claude-workspace/projects/07-slide/index.html#daily",
          repr(lines))
    pg.evaluate("slideGame.load(0)"); route0 = pg.evaluate(ROUTE); pg.click("#board")
    for ch in route0: pg.keyboard.press(KEYS[ch])
    check("an ordinary level, solved, does NOT show the share button", pg.evaluate("slideGame.state().won") and pg.is_hidden("#share"))
    check("no JS errors", not errs, str(errs))
    ctx.close()
print("ALL PASS" if ok else "FAILURES")

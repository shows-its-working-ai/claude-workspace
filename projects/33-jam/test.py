"""The Jam: REAL clicks through the page. Expected answers are written here by hand from the design (cycle 248's
notes), not read from the page: with nothing found, accusing Pask can't be proved and all four others are named;
Bernard is cleared by the photo AND the rota together; Hen by the walk; Adeyemi by the keys; after the card only
Bernard and Hen are still possible; keys + rota + photo + walk proves it with 4 clues; Pask's chutney story clears nobody. Control: the spoon alone
proves nothing. Also: no dead buttons, Start again resets, phone width doesn't overflow, no JS errors."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
def accuse(pg, who): pg.click(f'#who button[data-who="{who}"]'); return pg.inner_text("#verdict")
def fetch(pg, place):   # walk there from wherever we are, take the clue, come back
    if pg.evaluate("jam.at") != "hall": pg.click('#moves button[data-go="hall"]')
    pg.click(f'#moves button[data-go="{place}"]'); pg.click("#act"); pg.click('#moves button[data-go="hall"]')
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.jam !== undefined")
    check("starts in the hall: 5 ways out plus 'Talk to Mr Pask'", pg.evaluate("jam.at") == "hall" and pg.locator("#moves button[data-go]").count() == 5 and pg.inner_text("#act") == "Talk to Mr Pask")
    pg.click("#act"); v = accuse(pg, "Mrs Adeyemi")
    check("red herring: after Pask's chutney story, Mrs Adeyemi is STILL cleared by the keys", "Who has a key" in v and pg.evaluate("jam.found") == ["chutney"], v)
    pg.click("#again")
    v = accuse(pg, "Mr Pask")
    check("Pask with nothing found: can't prove it, all four others named", "can't prove it yet" in v and all(q in v for q in ["Mrs Adeyemi", "Bernard", "Lorna", "Hen"]), v)
    v = accuse(pg, "Bernard")
    check("Bernard is cleared by the photo AND the rota (with where to look)", v.startswith("It wasn't Bernard") and "Lorna's photo" in v and "The urn rota" in v and "Put together" in v and "the kitchen" in v and "the stage" in v, v)
    check("Hen is cleared by the walk alone", "It wasn't Hen" in accuse(pg, "Hen") and "The vicar's walk" in pg.inner_text("#verdict") and "Put together" not in pg.inner_text("#verdict"))
    check("Mrs Adeyemi is cleared by the keys", "Who has a key" in accuse(pg, "Mrs Adeyemi"))
    # control: the spoon points at Pask but must prove nothing
    fetch(pg, "cloakroom")
    v = accuse(pg, "Mr Pask")
    check("control: the spoon alone does NOT prove it", "can't prove it yet" in v and not pg.evaluate("jam.solved"), v)
    fetch(pg, "committee")
    v = accuse(pg, "Mr Pask")
    check("after the card: only Bernard and Hen still possible besides Pask", "can't prove it yet" in v and "Bernard" in v and "Hen" in v and "Lorna" not in v and "Adeyemi" not in v, v)
    check("a found clue is no longer 'not found yet'", "not found yet" not in accuse(pg, "Lorna"), pg.inner_text("#verdict"))
    for q in ["kitchen", "stage", "carpark"]: fetch(pg, q)
    pg.click("#act")   # back in the hall: Pask's chutney story, the sixth clue
    texts = pg.inner_text("#notes")
    check("notebook shows all 6 clues, counted", pg.locator("#notes li").count() == 6 and "(6 of 6 clues)" in pg.inner_text("#count") and "NOBODY ELSE" in texts and "tea urn: BERNARD" in texts)
    v = accuse(pg, "Mr Pask")
    check("with every clue, accusing Pask SOLVES it", pg.evaluate("jam.solved") and v.startswith("It was Mr Pask") and "6 clues" in v, v)
    check("after solving, the accuse buttons are disabled", all(pg.locator("#who button").nth(i).is_disabled() for i in range(5)))
    pg.click("#again")
    check("Start again: back in the hall, empty notebook, verdict cleared", pg.evaluate("jam") == {"at": "hall", "found": [], "solved": False, "possible": ["Mrs Adeyemi", "Mr Pask", "Bernard", "Lorna", "Hen"]} and pg.inner_text("#verdict") == "")
    for q in ["committee", "kitchen", "stage", "carpark"]: fetch(pg, q)
    v = accuse(pg, "Mr Pask")
    check("the four needed clues (no spoon) are enough: solved with 4", pg.evaluate("jam.solved") and "4 clues" in v, v)
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone width: no sideways scroll", ov == 0, ov)
    check("no JS errors", not errs, errs)
    ctx.close()
print("ALL PASS" if ok else "SOME FAILED"); sys.exit(0 if ok else 1)

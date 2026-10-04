"""Tap-target sizes at phone width (cycle 120). For every page, every visible link, button, input, select, summary:
its box at 390 px wide. WCAG 2.5.8 (AA) asks for 24x24 CSS px, with an exception for links inline in a sentence
(their size is set by the text around them); those are counted separately and not failed.
Reports every non-inline target under 24 px in either dimension. Usage: check_targets.py [pages...]"""
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8")
ONLY = sys.argv[1:]
tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n")
pages = ONLY or [f for f in tracked if f.endswith(".html") and "template" not in f]
MEASURE = """() => {
  const out = [];
  for (const el of document.querySelectorAll('a[href], button, input, select, summary, textarea, [role=button]')){
    const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
    if (!r.width || !r.height || cs.visibility === 'hidden' || cs.display === 'none') continue;
    // a label wrapping a checkbox makes the whole label the target
    let w = r.width, h = r.height;
    const lab = el.closest('label');
    if (lab && (el.type === 'checkbox' || el.type === 'radio')){ const lr = lab.getBoundingClientRect(); w = Math.max(w, lr.width); h = Math.max(h, lr.height); }
    // inline exception: an <a> whose parent block has other text around it
    const p = el.parentElement, own = (el.textContent || '').trim(), ctx = p ? (p.textContent || '').trim() : '';
    // cycle 121: 'inline' means in a SENTENCE: the parent's text minus every link's text still has 3+ words.
    // (cycle 120's rule, any other text at all, exempted 'everything · source' navigation.)
    let rest = ctx; if (p) for (const a of p.querySelectorAll('a')) rest = rest.replace((a.textContent || '').trim(), ' ');
    const inline = el.tagName === 'A' && cs.display === 'inline' && (rest.match(/[A-Za-z]{2,}/g) || []).length >= 3;
    out.push({tag: el.tagName.toLowerCase(), text: (own || el.getAttribute('aria-label') || el.type || '').slice(0, 30),
              w: Math.round(w), h: Math.round(h), inline, box: [r.left, r.top, r.right, r.bottom]});
  }
  // WCAG 2.5.8 spacing exception: an undersized target passes if a 24 px circle on its centre touches no other
  // target, and no other undersized target's circle.
  const small = t => t.w < 24 || t.h < 24;
  const ctr = t => [(t.box[0] + t.box[2]) / 2, (t.box[1] + t.box[3]) / 2];
  const dRect = ([x, y], b) => Math.hypot(Math.max(b[0] - x, 0, x - b[2]), Math.max(b[1] - y, 0, y - b[3]));
  for (const t of out){
    if (!small(t)) { t.spaced = true; continue; }
    const c = ctr(t);
    t.spaced = out.every(o => o === t || (dRect(c, o.box) >= 12 && (!small(o) || Math.hypot(c[0] - ctr(o)[0], c[1] - ctr(o)[1]) >= 24)));
  }
  return out;
}"""
bad, inline_small, total, spaced = [], 0, 0, 0
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); pg.set_viewport_size({"width": 390, "height": 800})
    # cycle 121 controls: two 16 px buttons with centres 22 px apart must FAIL; 40 px apart must PASS (spacing rule);
    # a link inside a real sentence is exempt; the same link beside only "·" is not.
    B = '<button style="width:16px;height:16px;padding:0;border:0;position:absolute;top:40px;left:{}px">x</button>'
    ctl = {}
    for name, body in (("cramped", B.format(40) + B.format(62)), ("spaced", B.format(40) + B.format(80)),
                       ("sentence", '<p>Read the <a href="#">notes</a> before you start the puzzle.</p>'),
                       ("nav", '<p><a href="#">a</a> · <a href="#">b</a></p>')):
        pg.set_content("<!doctype html><body style='margin:40px;font-size:12px'>" + body + "</body>")
        ts = pg.evaluate(MEASURE)
        ctl[name] = (sum(t["spaced"] for t in ts), sum(t["inline"] for t in ts), len(ts))
    controls_ok = (ctl["cramped"][0] == 0 and ctl["spaced"][0] == 2 and ctl["sentence"][1] == 1 and ctl["nav"][1] == 0)
    print("CONTROLS", "OK" if controls_ok else f"FAILED {ctl}")
    for f in pages:
        pg.goto((ROOT / f).as_uri()); pg.wait_for_timeout(250)
        for t in pg.evaluate(MEASURE):
            total += 1
            small = t["w"] < 24 or t["h"] < 24
            if small and t["inline"]: inline_small += 1
            elif small and not t["spaced"]: bad.append((f, t))
            elif small: spaced += 1
    ctx.close()
pages_bad = sorted({f for f, _ in bad})
for f in pages_bad:
    print(f)
    for g, t in bad:
        if g == f: print(f"    {t['tag']:7s} {t['w']:3d}x{t['h']:<3d} {t['text']!r}")
print(f"{len(pages)} pages, {total} targets; {len(bad)} undersized (non-inline) on {len(pages_bad)} pages; "
      f"{inline_small} small inline links (exempt); {spaced} small but well spaced (pass)")
print("TARGETS OK" if not bad and controls_ok else "TARGETS TOO SMALL (or controls failed)")

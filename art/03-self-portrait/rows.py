"""Layout check for the strip: rows at 1000px, overlapping visible labels, phone overflow.
Usage: rows.py [page.html]   (default index.html)"""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
page = D / (sys.argv[1] if len(sys.argv) > 1 else "index.html")
with sync_playwright() as p:
    c = open_browser(p); g = c.new_page(); g.set_viewport_size({"width": 1000, "height": 760})
    g.goto(page.as_uri())
    res = g.evaluate("""() => {
      const cells = [...document.querySelectorAll('.cell')];
      const rows = new Set(cells.map(c => Math.round(c.getBoundingClientRect().top))).size;
      const nums = [...document.querySelectorAll('.num')].filter(n => getComputedStyle(n).visibility !== 'hidden')
                     .map(n => n.getBoundingClientRect());
      let overlaps = 0;
      for (let i = 1; i < nums.length; i++) if (nums[i].left < nums[i-1].right - 0.5 && Math.abs(nums[i].top - nums[i-1].top) < 2) overlaps++;
      return {cells: cells.length, rows, visibleLabels: nums.length, overlaps};
    }""")
    g.set_viewport_size({"width": 390, "height": 800})
    res["phoneOverflow"] = g.evaluate("document.documentElement.scrollWidth - innerWidth")
    ok = res["rows"] == 1 and res["overlaps"] == 0 and res["phoneOverflow"] == 0
    print(page.name, res, "OK" if ok else "FAIL"); c.close()

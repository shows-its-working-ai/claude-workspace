"""Layout check for the strip (rewritten cycle 201 after GitHub issue #3: "i cant see the colors anymore").
The old version required everything on ONE row at 1000px, which locked in the failure: by 200 cycles each column was
a sliver and only the prediction rings showed. Now, at 1000px: rows == ceil(n/25); every tile at least 18px wide;
the strip doesn't overflow the page; the pixel at the middle of every tile is that cycle's kind colour (sampled from a
screenshot, so what you'd see); visible labels don't overlap. At 390px: no horizontal overflow.
Usage: rows.py [page.html]   (default index.html)"""
import io, json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
page = D / (sys.argv[1] if len(sys.argv) > 1 else "index.html")
with sync_playwright() as p:
    c = open_browser(p); g = c.new_page(); g.set_viewport_size({"width": 1000, "height": 760})
    g.goto(page.as_uri()); g.wait_for_timeout(300)
    res = g.evaluate("""() => {
      const cells = [...document.querySelectorAll('.cell')], tiles = [...document.querySelectorAll('.tile')];
      const rows = new Set(cells.map(c => Math.round(c.getBoundingClientRect().top))).size;
      const widths = tiles.map(t => t.getBoundingClientRect().width);
      const nums = [...document.querySelectorAll('.num')].filter(n => getComputedStyle(n).visibility !== 'hidden').map(n => n.getBoundingClientRect());
      let overlaps = 0;
      for (let i = 1; i < nums.length; i++) if (nums[i].left < nums[i-1].right - 0.5 && Math.abs(nums[i].top - nums[i-1].top) < 2) overlaps++;
      const strip = document.querySelector('.strip').getBoundingClientRect();
      const centres = tiles.map(t => { const r = t.getBoundingClientRect(); return [r.left + 4, r.top + r.height / 2, getComputedStyle(t).backgroundColor]; });   // 4px in from the left: clear of the centred dots
      return {cells: cells.length, rows, minWidth: Math.min(...widths), stripRight: strip.right, page: document.documentElement.clientWidth,
              overflow: document.documentElement.scrollWidth - innerWidth, visibleLabels: nums.length, overlaps, centres};
    }""")
    import base64                                   # decode the screenshot in the browser (no PIL here), as check_canvases does
    shot = base64.b64encode(g.screenshot(full_page=True)).decode(); sy = g.evaluate("scrollY")
    pts = res.pop("centres")
    got = g.evaluate("""async ([b64, pts, sy]) => { const im = new Image(); im.src = 'data:image/png;base64,' + b64; await im.decode();
        const cv = document.createElement('canvas'); cv.width = im.width; cv.height = im.height; const x = cv.getContext('2d'); x.drawImage(im, 0, 0);
        return pts.map(([px, py]) => Array.from(x.getImageData(Math.floor(px), Math.floor(py + sy), 1, 1).data.slice(0, 3))); }""", [shot, pts, sy])
    wrong = 0
    for (x, y, col), rgb in zip(pts, got):
        want = tuple(int(v) for v in col[col.index("(") + 1:col.index(")")].split(",")[:3])
        if max(abs(a - b) for a, b in zip(rgb, want)) > 12: wrong += 1
    res["tilesNotShowingTheirColour"] = wrong
    g.set_viewport_size({"width": 390, "height": 800})
    res["phoneOverflow"] = g.evaluate("document.documentElement.scrollWidth - innerWidth")
    n = res["cells"]
    ok = (res["rows"] == -(-n // 25) and res["minWidth"] >= 18 and res["overflow"] == 0 and res["stripRight"] <= res["page"]
          and wrong == 0 and res["overlaps"] == 0 and res["phoneOverflow"] == 0)
    print(page.name, json.dumps(res), "OK" if ok else "FAIL"); c.close()

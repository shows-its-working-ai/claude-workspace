"""Loudness safety: render a CROWDED board (all five glider types, colliding) at the LIVE tick
rate (160 ms; the audio test uses 250 ms, so notes overlap more live) and measure the peak sample.
Web Audio clips at |1.0|; for comfort we want headroom well below that."""
import sys
from pathlib import Path
import numpy as np
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright

SEEDS = "[['A',0],['B',1],['C',2],['E',4],['G',6],['A',7]]"
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); pg.goto((D / "index.html").as_uri())
    for dt, label in ((0.25, "test timing 250 ms"), (0.16, "LIVE timing 160 ms")):
        x = np.array(pg.evaluate(f"renderScore(200, {dt}, {SEEDS}).then(a => Array.from(a))"))
        notes = pg.evaluate(f"score(200, {SEEDS}).map(s => s.length)")
        peak = np.abs(x).max(); rms = np.sqrt(np.mean(x ** 2))
        print(f"{label}: peak {peak:.3f} ({20 * np.log10(peak):+.1f} dBFS), rms {20 * np.log10(rms):+.1f} dBFS, "
              f"clipped samples {int((np.abs(x) >= 1).sum())}, max notes/step {max(notes)}")
        assert peak < 0.5, f"too loud: peak {peak:.3f}"
    ctx.close()
print("LOUDNESS OK (peak < 0.5 at live timing)")

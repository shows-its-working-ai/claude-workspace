"""Loudness safety for Beat Rates: render the loudest-looking intervals exactly as playback does
(two harmonic voices, 6 s) and measure the peak sample. Web Audio clips at |1.0|."""
import sys
from pathlib import Path
import numpy as np
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
from beats import freq
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); pg.goto((D / "index.html").as_uri())
    worst = 0
    for lo, semis in ((53, 7), (60, 4), (65, 3), (77, 9), (53, 12)):
        x = np.array(pg.evaluate(f"""(async () => {{
          const c = new OfflineAudioContext(1, 44100 * 6, 44100);
          voices(c, {freq(lo)}, {freq(lo + semis)}, c.destination, 0, 6);
          return Array.from((await c.startRendering()).getChannelData(0)); }})()"""))
        pk = np.abs(x).max(); worst = max(worst, pk)
        print(f"lo={lo} +{semis} semitones: peak {pk:.3f} ({20 * np.log10(pk):+.1f} dBFS)")
    print(f"worst peak {worst:.3f}, clipping {'YES' if worst >= 1 else 'no'}")
    assert worst < 0.5, f"too loud: {worst:.3f}"
    print("LOUDNESS OK (peak < 0.5)")
    ctx.close()

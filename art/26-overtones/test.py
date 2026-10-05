"""Hidden Notes: the page's 16 notes and cents == overtones.py; the page's OWN audio, rendered offline and FFT'd:
a single overtone's peak sits at n x C2 within one bin (n = 1, 3, 7, 11, 16); the ladder plays overtone i+1 in slot i;
all sixteen together repeat at C2's period (autocorrelation peak) and contain all 16 peaks; audible, never clips;
pressing play twice leaves ONE live bus (cycle 203 bug class); control: a wrong frequency is SEEN by the same FFT
check; the page says it can't hear it; phone 0; no JS errors."""
import json, sys
from pathlib import Path
import numpy as np
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
py = json.loads((D / "overtones.json").read_text(encoding="utf-8")); C2 = py["c2"]; RATE = 22050
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
def peak(x, t, n=16384):
    i = int(t * RATE); seg = np.asarray(x[i:i + n]) * np.hanning(n); m = np.abs(np.fft.rfft(seg)); f = np.fft.rfftfreq(n, 1 / RATE)
    return f[int(np.argmax(m[5:])) + 5], RATE / n, m, f
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.hiddenApi !== undefined")
    rows = pg.evaluate("hiddenApi.ROWS")
    check("16 notes and cents == overtones.py", [(r["note"], r["cents"]) for r in rows] == [(r["note"], r["cents"]) for r in py["rows"]]
          and abs(pg.evaluate("hiddenApi.C2") - C2) < 1e-9)
    for n in (1, 3, 7, 11, 16):
        x = pg.evaluate(f"hiddenApi.render('one', [{n}], 1.6)"); f, bw, *_ = peak(x, 0.2)
        check(f"overtone {n}: FFT peak at {n} x C2 = {n * C2:.2f} Hz within a bin", abs(f - n * C2) <= bw, f"{f:.2f} Hz (bin {bw:.2f})")
    f7, bw, *_ = peak(pg.evaluate("hiddenApi.render('one', [7], 1.6)"), 0.2)
    check("control: the same check rejects a wrong frequency (7 x C2 vs 7.1 x C2)", abs(f7 - 7.1 * C2) > bw)
    lad = pg.evaluate("hiddenApi.render('ladder', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16], 9.0)")
    hits = [abs(peak(lad, i * 0.55 + 0.1, 4096)[0] - (i + 1) * C2) <= RATE / 4096 for i in range(16)]
    check("ladder: slot i plays overtone i+1 (all 16 slots)", all(hits), str([i + 1 for i, h in enumerate(hits) if not h]))
    al = np.asarray(pg.evaluate("hiddenApi.render('all', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16], 3.0)"))
    seg = al[int(0.5 * RATE): int(0.5 * RATE) + 8192]; ac = np.correlate(seg, seg, "full")[len(seg) - 1:]
    lag = int(np.argmax(ac[200:500])) + 200
    check("all together repeat at C2's period (autocorrelation)", abs(lag - RATE / C2) <= 1.5, f"lag {lag} vs {RATE / C2:.1f} samples")
    _, bw, m, f = peak(al, 0.5)
    present = [m[int(round(n * C2 / bw)) - 1: int(round(n * C2 / bw)) + 2].max() > 0.2 * m.max() for n in range(1, 17)]
    check("all together: all 16 overtones present in the spectrum", all(present), str([n for n, q in zip(range(1, 17), present) if not q]))
    pk, rms = float(np.abs(al).max()), float(np.sqrt((al ** 2).mean()))
    check("audible and never clips (all sixteen)", 0.02 < rms and pk < 1.0, f"rms {rms:.3f} peak {pk:.3f}")
    pg.click("#up"); pg.wait_for_timeout(100); pg.click("#up"); pg.wait_for_timeout(400)
    check("play pressed twice: exactly one live bus", pg.evaluate("hiddenApi.live()") == 1, str(pg.evaluate("hiddenApi.live()")))
    pg.click("#grid button[data-n='11']"); pg.wait_for_timeout(300)
    check("tapping 11: says F#5, -48.68 cents; still one live bus", "nearest F#5, -48.68 cents" in pg.inner_text("#msg") and pg.evaluate("hiddenApi.live()") == 1)
    pg.click("#stop"); pg.wait_for_timeout(300)
    check("stop: no live buses", pg.evaluate("hiddenApi.live()") == 0)
    check("the page says it can't hear it", "can't hear" in pg.inner_text("main"))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 760, "height": 1000}); pg.click("#grid button[data-n='7']")
    pg.screenshot(path=str(D.parents[1] / "tools" / "_overtones_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")

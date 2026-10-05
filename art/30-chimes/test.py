"""Wind Chimes: renders the page's OWN sound offline (seeded) and checks: (a) every isolated strike's strongest
frequency is its chime's note (D5 E5 F#5 A5 B5) within an FFT bin; (b) strikes per 10 s grow with the wind (0 at
wind 0; mean over 20 seeds ~ 5*100*w^2*0.08: 32 at 0.9, 1.6 at 0.2); (c) same seed -> identical strikes, samples equal to 1e-6 (offline renders differ by float rounding);
(d) audible and never clips at full gale; one live bus after Start/Stop/Start; (e) the page says it can't hear it;
control for (a): the same check rejects a wrong note."""
import sys
from pathlib import Path
import numpy as np
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
RATE = 22050
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
def peak(x, t, n=4096):
    i = int(t * RATE); seg = np.asarray(x[i:i + n]) * np.hanning(n); m = np.abs(np.fft.rfft(seg)); f = np.fft.rfftfreq(n, 1 / RATE)
    return f[int(np.argmax(m[20:])) + 20], RATE / n
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.chimesApi !== undefined")
    # cycle 238: the expected notes were read FROM THE PAGE, so a mistuned page passed (a mutant survived). They are
    # computed here, independently: D5 E5 F#5 A5 B5 are -7, -5, -3, 0 and +2 semitones from A5 = 880 Hz.
    notes = [880 * 2 ** (k / 12) for k in (-7, -5, -3, 0, 2)]
    check("the page's five notes are D5 E5 F#5 A5 B5 (computed here from A = 440)", all(abs(a - b) < 0.01 for a, b in zip(pg.evaluate("chimesApi.NOTES"), notes)))
    r = pg.evaluate("chimesApi.render(0.35, 23.5, 11)"); x, lst = r["samples"], r["list"]
    iso = [s for k, s in enumerate(lst) if all(abs(s["t"] - o["t"]) >= 0.45 or o is s for o in lst if o["t"] <= s["t"])]
    res = [(s, *peak(x, s["t"] + 0.01)) for s in iso]
    good = [abs(f - notes[s["i"]]) <= bw for s, f, bw in res]
    check(f"(a) each isolated strike's strongest frequency is its chime's note ({len(res)} strikes)", len(res) >= 5 and all(good), str([(round(f), round(notes[s['i']])) for s, f, bw in res][:6]))
    s, f, bw = res[0]; wrong = notes[(s["i"] + 1) % 5]
    check("control: the same check would reject the neighbouring note", abs(f - wrong) > bw)
    rates = {w: np.mean([len(pg.evaluate(f"chimesApi.strikes({w}, 10, chimesApi.rng({sd}))")) for sd in range(20)]) for w in (0, 0.2, 0.9)}
    check("(b) strikes per 10 s: none at 0, ~1.6 at 0.2, ~32 at 0.9 (20 seeds)", rates[0] == 0 and 0.5 <= rates[0.2] <= 3.5 and 26 <= rates[0.9] <= 38, str(rates))
    r2 = pg.evaluate("chimesApi.render(0.35, 23.5, 11)")
    dmax = float(np.abs(np.asarray(r2["samples"]) - np.asarray(x)).max())   # cycle 238: renders differ by float32 rounding (~3e-8)
    check("(c) same seed: identical strikes; samples equal to within 1e-6", r2["list"] == lst and dmax < 1e-6, f"max diff {dmax:.1e}")
    g = np.asarray(pg.evaluate("chimesApi.render(1.0, 13.5, 3)")["samples"]); pk, rms = float(np.abs(g).max()), float(np.sqrt((g ** 2).mean()))
    check("(d) full gale: audible and never clips", 0.02 < rms and pk < 1.0, f"rms {rms:.3f} peak {pk:.3f}")
    q = np.asarray(pg.evaluate("chimesApi.render(0, 5, 3)")["samples"]); check("wind 0: silence", float(np.abs(q).max()) == 0.0)
    pg.click("#go"); pg.wait_for_timeout(200); pg.click("#go"); pg.wait_for_timeout(200); pg.click("#go"); pg.wait_for_timeout(300)
    check("Start/Stop/Start: exactly one live bus", pg.evaluate("chimesApi.live()") == 1, str(pg.evaluate("chimesApi.live()")))
    pg.click("#go"); pg.wait_for_timeout(200)
    check("(e) the page says it can't hear it", "can't hear" in pg.inner_text("main"))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 700, "height": 1000}); pg.screenshot(path=str(D.parents[1] / "tools" / "_chimes_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")

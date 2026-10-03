"""Fact-check for writing/08-the-rating-nut.md: recompute every physics number the story states, and check the
story still states them (so an edit can't silently break the numbers)."""
import math
from pathlib import Path
s = (Path(__file__).resolve().parent / "08-the-rating-nut.md").read_text(encoding="utf-8")
g, T, alpha, dT, day = 9.81, 2.0, 12e-6, 10, 86400
ok = True
def check(name, cond, detail):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name}: {detail}")
L = g * T ** 2 / (4 * math.pi ** 2)
check("seconds pendulum length", "99.4 cm" in s and abs(L * 100 - 99.4) < 0.05, f"{L * 100:.2f} cm")
dL = L * alpha * dT
check("growth at +10 K", "0.12 mm" in s and abs(dL * 1000 - 0.12) < 0.005, f"{dL * 1000:.4f} mm")
frac = 0.5 * alpha * dT
check("fractional slowing", "6 × 10⁻⁵" in s and abs(frac - 6e-5) < 1e-9, f"{frac:.2e}")
lost = frac * day
check("seconds lost per day", "5.2 seconds" in s and "about five seconds a day" in s.lower() and abs(lost - 5.2) < 0.05, f"{lost:.2f} s")
check("swings per day", "Eighty-six thousand four hundred swings a day" in s and day / (T / 2) == 86400, "one swing per second")
# the rating nut: "one notch is about a second a day" -> how far must the bob move? (shorter = gains)
per_notch = 1 / day                                # fractional rate change per notch
dL_notch = 2 * per_notch * L                       # dT/T = dL/(2L)  ->  dL = 2 L (dT/T)
pitch_mm = dL_notch * 1000 * 20                    # if the nut had 20 notches per turn, thread pitch in mm
check("notch -> bob movement is a buildable size", 0.01 < dL_notch * 1000 < 0.1,
      f"{dL_notch * 1000:.3f} mm per notch; with 20 notches/turn that's a {pitch_mm:.2f} mm thread")
# five notches (story) should roughly cancel the 5.2 s/day summer loss; "minute and a half since May" ~ 3 weeks of drift
check("five notches ~ cancels the loss", "five notches" in s and abs(5 * 1 - lost) < 0.5, f"5 x 1 s/day vs {lost:.2f} s/day")
check("minute and a half lost", "minute and a half" in s and 14 < 90 / lost < 25, f"90 s at {lost:.2f} s/day = {90 / lost:.0f} days of warm weather")
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")

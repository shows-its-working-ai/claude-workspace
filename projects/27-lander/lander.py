"""Last Burn: a 1-D Moon lander, simulated exactly as the page does (fixed step 1/120 s, semi-implicit Euler).
Predictions (journal, cycle 221): (a) least fuel = suicide burn to 2 m/s, ~5.02 s analytically; (b) the simulated
suicide burn lands softly within 2 steps of it; (c) no single-switch time or random pulse pattern lands softly on less.
Control: burning from t = 0 doesn't land (it climbs)."""
import json, math, random
from pathlib import Path
D = Path(__file__).resolve().parent
G, A, H0, SOFT, DT = 1.62, 4.0, 100.0, 2.0, 1 / 120

def fly(burn, max_steps=120 * 120):          # burn(step, h, v) -> bool; v is DOWNWARD speed (positive = falling)
    h, v, fuel = H0, 0.0, 0
    for k in range(max_steps):
        on = burn(k, h, v)
        v += (G - (A if on else 0)) * DT; h -= v * DT; fuel += on
        if h <= 0: return {"landed": True, "v": v, "soft": v <= SOFT, "fuel": fuel * DT, "steps": k + 1}
    return {"landed": False, "v": v, "soft": False, "fuel": fuel * DT, "steps": max_steps}

v_sw = math.sqrt((2 * H0 * G * (A - G) + G * SOFT ** 2) / A); best = (v_sw - SOFT) / (A - G)
print(f"(a) analytic: switch at {v_sw:.4f} m/s, least fuel {best:.4f} s")
# cycle 221: my first autopilot used the continuous formula h <= (v^2 - u^2) / 2(a-g) and touched down at 2.026 m/s,
# just over the limit: continuous maths on a stepped simulation. This one looks ahead in the SAME stepped physics:
# burn now only if coasting one more step would leave no soft landing even at full thrust.
def can_land(h, v):                     # full thrust from here: soft touchdown (or stopped above ground)?
    if h <= 0: return v <= SOFT         # already down (my first look-ahead stepped once more before checking: 2.019)
    while True:
        v += (G - A) * DT; h -= v * DT
        if h <= 0: return v <= SOFT
        if v <= 0: return True          # stopped short; from here it can always settle
def suicide(k, h, v):
    v2 = v + G * DT; return not can_land(h - v2 * DT, v2)
r = fly(suicide)
print(f"(b) simulated suicide burn: soft {r['soft']}, v {r['v']:.3f}, fuel {r['fuel']:.4f} s, within 2 steps: {abs(r['fuel'] - best) <= 2 * DT}")
# (c) single switch: coast k0 steps, then burn until ground (or until slower than SOFT/2, to avoid climbing)
singles = []
for k0 in range(0, 1400):
    s = fly(lambda k, h, v, k0=k0: k >= k0 and v > 0.5)
    if s["soft"]: singles.append((s["fuel"], k0))
# random pilots: a random pulse pattern until a random hand-over step, then the look-ahead autopilot (so they LAND,
# and the comparison isn't vacuous; my first version had 0 of 20,000 land softly)
rng = random.Random(221); beat = 0; soft_random = 0
for _ in range(2000):
    pulses = sorted((rng.randint(0, 900), rng.randint(5, 200)) for _ in range(rng.randint(1, 4))); hand = rng.randint(0, 1000)
    s = fly(lambda k, h, v, P=pulses, H=hand: (any(a <= k < a + d for a, d in P) or not can_land(h - (v + G * DT) * DT, v + G * DT)) if k < H else suicide(k, h, v))
    if s["soft"]:
        soft_random += 1; beat += s["fuel"] < best - 2 * DT
print(f"(c) single-switch times that land softly: {len(singles)}; least fuel among them {min(singles)[0]:.4f} s; below the optimum: {sum(f < best - 2 * DT for f, _ in singles)}")
print(f"(c) random pilots: {soft_random} of 2,000 land softly; any on less fuel: {beat}")
c = fly(lambda k, h, v: True, max_steps=120 * 60)
print(f"control: burning from the start lands: {c['landed']} {'SEEN' if not c['landed'] else 'NOT SEEN'}")
held = soft_random >= 1500 and r["soft"] and abs(r["fuel"] - best) <= 2 * DT and not any(f < best - 2 * DT for f, _ in singles) and beat == 0
print("PREDICTION HELD" if held else "PREDICTION FAILED")
json.dump({"best": best, "suicide": r, "g": G, "a": A, "h0": H0, "soft": SOFT, "dt": DT}, open(D / "lander.json", "w"), indent=1)

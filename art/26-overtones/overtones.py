"""Hidden Notes: the harmonic series over C2, against the piano's equal temperament.
Predictions (journal, cycle 222): (a) 1,2,4,8,16 exact; (b) 3rd G +1.96, 5th E -13.69, 7th Bb -31.17; (c) the worst of
1-16 is the 11th, F# -48.68. Control: the piano fifth (700 c) vs 3:2 differs by 1.955 c - SEEN."""
import json, math
from pathlib import Path
D = Path(__file__).resolve().parent
C2 = 440 * 2 ** (-33 / 12)                        # C2, 33 semitones below A4
NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
rows = []
for n in range(1, 17):
    c = 1200 * math.log2(n); k = round(c / 100); off = c - 100 * k
    rows.append({"n": n, "hz": round(n * C2, 3), "note": NAMES[k % 12] + str(2 + k // 12), "cents": round(off, 2)})
    print(f"{n:2d}  {n * C2:8.3f} Hz  {rows[-1]['note']:>4}  {off:+7.2f} c")
R = {r["n"]: r for r in rows}
a = all(R[n]["cents"] == 0 for n in (1, 2, 4, 8, 16))
b = (R[3]["note"], R[3]["cents"]) == ("G3", 1.96) and (R[5]["note"], R[5]["cents"]) == ("E4", -13.69) and (R[7]["note"], R[7]["cents"]) == ("Bb4", -31.17)
worst = max(rows, key=lambda r: abs(r["cents"]))
c = worst["n"] == 11 and worst["note"] == "F#5" and worst["cents"] == -48.68
print(f"(a) 1, 2, 4, 8, 16 exact: {a}\n(b) 3rd G3 +1.96, 5th E4 -13.69, 7th Bb4 -31.17: {b}\n(c) worst is the 11th, {worst['note']} {worst['cents']:+.2f}: {c}")
ctl = 1200 * math.log2(1.5) - 700
print(f"control: piano fifth vs 3:2 differs by {ctl:.3f} cents {'SEEN' if abs(ctl) > 1 else 'NOT SEEN'}")
print("PREDICTION HELD" if a and b and c else "PREDICTION FAILED")
json.dump({"c2": C2, "rows": rows}, open(D / "overtones.json", "w"), indent=1)

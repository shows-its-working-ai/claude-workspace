"""First Digits: Benford's law on my own site. Takes the VISIBLE text of every published page (art, projects,
writing; scripts and styles removed, tags stripped), finds every number, and counts first significant digits.
Predictions (journal, cycle 223): (a) 1 is the most common; (b) its share is 25-40%; (c) GUESS: chi-square REJECTS
Benford at 5% (critical 15.51, 8 df), but the shares mostly decrease from 1 to 9. Control: uniform digits fail it."""
import json, math, re, subprocess, sys
from collections import Counter
from pathlib import Path
D = Path(__file__).resolve().parent; ROOT = D.parents[1]
files = sorted(f for f in subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True).stdout.split()
               if re.fullmatch(r"(art|projects)/[^/]+/index\.html|writing/[^/]+\.html|writing/[^/]+/index\.html", f) and "27-first-digits" not in f)
def visible(html):
    html = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", html)
    return re.sub(r"&[a-z#0-9]+;", " ", re.sub(r"<[^>]+>", " ", html))
nums = []; raw = []
for f in files:
    for m in re.finditer(r"(?<![\w.])\d[\d,]*(?:\.\d+)?", visible((ROOT / f).read_text(encoding="utf-8", errors="ignore"))):
        sig = m.group().replace(",", "").lstrip("0.").lstrip("0")
        if sig and sig[0].isdigit() and sig[0] != "0": nums.append(int(sig[0])); raw.append(m.group().replace(',', ''))
n = len(nums); cnt = Counter(nums); obs = [cnt[d] for d in range(1, 10)]
ben = [math.log10(1 + 1 / d) for d in range(1, 10)]
chi = sum((o - n * b) ** 2 / (n * b) for o, b in zip(obs, ben))
print(f"pages: {len(files)}; numbers: {n}")
for d in range(1, 10): print(f"  {d}: {obs[d - 1]:5d}  {obs[d - 1] / n:6.1%}   Benford {ben[d - 1]:6.1%}")
print(f"chi-square vs Benford: {chi:.2f} (8 df; 5% critical value 15.51)")
a = max(range(9), key=lambda i: obs[i]) == 0; b = 0.25 <= obs[0] / n <= 0.40
down = sum(obs[i] >= obs[i + 1] for i in range(8))
print(f"(a) 1 is the most common first digit: {a}\n(b) its share {obs[0] / n:.1%} is in 25-40%: {b}")
print(f"(c) GUESS chi-square rejects Benford: {chi > 15.51}; shares decrease at {down} of 8 steps")
big = [r for r in raw if float(r) >= 10]; cb = Counter(r.lstrip("0.")[0] for r in big)
print(f"numbers of 10 or more: {len(big)}; starting with 1: {cb['1'] / len(big):.1%}")
years = sum(1 for r in raw if r.isdigit() and 1000 <= int(r) <= 1999); r110 = raw.count("110")
print(f"of those: '110' appears {r110} times; numbers from 1000 to 1999 {years} times")
uni = sum((n / 9 - n * bb) ** 2 / (n * bb) for bb in ben)
print(f"control: uniform digits, same n: chi-square {uni:.1f} {'SEEN' if uni > 15.51 else 'NOT SEEN'}")
print("PREDICTION HELD" if a and b and chi > 15.51 else "PREDICTION FAILED")
# cycle 223: the site grows, so these counts change every cycle (the cycle-183 trap). The page shows a SNAPSHOT;
# only "--snapshot" rewrites it. Everyday runs just report the current numbers.
if "--snapshot" in sys.argv: json.dump({"cycle": 223, "pages": len(files), "n": n, "big": len(big), "big1": cb["1"], "r110": r110, "years": years, "observed": obs, "benford": ben, "chi": chi}, open(D / "digits.json", "w"), indent=1)

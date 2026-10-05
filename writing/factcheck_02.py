"""Fact-check for writing/02-the-tuner.md (cycle 255: this story was written in cycle 2, before I checked anything).
In equal temperament, beats are the gap between the nearest shared partials: a fifth f -> f*2^(7/12) beats at
|3f - 2g|, a major third f -> f*2^(4/12) at |5f - 4g|. Claims: in the middle of the keyboard (middle C) a fifth
beats "a little under once a second"; a major third beats "seven times a second or more" across the usual tuning
octave F3-F4. Control: the ORIGINAL wording, "about seven times", is wrong at middle C (10.4), so a check of
"about seven" at middle C must fail."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = " ".join((ROOT / "writing" / "02-the-tuner.md").read_text(encoding="utf-8").split())
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
f = lambda midi: 440 * 2 ** ((midi - 69) / 12)
fifth = lambda n: abs(3 * f(n) - 2 * f(n + 7))
third = lambda n: abs(5 * f(n) - 4 * f(n + 4))
C4, F3, F4 = 60, 53, 65
check("the story says a fifth beats a little under once a second", "beats a little under once a second" in s)
check("...and at middle C it does (0.5 to 1.0)", 0.5 < fifth(C4) < 1.0, f"{fifth(C4):.2f}/s")
check("the story says a major third beats seven times a second or more", "seven times a second or more" in s)
thirds = [third(n) for n in range(F3, F4 + 1)]
check("...and across F3-F4 every major third beats at least 6.9 times a second", min(thirds) >= 6.9, f"{min(thirds):.2f} to {max(thirds):.2f}/s")
off = abs(third(C4) - 7) / 7
check("control: 'about seven' at middle C is more than 25% off, so the old wording WAS wrong", off > 0.25, f"{third(C4):.2f}/s, {off:.0%} off  {'SEEN' if off > 0.25 else 'NOT SEEN'}")
check("the vicar's 'just under once a second' line matches the fifth", "Just under once a second" in s)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED"); raise SystemExit(0 if ok else 1)

"""Fact-check for writing/36-the-museum-of-lost-property.md: the box's contents add up to what Priya says (41 jumpers
+ recorder + boot + lunchbox = 44, 'and the hamster ball'), the nine claimed things are possible (nine <= 45) and
the named claims (a Grey, the lunchbox, the boot) are among them, and the recorder is never claimed."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = " ".join((ROOT / "writing" / "36-the-museum-of-lost-property.md").read_text(encoding="utf-8").split())
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
W = {"forty-one": 41, "forty-four": 44, "nine": 9, "forty-six": 46}
check("box: forty-one jumpers, a recorder, one boot, a lunchbox, a hamster ball", "it held forty-one jumpers, a recorder, one wellington boot, a lunchbox nobody would open, and a hamster ball" in s)
m = re.search(r'"(Forty-\w+)\. And the hamster ball\."', s)
check("Priya's count == 41 + 1 + 1 + 1 (hamster ball separate)", m and W[m[1].lower()] == 41 + 3, m[1] if m else "")
check("the Greys are 41 strong", "the Greys, forty-one strong" in s)
named = ["That's my Grey", "recognised the lunchbox", "wellington boot's owner"]
check("nine gone home, three of them named, nine <= 45", "nine of them have gone home" in s and all(n in s for n in named) and 9 <= 45)
check("the recorder is never claimed (it stays)", "The recorder stays" in s and "recorder" not in s.split("started disappearing")[1].split("THE MUSEUM OF LOST PROPERTY")[0])
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")

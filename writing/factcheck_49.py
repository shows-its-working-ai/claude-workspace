"""Form check for writing/49-going-without.md, a lipogram: no letter e (either case) anywhere in the story below the
line, nor in its title. Control: the note above the line, which is outside the rule, DOES contain e, so the check is
reading the right part of the file and can see the letter when it's there."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "writing" / "49-going-without.md").read_text(encoding="utf-8")
head, body = text.split("\n---\n", 1)
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
hits = [i for i, ch in enumerate(body) if ch in "eE"]
check("no 'e' anywhere in the story", not hits and len(body.split()) > 250, f"{len(body.split())} words; e at {hits[:3]}")
check("no 'e' in the title", "e" not in text.splitlines()[0].lower(), text.splitlines()[0])
seen = "e" in head.split("\n", 1)[1].lower()
check("control: the note above the line does contain 'e'", seen, "SEEN" if seen else "NOT SEEN")
print("FACTCHECK OK" if ok else "FACTCHECK FAILED"); raise SystemExit(0 if ok else 1)

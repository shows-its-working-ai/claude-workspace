"""Exact text replacement that refuses to fail silently (cycle 154).
sed reports nothing when its pattern doesn't match; three times now an edit "succeeded" without changing anything
(cycles 109, 153, ...), and once a too-broad one changed 25 lines instead of 1 (cycle 148).

    python tools/replace.py FILE OLD NEW [--count N]

OLD and NEW are literal text (no regex). Python-style escapes are NOT interpreted, so pass real newlines via a file:
    python tools/replace.py FILE --from-files old.txt new.txt
Exits 1, changing nothing, unless OLD occurs exactly N times (default 1). Prints what it did."""
import sys
from pathlib import Path
args = sys.argv[1:]
count = 1
if "--count" in args:
    i = args.index("--count"); count = int(args[i + 1]); del args[i:i + 2]
if len(args) == 4 and args[1] == "--from-files":
    path, old, new = Path(args[0]), Path(args[2]).read_bytes().decode("utf-8"), Path(args[3]).read_bytes().decode("utf-8")
elif len(args) == 3:
    path, old, new = Path(args[0]), args[1], args[2]
else:
    print(__doc__); sys.exit(2)
text = path.read_bytes().decode("utf-8")          # bytes, not text mode: text mode rewrote line endings (cycle 154)
n = text.count(old)
if n != count:
    print(f"REPLACE REFUSED: {path} has {n} occurrence(s) of the text, expected {count}. Nothing changed.")
    sys.exit(1)
path.write_bytes(text.replace(old, new).encode("utf-8"))
print(f"replaced {n} occurrence(s) in {path}")

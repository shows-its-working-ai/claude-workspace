"""Every tracked .py file must compile (cycle 155: a SyntaxError in tools/mutate.py was committed, because the quick
gate never imports it and a pipe hid the failing command's exit code)."""
import py_compile, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
files = [f for f in subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.py"], cwd=ROOT, capture_output=True, text=True).stdout.split() if f]
bad = []
for f in files:
    try: py_compile.compile(str(ROOT / f), doraise=True, cfile=str(ROOT / "__pycache__" / "_compile_check.pyc"))
    except py_compile.PyCompileError as e: bad.append(f"{f}: {e.msg.splitlines()[-1] if e.msg else e}")
print(f"{len(files)} tracked .py files; {len(bad)} fail to compile")
for b in bad: print("  ", b)
print("COMPILE OK" if not bad else "COMPILE FAILED")

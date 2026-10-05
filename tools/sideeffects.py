"""Snapshot and restore what a check might change (cycle 253).
cycle 125: a check run against a mutant rewrote a TRACKED data file; mutate.py learned to put those back from git.
cycle 252: a mutant made coast.py rewrite coast.json while it was still UNTRACKED (new that cycle), so git couldn't
put it back and the next baseline failed. Now untracked (not ignored) files are snapshotted by content too.
New untracked files a check creates are reported, never deleted: they might not be mine to remove."""
import subprocess
from pathlib import Path

def _git(root, *args):
    return [l for l in subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout.split("\n") if l]

class Snapshot:
    def __init__(self, root, untracked=True):
        self.root = Path(root); self.untracked = untracked
        self.dirty = {g: (self.root / g).read_bytes() for g in _git(root, "diff", "--name-only")}
        self.loose = {g: (self.root / g).read_bytes() for g in _git(root, "ls-files", "--others", "--exclude-standard")} if untracked else {}

    def restore(self):
        """Put everything back. Returns the list of NEW untracked files (left in place)."""
        for g in _git(self.root, "diff", "--name-only"):
            if g in self.dirty: (self.root / g).write_bytes(self.dirty[g])
            else: subprocess.run(["git", "checkout", "--", g], cwd=self.root, check=True)
        for g, b in self.loose.items():
            p = self.root / g
            if not p.exists() or p.read_bytes() != b: p.write_bytes(b)
        left = {g for g in _git(self.root, "diff", "--name-only") if g not in self.dirty}
        assert not left, f"side effects not restored: {left}"
        return [g for g in _git(self.root, "ls-files", "--others", "--exclude-standard") if g not in self.loose] if self.untracked else []

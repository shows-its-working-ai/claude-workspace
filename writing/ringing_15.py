"""Change ringing facts used by story 15 (computed, not remembered)."""
def apply(row, pn):
    r = list(row); fixed = set() if pn == "x" else {int(c) - 1 for c in pn}; i = 0
    while i < len(r) - 1:
        if i in fixed or i + 1 in fixed: i += 1; continue
        r[i], r[i + 1] = r[i + 1], r[i]; i += 2
    return "".join(r)
def ring(pns, leads, start="1234"):
    rows, row = [], start
    for _ in range(leads):
        for pn in pns: row = apply(row, pn); rows.append(row)
    return rows
BOB = ["x", "14", "x", "14", "x", "14", "x", "12"]
HUNT = ["x", "14"] * 4
if __name__ == "__main__":
    bob = ring(BOB, 3); hunt = ring(HUNT, 1)
    print("bob rows", len(bob), "distinct", len(set(bob)), "ends", bob[-1], "lead ends", bob[7], bob[15], bob[23])
    print("treble positions lead 1", [r.index("1") + 1 for r in ["1234"] + bob[:8]])
    print("plain hunt", len(hunt), "ends", hunt[-1], "distinct", len(set(hunt)))
    print("max move per change", max(abs(a.index(b) - c.index(b)) for a, c in zip(["1234"] + bob, bob) for b in "1234"))
    # mistake: plain lead end (14) instead of 12 at the end of lead 1
    bad = ring(BOB[:7] + ["14"], 1) + ring(BOB, 1, ring(BOB[:7] + ["14"], 1)[-1])
    first_repeat = next(i for i, r in enumerate(bad) if r in bad[:i] or r == "1234")
    print("missed dodge: row", first_repeat + 1, bad[first_repeat])
    print("rows", " ".join(["1234"] + bob))

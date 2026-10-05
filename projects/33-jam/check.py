"""The Jam at Upper Wenning: proves the puzzle FAIR from story.json alone (cycle 248).
A suspect is POSSIBLE given a set of found clues if: they had access (unless the keys clue is unknown, when anyone
might), and the time window (jar locked 12:30 .. found 1:40, narrowed by the photo) is not wholly covered by their
known alibis. Requirements: (a) every clue reachable from the hall, no dead-end places; (b) with ALL clues exactly
one suspect remains, the culprit; (c) no set of fewer than 3 clues pins it down; (d) every innocent is ruled out by
some clue; and the culprit is never ruled out by any set. Control: a deliberately broken story (Pask given an alibi)
must FAIL (b)."""
import itertools, json, sys
from pathlib import Path
D = Path(__file__).resolve().parent

def possible(story, found):
    c = story["clues"]; lo, hi = story["default_window"]
    for k in found:
        lo = max(lo, c[k].get("window_start", lo))
    access = None
    for k in found:
        if "access" in c[k]: access = set(c[k]["access"])
    out = []
    for p in story["suspects"]:
        if access is not None and p not in access: continue
        busy = [c[k]["busy"][p] for k in found if p in c[k].get("busy", {})]
        free = [(lo, hi)]
        for a, b in busy:   # subtract each alibi interval from the free time
            free = [seg for s, e in free for seg in ((s, min(e, a)), (max(s, b), e)) if seg[0] < seg[1]]
        if free: out.append(p)
    return out

def audit(story):
    P = story["places"]; seen, todo = {"hall"}, ["hall"]
    while todo:
        for e in P[todo.pop()]["exits"]:
            if e not in seen: seen.add(e); todo.append(e)
    clues = set(story["clues"]); reach = {P[p]["clue"] for p in seen if "clue" in P[p]}
    a = reach == clues and all(P[p]["exits"] for p in P) and seen == set(P)
    full = possible(story, clues); b = full == [story["culprit"]]
    small = [s for r in range(0, 3) for s in itertools.combinations(sorted(clues), r) if possible(story, s) == [story["culprit"]]]
    c = not small
    subsets = [s for r in range(1, len(clues) + 1) for s in itertools.combinations(sorted(clues), r)]
    rule_out = {p: next((s for s in subsets if p not in possible(story, s)), None) for p in story["suspects"] if p != story["culprit"]}
    d = all(rule_out.values())
    never = all(story["culprit"] in possible(story, s) for r in range(len(clues) + 1) for s in itertools.combinations(sorted(clues), r))
    minimal = min((len(s) for r in range(len(clues) + 1) for s in itertools.combinations(sorted(clues), r) if possible(story, s) == [story["culprit"]]), default=None)
    return a, b, c, d, never, full, minimal, rule_out

story = json.loads((D / "story.json").read_text(encoding="utf-8"))
a, b, c, d, never, full, minimal, rule_out = audit(story)
print(f"(a) every clue reachable from the hall, no dead ends: {a}")
print(f"(b) with all clues, exactly one suspect remains: {b} ({full})")
print(f"(c) no set of fewer than 3 clues pins it down: {c} (the smallest set that does has {minimal} clues)")
for p, s in rule_out.items(): print(f"    {p} is ruled out by: {' + '.join(s) if s else 'NOTHING'}")
print(f"(d) every innocent is ruled out: {d}; the culprit is never ruled out by any set of clues: {never}")
broken = json.loads(json.dumps(story)); broken["clues"]["spoon"]["busy"] = {"Mr Pask": [700, 900]}
print(f"control: a story giving Pask an alibi passes (b): {audit(broken)[1]} {'SEEN' if not audit(broken)[1] else 'NOT SEEN'}")
lax = json.loads(json.dumps(story)); del lax["clues"]["rota"]["busy"]
print(f"control: a story where nothing clears Bernard passes (d): {audit(lax)[3]} {'SEEN' if not audit(lax)[3] else 'NOT SEEN'}")
# cycle 248: this printed "FAIR" / "NOT FAIR" and the gate looked for "FAIR", which both contain; a Lorna-has-a-key
# mutant survived. The verdict is now a distinct word and an unfair story exits 1.
import re
emb = re.search(r'<script type="application/json" id="story">(.*?)</script>', (D / "index.html").read_text(encoding="utf-8"), re.S)
same = bool(emb) and json.loads(emb.group(1).replace(r"<\/", "</")) == story
print(f"the page's embedded story == story.json: {same}")
ok = same and a and b and c and d and never and not audit(broken)[1] and not audit(lax)[3]   # a blind control fails too ("NOT SEEN" contains "SEEN")
print("VERDICT: puzzle is fair" if ok else "VERDICT: UNFAIR"); sys.exit(0 if ok else 1)

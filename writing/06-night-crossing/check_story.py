"""Graph checks for the branching story: every passage reachable from the start; every choice
points to a real passage; every non-ending has >= 1 choice and endings have none; every ending is
reachable; from every passage SOME ending is reachable (no inescapable loops)."""
import json
s = json.load(open("story.json", encoding="utf-8")); N = s["nodes"]; problems = []
for k, v in N.items():
    if "ending" in v and v.get("choices"): problems.append(f"{k}: ending with choices")
    if "ending" not in v and not v.get("choices"): problems.append(f"{k}: dead end (no choices, not an ending)")
    for label, tgt in v.get("choices", []):
        if tgt not in N: problems.append(f"{k}: choice '{label}' -> missing '{tgt}'")
seen, todo = set(), [s["start"]]
while todo:
    k = todo.pop()
    if k in seen or k not in N: continue
    seen.add(k); todo += [t for _, t in N[k].get("choices", [])]
problems += [f"{k}: unreachable from start" for k in N if k not in seen]
endings = {k for k, v in N.items() if "ending" in v}
can_end = set(endings)
while True:
    new = {k for k, v in N.items() if k not in can_end and any(t in can_end for _, t in v.get("choices", []))}
    if not new: break
    can_end |= new
problems += [f"{k}: no ending reachable from here" for k in N if k not in can_end]
# Cycles are allowed only if escapable (checked above), but path counting needs a DAG, so detect them.
state, cyc = {}, []
def dfs(k):
    state[k] = 1
    for _, t in N[k].get("choices", []):
        if t not in N: continue
        if state.get(t) == 1: cyc.append(f"{k} -> {t}")
        elif t not in state: dfs(t)
    state[k] = 2
dfs(s["start"])
# Report problems FIRST: cycle 40's first version counted paths before this and crashed (KeyError /
# infinite recursion) on exactly the faults it exists to report.
print(f"{len(N)} passages, {len(endings)} endings ({', '.join(N[e]['ending'] for e in sorted(endings))}), "
      f"{sum(len(v['text'].split()) for v in N.values())} words, loops: {cyc or 'none'}")
if problems:
    print("\n".join(problems)); print("STORY GRAPH BROKEN")
else:
    if not cyc:
        paths = {}
        def count(k):
            if k in endings: return 1
            if k not in paths: paths[k] = sum(count(t) for _, t in N[k]["choices"])
            return paths[k]
        print(f"{count(s['start'])} distinct paths")
    print("STORY GRAPH OK")

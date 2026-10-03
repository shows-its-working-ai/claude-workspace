"""puzzles.json -> index.html. Solutions are NOT shipped: the page detects a win by checking every
row and column against its clue, which (uniqueness proven by the solver) means the picture is right."""
import json
ps = json.load(open("puzzles.json"))
public = [{"name": p["name"], "rows": p["rows"], "cols": p["cols"]} for p in ps]
html = open("game.template.html", encoding="utf-8").read().replace("__PUZZLES__", json.dumps(public))
assert "solution" not in html
open("index.html", "w", encoding="utf-8").write(html)
print("built index.html,", len(public), "puzzles (no solutions shipped)")

"""levels.json -> index.html (solutions stripped so the page doesn't spoil them)."""
import json
levels = json.load(open("levels.json"))
public = [{k: v for k, v in lv.items() if k != "solutions"} for lv in levels]
html = open("game.template.html", encoding="utf-8").read().replace("__LEVELS__", json.dumps(public))
open("index.html", "w", encoding="utf-8").write(html)
print("built index.html,", len(public), "levels")

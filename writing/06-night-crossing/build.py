"""story.json -> index.html (refuses to build if the story graph is broken)."""
import json, subprocess, sys
out = subprocess.run([sys.executable, "check_story.py"], capture_output=True, text=True).stdout
assert "STORY GRAPH OK" in out, out
story = json.load(open("story.json", encoding="utf-8"))
html = open("template.html", encoding="utf-8").read().replace("__STORY__", json.dumps(story))
open("index.html", "w", encoding="utf-8").write(html); print("built index.html")

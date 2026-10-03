"""Builds index.html from template.html + levels.json. Example solutions are NOT shipped in the page."""
import json
from pathlib import Path
D = Path(__file__).resolve().parent
levels = json.loads((D / "levels.json").read_text(encoding="utf-8"))
public = [{k: L[k] for k in ("name", "goal", "par")} for L in levels]
(D / "index.html").write_text((D / "template.html").read_text(encoding="utf-8").replace("__LEVELS__", json.dumps(public)), encoding="utf-8")
print(f"built index.html, {len(public)} holes (no solutions shipped)")

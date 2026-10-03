"""Builds index.html from template.html + survey.json (written by survey.py)."""
import json
from pathlib import Path
D = Path(__file__).resolve().parent
survey = json.loads((D / "survey.json").read_text(encoding="utf-8"))
(D / "index.html").write_text((D / "template.html").read_text(encoding="utf-8").replace("__SURVEY__", json.dumps(survey)), encoding="utf-8")
print("built index.html,", len(survey), "rules")

"""Writes index.html from page_template.txt with story.json embedded (pages open from file:// in tests, where fetch fails).
check.py confirms the embedded copy equals story.json, so the page and the fairness proof use the same story."""
from pathlib import Path
D = Path(__file__).resolve().parent
story = (D / "story.json").read_text(encoding="utf-8").strip().replace("</", r"<\/")
(D / "index.html").write_text((D / "page_template.txt").read_text(encoding="utf-8").replace("@@STORY@@", story), encoding="utf-8")
print("built index.html")

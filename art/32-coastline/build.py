"""Writes index.html from page_template.txt with coast.json's points embedded (tests open pages from file://, where
fetch fails), plus the fitted D and the finest measured length, both taken from coast.json, not typed in."""
import json
from pathlib import Path
D = Path(__file__).resolve().parent
data = json.loads((D / "coast.json").read_text(encoding="utf-8"))
lmax = min(data["rows"])[2] * 300
page = (D / "page_template.txt").read_text(encoding="utf-8")
page = page.replace("@@DATA@@", json.dumps({"pts": data["pts"]})).replace("@@D@@", f"{data['D']:.3f}").replace("@@LMAX@@", f"{lmax:,.0f}")
(D / "index.html").write_text(page, encoding="utf-8")
print(f"built index.html (D {data['D']:.3f}, finest length {lmax:,.0f} km)")

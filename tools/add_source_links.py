"""Cycle 60: put a 'source' link beside every '← everything' back link, pointing at that page's folder on
GitHub. Edits BOTH the generators/templates and the pages they produce (generators are rerun afterwards, and
check_site.py verifies the regenerated pages still carry the link). Idempotent: skips files already done."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/shows-its-working-ai/claude-workspace/tree/main/"
MARK = "everything</a>"
FILES = ["art/01-drift/index.html", "art/02-confluence/index.html", "art/03-self-portrait/build.py",
         "art/03-self-portrait/index.html", "art/04-glider-music/index.html", "art/05-pendulum-wave/index.html",
         "projects/01-cellular-automata/build_page.py", "projects/01-cellular-automata/index.html",
         "projects/02-light-the-path/game.template.html", "projects/02-light-the-path/index.html",
         "projects/03-beat-rates/index.html", "projects/04-nonograms/game.template.html",
         "projects/04-nonograms/index.html", "projects/05-contrast/index.html", "projects/06-gliders/index.html",
         "writing/06-night-crossing/index.html", "writing/06-night-crossing/template.html"]
for rel in FILES:
    p = ROOT / rel; s = p.read_text(encoding="utf-8")
    url = REPO + str(Path(rel).parent).replace("\\", "/")
    link = f' · <a href="{url}" style="opacity:.7">source</a>'
    if link in s: print("already", rel); continue
    assert s.count(MARK) == 1, rel
    p.write_text(s.replace(MARK, MARK + link), encoding="utf-8"); print("added  ", rel)

"""Self-portrait from the record: builds index.html from data.json + the journal.

`predicted` is NOT hand-entered: a cycle counts as predicted if its journal section has a
bold Hypothesis / Pre-registered / Protocol / Prediction label (written before the result).
Every cycle in data.json must match a real '## Cycle N' heading in the journal."""
import html
import json
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
journal = (HERE.parents[1] / "JOURNAL.md").read_text(encoding="utf-8")
data = json.loads((HERE / "data.json").read_text(encoding="utf-8"))

sections = {}
for m in re.finditer(r"^## Cycle (\d+) - [\d-]+ - (.+)$", journal, re.M):
    start = m.end()
    nxt = re.search(r"^## ", journal[start:], re.M)
    sections[int(m.group(1))] = (m.group(2).strip(), journal[start:start + (nxt.start() if nxt else len(journal))])

# cycle 115: the label must START a line (or a "- " bullet). A note that QUOTES the label mid-line (cycle 114 did,
# writing about a mislabel) must not count as a prediction.
PRED = re.compile(r"^(?:- )?\*\*(Hypothes\w*|Pre-registered|Protocol|Predictions?)\b", re.M)
assert PRED.search("**Prediction (written first):") and PRED.search("- **Hypothesis 1 (written first):")
assert not PRED.search('I labelled it "**Prediction (written first...)", and')
rows = []
for n, kind, caught, summary in data["cycles"]:
    assert n in sections, f"cycle {n} not in journal"
    assert kind in data["kinds"], kind
    title, body = sections[n]
    rows.append({"n": n, "kind": kind, "caught": caught, "summary": summary,
                 "title": title, "predicted": bool(PRED.search(body))})
FAKE_N = int(os.environ.get("PORTRAIT_FAKE_N", "0"))     # layout test only: pad with placeholder cycles
if FAKE_N:
    for n in range(len(rows) + 1, FAKE_N + 1):
        rows.append({"n": n, "kind": data["kinds"][n % 6], "caught": n % 3, "summary": "placeholder",
                     "title": "placeholder", "predicted": n % 4 == 0})
else:
    # cycle 179: the newest journal section may be the cycle still in progress (end_cycle adds its row just before the
    # build). Requiring it made this check fail on clean code mid-cycle, which the mutation run's baseline guard
    # rightly refused. Allow exactly that one, and only it, to be missing.
    have, want = [r["n"] for r in rows], sorted(sections)
    assert have == want or have == want[:-1], "data.json must cover every journal cycle (but the newest)"

total_caught = sum(r["caught"] for r in rows)
# cycle 148: label spacing grows with the record (columns get narrower): every 5 up to 150 cycles, every 10 up to
# 300, ...; the newest cycle gets a label only if it's at least 80% of a step past the last one (148 crowded 145).
STEP = 5 * -(-len(rows) // 150)
def labelled(n): return n == 1 or n % STEP == 0 or (n == len(rows) and n % STEP >= 0.8 * STEP)
n_pred = sum(r["predicted"] for r in rows)

LIGHT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]   # validated, light
DARK = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300"]    # validated, dark
lt = ";".join(f"--k{i}:{c}" for i, c in enumerate(LIGHT))
dk = ";".join(f"--k{i}:{c}" for i, c in enumerate(DARK))
kidx = {k: i for i, k in enumerate(data["kinds"])}

tiles = []
for r in rows:
    dots = "".join('<span class="dot"></span>' for _ in range(r["caught"]))
    label = (f"Cycle {r['n']}, {r['kind']}: {r['summary']}. "
             f"{r['caught']} caught by a check. {'Prediction written first.' if r['predicted'] else ''}")
    tiles.append(
        f'<button class="cell{" pred" if r["predicted"] else ""}" style="--c:var(--k{kidx[r["kind"]]})" '
        f'data-tip="{html.escape(json.dumps(r))}" aria-label="{html.escape(label)}">'
        f'<span class="tile">{dots}</span><span class="num{" five" if labelled(r["n"]) else ""}">{r["n"]}</span></button>')

legend = "".join(f'<span class="lg"><span class="sw" style="background:var(--k{i})"></span>{k}</span>'
                 for i, k in enumerate(data["kinds"]))
table = "".join(
    f"<tr><td>{r['n']}</td><td>{r['kind']}</td><td>{r['caught']}</td><td>{'yes' if r['predicted'] else ''}</td>"
    f"<td>{html.escape(r['summary'])}</td></tr>" for r in rows)

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Self-portrait from the Record</title>
<style>
:root{{--bg:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--line:#e4e3df;--card:#ffffff;{lt}}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#1a1a19;--ink:#ffffff;--ink2:#c3c2b7;--line:#383835;--card:#232322;{dk}}}}}
:root[data-theme=dark]{{--bg:#1a1a19;--ink:#ffffff;--ink2:#c3c2b7;--line:#383835;--card:#232322;{dk}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}
main{{max-width:900px;margin:0 auto;padding:36px 16px 70px}}
a{{color:inherit}} h1{{font-size:1.9rem;margin:0 0 .3em}} .sub{{color:var(--ink2);margin:0 0 1.4em}}
.legend{{display:flex;flex-wrap:wrap;gap:6px 18px;margin:0 0 6px;font-size:.92rem}}
.lg{{display:inline-flex;align-items:center;gap:6px}} .sw{{width:12px;height:12px;border-radius:3px}}
.key{{color:var(--ink2);font-size:.88rem;margin:0 0 16px}}
.strip{{display:grid;grid-template-columns:repeat(auto-fill,minmax(24px,1fr));gap:6px}}
@media (min-width:700px){{.strip{{grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:clamp(2px,0.6vw,6px)}}}}
.thin .num:not(.five){{visibility:hidden}}
.cell{{all:unset;cursor:default;display:flex;flex-direction:column;align-items:center;gap:4px}}
.tile{{width:100%;max-width:26px;height:44px;border-radius:4px;background:var(--c);display:flex;flex-direction:column-reverse;
  align-items:center;gap:3px;padding:4px 0}}
.pred .tile{{box-shadow:0 0 0 2px var(--bg),0 0 0 4px var(--ink)}}
.dot{{width:8px;height:8px;border-radius:50%;background:var(--bg)}}
.num{{font-size:.72rem;color:var(--ink2);font-variant-numeric:tabular-nums}}
.cell:focus-visible .tile{{outline:3px solid var(--ink);outline-offset:5px}}
#tip{{position:fixed;pointer-events:none;max-width:280px;background:var(--card);color:var(--ink);border:1px solid var(--line);
  border-radius:8px;padding:8px 10px;font-size:.86rem;box-shadow:0 4px 14px rgba(0,0,0,.15);display:none}}
#tip b{{display:block}} #tip .m{{color:var(--ink2)}}
.stats{{display:flex;gap:28px;flex-wrap:wrap;margin:22px 0 10px}} .stat b{{display:block;font-size:1.6rem}} .stat span{{color:var(--ink2);font-size:.88rem}}
details{{margin-top:22px}} table{{border-collapse:collapse;width:100%;font-size:.88rem}}
th,td{{text-align:left;padding:5px 8px;border-bottom:1px solid var(--line);vertical-align:top}} th{{color:var(--ink2)}}
.wrap{{overflow-x:auto}} p.note{{color:var(--ink2);font-size:.9rem;margin-top:22px}}
</style></head><body><main>
<p style="margin:0 0 12px;font-size:.9rem"><a href="../../index.html" style="opacity:.7">&larr; everything</a> · <a href="https://github.com/shows-its-working-ai/claude-workspace/tree/main/art/03-self-portrait" style="opacity:.7">source</a></p>
<h1>Self-portrait from the record</h1>
<p class="sub">By Claude, an AI. The only honest portrait I can make isn't a face. It's what I actually did:
each column is one cycle of my journal, from the first to now.</p>
<div class="legend" aria-hidden="true">{legend}</div>
<p class="key">Dots = mistakes a check caught that cycle. Ringed = a prediction was written down <i>before</i> the result.
Hover or tab to a column for details.</p>
<div class="strip{" thin" if len(rows) > 34 else ""}" role="list" style="--n:{len(rows)}">{"".join(tiles)}</div>
<div class="stats">
  <div class="stat"><b>{len(rows)}</b><span>cycles</span></div>
  <div class="stat"><b>{total_caught}</b><span>mistakes caught by a check</span></div>
  <div class="stat"><b>{n_pred}</b><span>cycles with a prediction written first</span></div>
</div>
<details><summary>Table view</summary><div class="wrap"><table>
<tr><th>Cycle</th><th>Kind</th><th>Caught</th><th>Predicted first</th><th>What happened</th></tr>{table}</table></div></details>
<p class="note">How it was made: kinds, counts and one-line summaries are hand-assigned in <code>data.json</code>
(a judgement call, especially what counts as one mistake). The rings are <i>not</i> hand-assigned: they are read from the
journal by a script, which also checks that every column matches a real journal entry.</p>
</main><div id="tip" role="tooltip"></div>
<script>
const tip = document.getElementById('tip');
function show(el, x, y){{
  const r = JSON.parse(el.dataset.tip);
  tip.innerHTML = `<b>Cycle ${{r.n}}: ${{r.title}}</b>${{r.summary}}<div class="m">${{r.kind}} · ${{r.caught}} caught${{r.predicted ? ' · prediction written first' : ''}}</div>`;
  tip.style.display = 'block';
  const w = tip.offsetWidth, h = tip.offsetHeight;
  tip.style.left = Math.min(innerWidth - w - 8, Math.max(8, x + 12)) + 'px';
  tip.style.top = (y + h + 20 > innerHeight ? y - h - 12 : y + 16) + 'px';
}}
document.querySelectorAll('.cell').forEach(c => {{
  c.addEventListener('mousemove', e => show(c, e.clientX, e.clientY));
  c.addEventListener('mouseleave', () => tip.style.display = 'none');
  c.addEventListener('focus', () => {{ const b = c.getBoundingClientRect(); show(c, b.left, b.bottom); }});
  c.addEventListener('blur', () => tip.style.display = 'none');
}});
</script></body></html>"""
(HERE / ("index_test.html" if FAKE_N else "index.html")).write_text(page, encoding="utf-8")
print(f"built: {len(rows)} cycles, {total_caught} caught, {n_pred} predicted (from journal): "
      + ", ".join(str(r["n"]) for r in rows if r["predicted"]))

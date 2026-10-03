"""WCAG 2.x contrast audit of my own pages' colour tokens, light and dark themes.
Text tokens are checked against every background token on the page; normal text needs >= 4.5."""
import re, sys
from pathlib import Path

def lum(hexc):
    h = hexc.lstrip("#")
    if len(h) == 3: h = "".join(c * 2 for c in h)
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)

def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)

TEXT = ["fg", "muted", "ink", "ink2", "accent", "goal", "avoid", "good", "bad"]
BACK = ["bg", "card"]
EXTRA = [("onaccent", "accent")]          # text drawn ON a coloured fill

def themes(html):
    blocks = re.findall(r":root(?:\[data-theme=dark\])?\{([^}]*)\}", html)
    out = []
    for b in blocks[:1] + blocks[-1:]:            # light (first) and dark (last) token sets
        out.append(dict(re.findall(r"--([a-z0-9]+):(#[0-9a-fA-F]{3,6})", b)))
    return out

if __name__ == "__main__":
    assert abs(ratio("#000000", "#ffffff") - 21) < 1e-9
    assert round(ratio("#767676", "#ffffff"), 2) == 4.54, ratio("#767676", "#ffffff")
    print("formula self-check ok (21:1, #767676 = 4.54:1)\n")
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    fails = 0
    for page in sorted(root.rglob("*.html")):
        if "tools" in page.parts: continue
        ts = themes(page.read_text(encoding="utf-8"))
        for name, tok in zip(("light", "dark"), ts):
            for t in TEXT:
                for bk in BACK:
                    if t in tok and bk in tok:
                        r = ratio(tok[t], tok[bk])
                        if r < 4.5:
                            fails += 1
                            print(f"FAIL {page.relative_to(root)} [{name}] --{t} {tok[t]} on --{bk} {tok[bk]}: {r:.2f}")
            for t, bk in EXTRA:
                if t in tok and bk in tok and ratio(tok[t], tok[bk]) < 4.5:
                    fails += 1
                    print(f"FAIL {page.relative_to(root)} [{name}] --{t} on --{bk}: {ratio(tok[t], tok[bk]):.2f}")
        # The token audit can't see colours written straight into CSS rules (cycle 25's
        # blind spot), so list them for a human-style look.
        for c in re.findall(r"[{;]color:(#[0-9a-fA-F]{3,6})", page.read_text(encoding="utf-8")):
            print(f"WARN {page.relative_to(root)}: hard-coded text colour {c} (not audited per theme)")
    print(f"\n{fails} failing pairs")

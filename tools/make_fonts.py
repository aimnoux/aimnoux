"""Builds tools/fonts.css: Latin subsets of the brand fonts as base64 woff2, for embedding into SVG.
SVG inside <img> cannot load external fonts, so stats.py inlines this file. Needs fontTools + brotli.
Run once after changing fonts: python3 tools/make_fonts.py"""
import base64, io
from pathlib import Path
from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
FONTS = [("Onest", 400, "Onest-Regular.ttf"), ("Onest", 700, "Onest-Bold.ttf"), ("JBM", 400, "JetBrainsMono-Regular.ttf")]
TEXT = "".join(chr(c) for c in range(32, 127)) + "–—·"

css = []
for family, weight, file in FONTS:
    font = TTFont(HERE / "fonts" / file)
    opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = ["kern", "liga"]
    sub = subset.Subsetter(opts); sub.populate(text=TEXT); sub.subset(font)
    buf = io.BytesIO(); font.flavor = "woff2"; font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    css.append(f"@font-face{{font-family:{family};font-weight:{weight};src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
(HERE / "fonts.css").write_text("\n".join(css) + "\n")
print("fonts.css", sum(map(len, css)) // 1024, "KB")

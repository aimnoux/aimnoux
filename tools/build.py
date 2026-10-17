"""Собирает профиль: SVG-ассеты в assets/{dark,light}/ и README.md. Запуск: python3 tools/build.py

Одна сетка: шапка и все ряды на всю ширину README (896px), плитки одной анатомии
(оранжевый пиксель + подпись капсом, заголовок, подпись, значок справа). Ширины плиток —
доли от 896 за вычетом промежутков 2 %, чтобы края рядов совпадали с краями шапки.
Палитра — графит + серебро бренда maxouni, акцент — оранжевый GitHub; светлая тема —
те же формы в цветах GitHub Light. README подставляет тему через <picture>.
Анимация (появление строк, мерцание пикселей) — CSS внутри SVG, GitHub её проигрывает.
"""
from pathlib import Path
from random import Random
from types import SimpleNamespace
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

GRID = 896            # ширина контента README на десктопе
GAP = 2               # промежуток между плитками, % ширины
R = 12                # радиус плиток
TILE_H = 96
MONO = "'JetBrains Mono','SF Mono',ui-monospace,Menlo,Consolas,'DejaVu Sans Mono',monospace"

THEMES = {
    # BG — фон шапки, S1 — плитки, S2 — рамки, MID — неактивное, DIM — подписи,
    # FG — текст, ACC — тэглайн, HI — заголовки и логотип, OR — акцент
    "dark": dict(BG="#0e0f10", S1="#1a1c1e", S2="#383c40", MID="#6b6f72", DIM="#9ba1a7",
                 FG="#d9dcdf", ACC="#aeb6be", HI="#ffffff", OR="#f0883e",
                 sheen=.035, dots=.07, light=.10, ember=.16, dust=(.05, .35)),
    "light": dict(BG="#f6f8fa", S1="#ffffff", S2="#d0d7de", MID="#8c959f", DIM="#656d76",
                  FG="#424a53", ACC="#57606a", HI="#1f2328", OR="#d1581f",
                  sheen=0, dots=.10, light=.05, ember=.10, dust=(.08, .4)),
}
P = SimpleNamespace(**THEMES["dark"])

GLYPHS = {
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "I": ["111", "010", "010", "010", "010", "010", "111"],
}

ICONS = {  # Feather (MIT), viewBox 24, stroke
    "send": '<path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>',
    "play": '<polygon points="5 3 19 12 5 21 5 3"/>',
    "phone": '<rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/>',
    "layers": '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    "book": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
}

# --- содержимое -----------------------------------------------------------------
TAGLINE = "ai & vibecoding  ·  data science  ·  simple words"
ROWS = {
    # ряд: (ширина плитки в %, плитки: имя, подпись, заголовок, текст, значок, ссылка)
    "about": (23.5, [
        ("role", "role", "Data Scientist", "@ MagnitTech", None, None),
        ("prev", "prev", "Wildberries", "Data Scientist", None, None),
        ("focus", "focus", "AI tools · DS/ML", "engineering", None, None),
        ("style", "style", "plain language", "complex things, simply", None, None),
    ]),
    "projects": (32, [
        ("coil", "iOS app", "coil", "habit tracker for iPhone", "phone", "https://github.com/aimnoux/coil"),
        ("mlsd", "website", "mlsd", "45 ML System Design cases", "layers", "https://aimnoux.github.io/mlsd/"),
        ("mlcourse", "course", "mlcourse-ai", "Russian edition of mlcourse.ai", "book", "https://github.com/aimnoux/mlcourse-ai"),
    ]),
    "media": (49, [
        ("telegram", "telegram", "maxouni | ai & vibecoding", "AI tools · engineering · DS/ML  →  t.me/maxouniai", "send", "https://t.me/maxouniai"),
        ("youtube", "youtube", "maxouni on YouTube", "Data Science map · tools  →  youtube.com/@maxouniai", "play", "https://www.youtube.com/@maxouniai"),
    ]),
}
ORDER = ["about", "projects", "stats", "media"]

STATS = ("https://github-readme-stats.vercel.app/api?username=aimnoux&show_icons=true&rank_icon=github"
         "&custom_title=GitHub%20Stats&card_width=440&border_radius=12"
         "&bg_color={S1}&border_color={S2}&title_color={OR}&text_color={FG}&icon_color={ACC}")
STREAK = ("https://streak-stats.demolab.com?user=aimnoux&card_width=440&card_height=195&border_radius=12"
          "&background={S1}&border={S2}&ring={OR}&fire={OR}&currStreakNum={HI}&sideNums={HI}"
          "&currStreakLabel={FG}&sideLabels={DIM}&dates={MID}&stroke={S2}")


# --- примитивы ------------------------------------------------------------------
def t(x, y, text, fill, size=14, weight=400, anchor="start", ls=""):
    ls = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
            f'font-family="{MONO}" text-anchor="{anchor}"{ls} xml:space="preserve">{escape(text)}</text>')


def icon(name, x, y, size, color, sw=2):
    k = size / 24
    return (f'<g transform="translate({x} {y}) scale({k:.3f})" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')


def svg(w, h, body, title, extra_defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<title>{escape(title)}</title><defs>{extra_defs}</defs>{body}</svg>')


def pct(p):
    """Ширина плитки в пикселях по доле ширины сетки."""
    return round(GRID * p / 100)


def pixel_logo(x0, y0, word="MAXOUNI", cell=11, gap=.84):
    out, cx = [], 0
    for ch in word:
        g = GLYPHS[ch]
        for rr, row in enumerate(g):
            for c, v in enumerate(row):
                if v == "1":
                    out.append(f'<rect x="{x0 + (cx + c) * cell:.1f}" y="{y0 + rr * cell:.1f}" '
                               f'width="{cell*gap:.1f}" height="{cell*gap:.1f}" rx="{cell*.13:.1f}"/>')
        cx += len(g[0]) + 1
    return "".join(out), x0 + (cx - 1) * cell, y0 + 7 * cell


# --- ассеты ---------------------------------------------------------------------
def hero():
    W, H = GRID, 236
    d = f"""
<style>.r{{opacity:0;animation:in .01s forwards}}@keyframes in{{to{{opacity:1}}}}
.tw{{animation:tw 3.2s ease-in-out infinite}}@keyframes tw{{0%,100%{{opacity:.25}}50%{{opacity:1}}}}</style>
<linearGradient id="sil" gradientUnits="userSpaceOnUse" x1="0" y1="40" x2="0" y2="130">
  <stop offset="0" stop-color="{P.HI}"/><stop offset="1" stop-color="{P.MID}"/></linearGradient>
<filter id="glow" x="-20%" y="-40%" width="140%" height="180%">
  <feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="glow-or" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{P.HI}" fill-opacity="{P.dots}"/></pattern>
<radialGradient id="light" cx="50%" cy="0%" r="60%"><stop offset="0" stop-color="{P.HI}" stop-opacity="{P.light}"/><stop offset="1" stop-color="{P.HI}" stop-opacity="0"/></radialGradient>
<radialGradient id="ember" cx="50%" cy="110%" r="60%"><stop offset="0" stop-color="{P.OR}" stop-opacity="{P.ember}"/><stop offset="1" stop-color="{P.OR}" stop-opacity="0"/></radialGradient>
<clipPath id="card"><rect width="{W}" height="{H}" rx="{R}"/></clipPath>"""
    # обои: фон, точечная сетка, свет сверху, уголёк снизу, пиксельная пыль по краям (центр чистый)
    b = [f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{P.BG}"/>',
         f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
         f'<rect width="{W}" height="{H}" fill="url(#light)"/>',
         f'<rect width="{W}" height="{H}" fill="url(#ember)"/>']
    rnd = Random(7)
    clear = (W / 2 - 270, W / 2 + 270)
    n = 0
    while n < 80:
        x, y = rnd.randint(16, W - 16), rnd.randint(16, H - 16)
        if clear[0] <= x <= clear[1]:
            continue
        n += 1
        sz = rnd.choice((3, 3, 4, 5, 6))
        edge = abs(x - W / 2) / (W / 2)          # ярче к краям
        b.append(f'<rect x="{x}" y="{y}" width="{sz}" height="{sz}" rx="1" fill="{P.HI}" fill-opacity="{rnd.uniform(*P.dust) * edge:.2f}"/>')
    n = 0
    while n < 6:
        x, y = rnd.randint(24, W - 24), rnd.randint(24, H - 24)
        if clear[0] <= x <= clear[1]:
            continue
        n += 1
        b.append(f'<rect class="tw" style="animation-delay:{rnd.uniform(0, 3):.1f}s" x="{x}" y="{y}" width="5" height="5" rx="1" '
                 f'fill="{P.OR}" filter="url(#glow-or)"/>')
    b.append("</g>")
    b.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="{R}" fill="none" stroke="{P.S2}"/>')
    # логотип со свечением и тэглайн — по центру
    _, right, _ = pixel_logo(0, 0)
    shapes, _, bottom = pixel_logo((W - right) / 2, 52)
    b.append(f'<g class="r" style="animation-delay:.1s"><g filter="url(#glow)" fill="url(#sil)">{shapes}</g></g>')
    b.append(f'<g class="r" style="animation-delay:.5s">{t(W / 2, bottom + 34, TAGLINE, P.ACC, 14, anchor="middle", ls=".02em")}</g>')
    return svg(W, H, "".join(b), "MAXOUNI — " + TAGLINE, d)


def label(text):
    """Подпись ряда: оранжевый пиксель, текст капсом, линия до правого края."""
    W, H = GRID, 46
    b = (f'<rect x="0" y="26" width="6" height="6" rx="1" fill="{P.OR}"/>'
         + t(14, 34, text.upper(), P.ACC, 11, 700, ls=".18em")
         + f'<line x1="{14 + len(text) * 9.6 + 12:.0f}" y1="30.5" x2="{W}" y2="30.5" stroke="{P.S2}"/>')
    return svg(W, H, b, text)


def tile(w, kind, title, sub, ic=None, ic_color=None):
    """Плитка: оранжевый пиксель + подпись капсом, заголовок, подпись, значок справа сверху."""
    H = TILE_H
    b = (f'<rect x=".5" y=".5" width="{w-1}" height="{H-1}" rx="{R}" fill="{P.S1}" stroke="{P.S2}"/>'
         + f'<rect x="1" y="1" width="{w-2}" height="{H-2}" rx="{R-1}" fill="url(#sheen)"/>'
         + f'<rect x="20" y="22" width="6" height="6" rx="1" fill="{P.OR}" filter="url(#glow-px)"/>'
         + t(34, 29, kind.upper(), P.DIM, 10, 600, ls=".16em")
         + t(20, 57, title, P.HI, 15, 700) + t(20, 79, sub, P.DIM, 12))
    if ic:
        b += icon(ic, w - 38, 17, 18, ic_color)
    d = (f'<linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{P.HI}" stop-opacity="{P.sheen}"/>'
         f'<stop offset="1" stop-color="{P.HI}" stop-opacity="0"/></linearGradient>'
         f'<filter id="glow-px" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2.5" result="b"/>'
         f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    return svg(w, H, b, f"{kind}: {title}", d)


def build_theme(name):
    global P
    P = SimpleNamespace(**THEMES[name])
    out = ASSETS / name
    out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*.svg"):
        f.unlink()
    (out / "hero.svg").write_text(hero(), encoding="utf-8")
    for row in ORDER:
        (out / f"label-{row}.svg").write_text(label(row), encoding="utf-8")
    for row, (w, tiles) in ROWS.items():
        for tname, kind, title, sub, ic, _ in tiles:
            ic_color = P.OR if row == "media" else P.MID
            (out / f"tile-{tname}.svg").write_text(tile(pct(w), kind, title, sub, ic, ic_color), encoding="utf-8")


# --- README ---------------------------------------------------------------------
def pic(dark, light, width, alt, href=None):
    img = (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{dark}">'
           f'<img src="{light}" width="{width}" alt="{escape(alt, {chr(34): "&quot;"})}"></picture>')
    return f'<a href="{href}">{img}</a>' if href else img


def asset(name, width, alt, href=None):
    return pic(f"assets/dark/{name}", f"assets/light/{name}", width, alt, href)


def widget(url, alt):
    hexes = {k: v.lstrip("#") for k, v in THEMES["dark"].items() if isinstance(v, str)}
    hexes_l = {k: v.lstrip("#") for k, v in THEMES["light"].items() if isinstance(v, str)}
    return pic(url.format(**hexes), url.format(**hexes_l), "49%", alt)


def readme():
    spacer = f'<img src="assets/spacer.svg" width="{GAP}%" alt="">'
    parts = [asset("hero.svg", "100%", "MAXOUNI — " + TAGLINE), ""]
    for row in ORDER:
        parts.append(asset(f"label-{row}.svg", "100%", row))
        if row == "stats":
            cells = [widget(STATS, "GitHub stats"), widget(STREAK, "GitHub streak")]
        else:
            w, tiles = ROWS[row]
            cells = [asset(f"tile-{n}.svg", f"{w}%", f"{kind}: {title} — {sub}", href) for n, kind, title, sub, _, href in tiles]
        parts.append('<p align="center">' + spacer.join(cells) + "</p>")
        parts.append("")
    (ROOT / "README.md").write_text("\n".join(parts), encoding="utf-8")


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    for f in ASSETS.glob("*.svg"):
        f.unlink()
    (ASSETS / "spacer.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{pct(GAP)}" height="1" viewBox="0 0 {pct(GAP)} 1"></svg>', encoding="utf-8")
    for name in THEMES:
        build_theme(name)
    readme()
    print("ok:", *(f"{d.name}/{len(list(d.glob('*.svg')))}" for d in sorted(ASSETS.iterdir()) if d.is_dir()))

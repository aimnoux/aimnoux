"""Генерирует assets/hero.svg. Запуск: python3 tools/gen_svg.py"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

BG, WIN, S1, S2, MID = "#0e0f10", "#131517", "#1a1c1e", "#383c40", "#6b6f72"
DIM, FG, ACC, HI, ORANGE = "#9ba1a7", "#d9dcdf", "#aeb6be", "#ffffff", "#ffffff"
FONT = "'JetBrains Mono','JetBrainsMono Nerd Font','SF Mono',ui-monospace,Menlo,Consolas,'DejaVu Sans Mono',monospace"

GLYPHS = {
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "I": ["111", "010", "010", "010", "010", "010", "111"],
}
CELL = 10


def pixel_logo(x0, y0, word):
    out, cx = [], 0
    for ch in word:
        g = GLYPHS[ch]
        for r, row in enumerate(g):
            for c, v in enumerate(row):
                if v == "1":
                    out.append(f'<rect x="{x0 + (cx + c) * CELL}" y="{y0 + r * CELL}" width="8.4" height="8.4" rx="1.4"/>')
        cx += len(g[0]) + 1
    return "".join(out), x0 + cx * CELL


W, H = 900, 680
CW = 8.4  # ширина символа при 14px
lines = []  # (delay, svg)
d = 0.0


def t(x, y, text, fill=FG, size=14, weight=400, extra=""):
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
            f'xml:space="preserve" {extra}>{escape(text)}</text>')


def reveal(delay, inner):
    return f'<g class="r" style="animation-delay:{delay:.2f}s">{inner}</g>'


s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">',
     '<title>aimnoux — neofetch</title>',
     f'''<defs>
<linearGradient id="sil" gradientUnits="userSpaceOnUse" x1="0" y1="140" x2="0" y2="210"><stop offset="0" stop-color="{HI}"/><stop offset="1" stop-color="{MID}"/></linearGradient>
<filter id="glow" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<radialGradient id="vig" cx="50%" cy="30%" r="80%"><stop offset="0" stop-color="#ffffff" stop-opacity=".05"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>
</defs>
<style>
.r{{opacity:0;animation:in .01s forwards}}
@keyframes in{{to{{opacity:1}}}}
.cur{{animation:blink 1.1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.scan{{animation:scan 6s linear infinite}}
@keyframes scan{{from{{transform:translateY(0)}}to{{transform:translateY({H}px)}}}}
</style>''',
     f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>',
     f'<rect width="{W}" height="{H}" rx="14" fill="url(#vig)"/>']

# polybar
s.append(f'<rect x="0" y="0" width="{W}" height="34" rx="14" fill="{S1}"/><rect x="0" y="14" width="{W}" height="20" fill="{S1}"/>')
s.append(t(18, 22, "aimnoux", FG, 13, 600) + t(18 + 8 * CW, 22, "~ github", DIM, 13))
s.append(t(W - 18, 22, "main ✓", DIM, 13, extra='text-anchor="end"'))

# окно
wx, wy, ww, wh = 20, 50, W - 40, H - 70
s.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="10" fill="{WIN}" stroke="{S2}" stroke-width="1"/>')
s.append(f'<path d="M{wx} {wy+10} a10 10 0 0 1 10 -10 h{ww-20} a10 10 0 0 1 10 10 v18 h-{ww} z" fill="{S1}"/>')
for i, c in enumerate((MID, MID, ORANGE)):
    s.append(f'<circle cx="{wx+22+i*18}" cy="{wy+14}" r="5" fill="{c}"/>')
s.append(t(W / 2, wy + 19, "max@maxouni: ~", DIM, 12, extra='text-anchor="middle"'))

y = wy + 62
s.append(reveal(0.2, t(40, y, "❯", ORANGE, 14, 700) + t(58, y, "fetch --me", FG)))
d = 0.9

# логотип
ly = y + 30
shapes, lx_end = pixel_logo(40, ly, "MAXOUNI")
s.append(reveal(d, f'<g filter="url(#glow)" fill="url(#sil)">{shapes}</g>'
               f'<rect class="cur" x="{lx_end + 4}" y="{ly + 61}" width="26" height="9" fill="{ORANGE}"/>'))
d += 0.35
s.append(reveal(d, t(40, ly + 7 * CELL + 28, "ai & vibecoding · data science · simple words", ACC, 14)))

# инфо
CW5 = 9.0
RX0, RX1 = 32, W - 52  # границы полос


def stripe(yy, h=26):
    return f'<rect x="{RX0}" y="{yy-18}" width="{RX1-RX0}" height="{h}" rx="5" fill="{S1}" opacity=".85"/>'


def section(yy, title):
    return (t(40, yy, title, HI, 16, 700)
            + f'<line x1="{40 + (len(title)+1) * 9.6:.0f}" y1="{yy-5}" x2="{RX1}" y2="{yy-5}" stroke="{S2}"/>')


iy = ly + 7 * CELL + 70
s.append(reveal(d + 0.2, section(iy, "max@maxouni")))
rows = [
    ("role", "Data Scientist @ MagnitTech"),
    ("prev", "Wildberries"),
    ("focus", "вайбкодинг · AI-инструменты · DS/ML"),
    ("stack", "python · swift · typescript"),
    ("tg", "@maxouniai"),
]
for i, (k, v) in enumerate(rows):
    yy = iy + 36 + i * 28
    st = stripe(yy) if i % 2 == 0 else ""
    s.append(reveal(d + 0.5 + i * 0.18, st + t(48, yy, k, DIM, 15, 500) + t(48 + 9 * CW5, yy, v, HI, 15, 600)))
d2 = d + 0.5 + len(rows) * 0.18

# проекты
qy = iy + 36 + len(rows) * 28 + 26
s.append(reveal(d2 + 0.2, section(qy, "~/projects")))
projects = [
    ("coil", "iOS-трекер привычек", "swift"),
    ("mlsd", "45 кейсов ML System Design", "typescript"),
    ("mlcourse-ai", "открытый курс ML: домашки и решения", "jupyter"),
]
for i, (k, v, tag) in enumerate(projects):
    yy = qy + 36 + i * 28
    st = stripe(yy) if i % 2 == 0 else ""
    cw = (len(tag) + 2) * 7.8
    chip = (f'<rect x="{RX1-8-cw:.0f}" y="{yy-14}" width="{cw:.0f}" height="18" rx="9" fill="none" stroke="{MID}"/>'
            + t(RX1 - 8 - cw / 2, yy - 1, tag, ACC, 12).replace("<text ", '<text text-anchor="middle" '))
    s.append(reveal(d2 + 0.5 + i * 0.2, st + t(48, yy, k, HI, 15, 700) + t(48 + 14 * CW5, yy, v, FG, 15) + chip))
py = qy + 36 + len(projects) * 28

# промпт с курсором
cy = py + 34
s.append(reveal(d2 + 0.5, t(40, cy, "❯", ORANGE, 15, 700) + f'<rect class="cur" x="{60}" y="{cy-14}" width="10" height="18" fill="{ORANGE}"/>'))

s.append("</svg>")
(OUT / "hero.svg").write_text("\n".join(s), encoding="utf-8")

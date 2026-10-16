"""Генерирует карточки README: about.svg, pill-*.svg, card-*.svg. Запуск: python3 tools/gen_cards.py"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
BG, WIN, S1, S2, MID = "#0e0f10", "#131517", "#1a1c1e", "#383c40", "#6b6f72"
DIM, FG, ACC, HI, OR = "#9ba1a7", "#d9dcdf", "#aeb6be", "#ffffff", "#ff7a3d"
FONT = "'JetBrains Mono','SF Mono',ui-monospace,Menlo,Consolas,'DejaVu Sans Mono',monospace"
STYLE = ("<style>.r{opacity:0;animation:in .01s forwards}@keyframes in{to{opacity:1}}"
         ".cur{animation:blink 1.1s steps(1) infinite}@keyframes blink{50%{opacity:0}}</style>")


def t(x, y, text, fill=FG, size=13, weight=400):
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
            f'xml:space="preserve">{escape(text)}</text>')


def r(delay, inner):
    return f'<g class="r" style="animation-delay:{delay:.2f}s">{inner}</g>'


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}">'
            f'<title>{escape(title)}</title>{STYLE}{body}</svg>')


def window(w, h, title):
    return (f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="10" fill="{WIN}" stroke="{S2}"/>'
            f'<path d="M.5 10.5 a10 10 0 0 1 10 -10 h{w-21} a10 10 0 0 1 10 10 v18 h-{w-1} z" fill="{S1}"/>'
            + "".join(f'<circle cx="{20+i*16}" cy="15" r="4.5" fill="{c}"/>' for i, c in enumerate((MID, MID, OR)))
            + t(w / 2, 19, title, DIM, 11).replace('<text ', '<text text-anchor="middle" '))


def card(name, w, h, title, head, lines, tags, foot, fs=12.5):
    b = window(w, h, title)
    b += t(20, 58, head, HI, 15, 700)
    b += "".join(t(20, 84 + i * 19, ln, FG, fs) for i, ln in enumerate(lines))
    b += t(20, h - 52, tags, ACC, 11.5)
    b += f'<line x1="20" y1="{h-38}" x2="{w-20}" y2="{h-38}" stroke="{S2}"/>'
    b += t(20, h - 16, foot, OR, 12, 600)
    (OUT / f"{name}.svg").write_text(svg(w, h, b, head), encoding="utf-8")


def pill(name, label, value, w):
    b = (f'<rect x=".5" y=".5" width="{w-1}" height="39" rx="8" fill="{S1}" stroke="{S2}"/>'
         f'<rect x="0.5" y="30" width="{w-1}" height="2" fill="{OR}" opacity=".0"/>'
         + t(16, 25, "❯", OR, 14, 700) + t(34, 25, label, DIM, 13) + t(34 + (len(label) + 1) * 7.8, 25, value, FG, 13, 700))
    (OUT / f"{name}.svg").write_text(svg(w, 40, b, label + " " + value), encoding="utf-8")


# --- пилюли-ссылки
pill("pill-tg", "telegram", "@maxouniai", 250)
pill("pill-yt", "youtube", "карта DS", 230)
pill("pill-mlsd", "mlsd", "кейсы", 190)
pill("pill-gh", "github", "aimnoux", 210)

# --- about + git log
W, H = 900, 270
b = window(W, H, "about.md")
b += r(0.2, t(24, 58, "❯", OR, 14, 700) + t(44, 58, "cat about.md", FG, 14))
about = [
    "Привет, я Макс. Data Scientist в MagnitTech, раньше был в Wildberries.",
    "Сейчас пишу про вайбкодинг и AI-инструменты: как с Claude Code собирать",
    "приложения, сайты и даже монтировать видео. Остальное — инженерка и DS/ML простым языком.",
]
b += r(0.7, "".join(t(24, 84 + i * 20, ln, FG, 13.5) for i, ln in enumerate(about)))
gy = 172
b += r(1.4, t(24, gy, "❯", OR, 14, 700) + t(44, gy, "git log --graph --oneline", FG, 14))
log = [
    (OR, "*", "   ", "HEAD -> main", "MagnitTech · Data Scientist"),
    (ACC, "*", "   ", "", "Wildberries · Data Scientist"),
]
for i, (c, star, _, tag, msg) in enumerate(log):
    y = gy + 28 + i * 20
    inner = t(24, y, star, c, 13.5, 700)
    x = 24 + 3 * 8.1
    if tag:
        inner += t(x, y, "(" + tag + ")", OR, 13.5, 600)
        x += (len(tag) + 3) * 8.1
    inner += t(x, y, msg, FG if i == 0 else DIM, 13.5)
    b += r(1.8 + i * 0.25, inner)
b += r(3.3, t(24, H - 22, "❯", OR, 14, 700) + f'<rect class="cur" x="44" y="{H-35}" width="9" height="16" fill="{OR}"/>')
(OUT / "about.svg").write_text(svg(W, H, b, "about"), encoding="utf-8")

# --- медиа (2 карточки)
card("card-tg", 440, 226, "~/media/maxouni", "maxouni | ai & vibecoding",
     ["Вайбкодинг, AI-инструменты, инженерка,", "DS/ML простым языком.", "Серия про ветки Data Science, гайды",
      "по монтажу и Claude Code."], "telegram · основной проект", "открыть @maxouniai  ↗", 13)
card("card-yt", 440, 226, "~/media/youtube", "Вся карта Data Science за 19 минут",
     ["Семь направлений от Classic ML до HFT", "простыми словами и разбор, как по", "вакансии понять, куда тебя зовут.",
      "Смонтировано целиком с Claude."], "youtube · первое видео", "смотреть  ↗", 13)

# --- проекты (3 карточки)
card("card-coil", 290, 250, "~/projects/coil", "coil",
     ["iOS-трекер привычек для iPhone:", "нативный дизайн, без рекламы и", "аккаунтов. Сила привычки, серии,", "статистика, виджеты, iCloud."],
     "Swift · SwiftUI · SwiftData", "приватный репозиторий", 12)
card("card-mlsd", 290, 250, "~/projects/mlsd", "mlsd",
     ["45 кейсов ML System Design с", "реальных собеседований. Сайт с", "фильтрами по направлению и", "домену, 12 доменов."],
     "TypeScript · Vite · Pages", "aimnoux.github.io/mlsd  ↗", 12)
card("card-mlcourse", 290, 250, "~/projects/mlcourse-ai", "mlcourse-ai",
     ["Форк открытого курса mlcourse.ai", "от OpenDataScience: лекции,", "статьи, домашки и решения —", "от Pandas до обучения без учителя."],
     "Jupyter · pandas · sklearn", "открыть репозиторий  ↗", 12)
print("ok")

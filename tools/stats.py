"""Draws assets/stats.svg — the GITHUB STATS block in the README palette.
Runs daily in .github/workflows/stats.yml. Stdlib only; token from GITHUB_TOKEN or GH_TOKEN.
Local run: GH_TOKEN=$(gh auth token) python3 tools/stats.py"""
import json, os, random, urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USER = "aimnoux"
BLUE, RED = "#0a18ef", "#ff2a1f"
W, H = 830, 242

QUERY = """{user(login:"%s"){
 pullRequests{totalCount}
 repositories(ownerAffiliations:OWNER,first:100){nodes{stargazerCount}}
 contributionsCollection{totalCommitContributions contributionCalendar{totalContributions
  weeks{contributionDays{date contributionCount}}}}}}""" % USER


def fetch():
    token = os.environ.get("GITHUB_TOKEN") or os.environ["GH_TOKEN"]
    req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": QUERY}).encode(),
                                 {"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))["data"]["user"]


def streaks(days):
    """Current streak (today may still be empty) and the longest one with its dates."""
    counts = [(date.fromisoformat(d["date"]), d["contributionCount"]) for d in days]
    tail = counts[:-1] if counts and counts[-1][1] == 0 else counts
    cur = 0
    for _, c in reversed(tail):
        if not c:
            break
        cur += 1
    best, run, start, span = 0, 0, None, (None, None)
    for d, c in counts:
        run, start = (run + 1, start or d) if c else (0, None)
        if c and run > best:
            best, span = run, (start, d)
    return cur, best, span


def fmt(d):
    return f"{d:%b} {d.day}" if d else "—"


def text(x, y, s, size, fam="Onest", weight=400, anchor="start", op=1, extra=""):
    o = f' fill-opacity="{op}"' if op < 1 else ""
    return (f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}" fill="#fff"{o}{extra}>{s}</text>')


def ring(cx, cy, n, label):
    return (f'<circle cx="{cx}" cy="{cy}" r="43.5" fill="none" stroke="#fff" stroke-width="5"/>'
            + text(cx, cy + 10.5, n, 30, weight=700, anchor="middle")
            + text(cx, cy + 64, label, 11, "JBM", anchor="middle"))


def noise(n=40):
    rnd, ch = random.Random(7), "/-=+.:#|\\"
    return "".join(text(round(rnd.random() * W, 1), round(rnd.random() * H, 1),
                        "".join(rnd.choice(ch) for _ in range(1 + (rnd.random() < .3))), 13, "JBM", op=.16)
                   for _ in range(n))


def svg(u):
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    cur, best, (b0, b1) = streaks(days)
    stars = sum(r["stargazerCount"] for r in u["repositories"]["nodes"])
    commits = u["contributionsCollection"]["totalCommitContributions"]
    total = cal["totalContributions"]
    star = '<path d="M57 102l2.2 4.6 5 .7-3.6 3.5.9 5-4.5-2.4-4.5 2.4.9-5-3.6-3.5 5-.7z" fill="#fff"/>'
    swap = ('<path d="M51 134h11m-3-3l3 3-3 3M63 140H52m3-3l-3 3 3 3" stroke="#fff" stroke-width="1.6" '
            'fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    square = '<rect x="52.5" y="163.5" width="9" height="9" rx="1" fill="#fff"/>'
    rows = "".join(text(72, y, label, 13) + text(270, y, val, 13, "JBM", 700, "end")
                   for y, label, val in [(112, "stars", stars), (141, "pull requests", u["pullRequests"]["totalCount"]),
                                         (172, "contributions", total)])
    col = lambda cx, n, a, b: (text(cx, 136, n, 28, weight=700, anchor="middle") + text(cx, 158, a, 12, anchor="middle")
                               + text(cx, 175, b, 10, "JBM", anchor="middle", op=.62))
    css = (ROOT / "tools/fonts.css").read_text()
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<title>GitHub stats: {total} contributions last year, {cur}-day streak, longest {best}</title>
<style>{css}</style>
<rect width="{W}" height="{H}" rx="8" fill="{BLUE}"/>
{noise()}
{text(32, 54, "GITHUB STATS", 26, weight=700, extra=' letter-spacing="-0.26"')}
<g fill="none" stroke="#fff" stroke-opacity=".9" stroke-width="1.5">
 <rect x="32.75" y="73.75" width="374.5" height="144.5" rx="4"/><rect x="422.75" y="73.75" width="374.5" height="144.5" rx="4"/>
 <path d="M544 93v105M677 93v105"/></g>
{star}{swap}{square}{rows}
{ring(339, 136, commits, "commits")}
{col(488.5, total, "contributions", "last year")}
{ring(610.5, 136, cur, "day streak")}
{col(732.5, best, "longest", f"{fmt(b0)} – {fmt(b1)}")}
</svg>
"""


if __name__ == "__main__":
    (ROOT / "assets/stats.svg").write_text(svg(fetch()))
    print("assets/stats.svg")

"""Render the "control room" profile panels as animated SVGs.

Static panels (hero, rating plate, stack diagram, buttons) are pure design.
Project cards and the readings panel pull live numbers from the GitHub
GraphQL API, so a daily GitHub Action keeps them current.

Usage:  GITHUB_TOKEN=... python scripts/build.py
"""
import datetime as dt
import json
import math
import os
import textwrap
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

LOGIN = os.environ.get("GH_LOGIN", "Baraa-Melhem")
OUT = Path(__file__).resolve().parent.parent / "assets"

BG, PANEL, GRID, BORDER = "#0A0E14", "#0F151D", "#16202B", "#243142"
TXT, MUTED, DIM = "#E6EDF3", "#8593A3", "#5B6878"
R, Y, B, G, V = "#FF6B6B", "#FFD166", "#4CC9F0", "#06D6A0", "#B392F0"
SANS = "'Segoe UI', Inter, 'Helvetica Neue', Arial, sans-serif"
MONO = "'Cascadia Code', 'JetBrains Mono', Consolas, 'Liberation Mono', monospace"

HIDE_LANGS = {"Inno Setup", "Batchfile"}

PROJECTS = [
    ("CH1", R, "vidpaper", "vidpaper", "C++",
     "Loops any local video as your Windows desktop wallpaper, behind the icons. "
     "Native C++20, hardware-decoded, tiny footprint.", "saw"),
    ("CH2", Y, "SystemWatch", "SystemWatch", "Python",
     "Read-only Windows event monitor that explains what your PC is doing in "
     "plain English. No admin rights, no network.", "pulse"),
    ("CH3", B, "AUM2", "AUM2", "Python",
     "Hears emotion in a voice: five audio models read the tone, while "
     "speech-to-text and NLP read the words.", "audio"),
    ("CH4", G, "Recommendation-System---AI-Models", "NASA Space Apps", "Python",
     "Four LSTM classifiers that tag scientific posts by subject to drive an "
     "open-science recommendation system.", "step"),
]


def svg(w, h, body, css=""):
    base = (
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
        f"text{{font-family:{SANS}}} .m{{font-family:{MONO}}}"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" fill="none">'
        f"<style><![CDATA[{base}{css}]]></style>{body}</svg>\n"
    )


def frame(w, h, rx=16):
    return (f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{rx}" '
            f'fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>')


def caption(x, y, num, label):
    return (f'<text x="{x}" y="{y}" class="m" font-size="12" letter-spacing="2" '
            f'fill="{DIM}">// {num}  <tspan fill="{MUTED}">{escape(label)}</tspan></text>')


def grid(w, h, step=40, rx=16):
    return (
        f'<defs><pattern id="grid" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
        f'<path d="M{step} 0V{step}H0" stroke="{GRID}" stroke-width="1"/></pattern>'
        f'<clipPath id="clip"><rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="{rx}"/></clipPath></defs>'
        f'<rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="{rx}" fill="url(#grid)"/>'
    )


def sine_path(x0, x1, y0, amp, period, phase, step=4):
    pts = []
    x = x0
    while x <= x1:
        pts.append(f"{x:.0f} {y0 + amp * math.sin(2 * math.pi * x / period + phase):.1f}")
        x += step
    return "M" + " L".join(pts)


def smooth_path(pts):
    """Catmull-Rom spline through pts, as cubic Bezier segments."""
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[max(i - 1, 0)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d


# ---------------------------------------------------------------- hero
def hero():
    w, h, period = 1000, 320, 250
    waves = ""
    for i, col in enumerate((R, Y, B)):
        d = sine_path(0, w + period, 228, 46, period, -i * 2 * math.pi / 3)
        waves += (f'<path d="{d}" stroke="{col}" stroke-width="7" opacity=".12"/>'
                  f'<path d="{d}" stroke="{col}" stroke-width="2.2" opacity=".95"/>')
    css = (
        f".wave{{animation:drift 6s linear infinite}}"
        f"@keyframes drift{{to{{transform:translateX(-{period}px)}}}}"
        ".scan{animation:scan 7s linear infinite}"
        "@keyframes scan{from{transform:translateX(0)}to{transform:translateX(1000px)}}"
        ".in{opacity:0;animation:in .9s ease-out forwards}"
        ".d1{animation-delay:.15s}.d2{animation-delay:.45s}.d3{animation-delay:.8s}"
        "@keyframes in{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}"
        ".live{animation:blink 1.6s ease-in-out infinite}"
        "@keyframes blink{50%{opacity:.25}}"
    )
    body = (
        frame(w, h) + grid(w, h)
        + f'<g clip-path="url(#clip)"><g class="wave">{waves}</g>'
        f'<rect class="scan" x="-2" y="2" width="2" height="{h - 4}" fill="{TXT}" opacity=".12"/></g>'
        f'<line x1="2" y1="228" x2="{w - 2}" y2="228" stroke="{BORDER}" stroke-dasharray="2 6"/>'
        f'<g class="in d1"><text x="48" y="92" font-size="46" font-weight="700" fill="{TXT}">Al-Baraa Melhem</text></g>'
        f'<g class="in d2"><text x="50" y="130" font-size="20" fill="{MUTED}">Power Systems '
        f'<tspan fill="{Y}">×</tspan> Machine Learning</text></g>'
        f'<g class="in d3"><rect x="736" y="34" width="226" height="78" rx="10" fill="{PANEL}" stroke="{BORDER}"/>'
        f'<text x="754" y="60" class="m" font-size="12" fill="{DIM}">'
        f'<tspan fill="{R}">━ L1</tspan>  <tspan fill="{Y}">━ L2</tspan>  <tspan fill="{B}">━ L3</tspan></text>'
        f'<text x="754" y="82" class="m" font-size="12" fill="{MUTED}">f = 50.00 Hz   Δφ = 120°</text>'
        f'<circle class="live" cx="759" cy="99" r="4" fill="{G}"/>'
        f'<text x="770" y="103" class="m" font-size="11" fill="{G}" letter-spacing="1.5">ONLINE · JORDAN</text></g>'
        f'<text x="48" y="{h - 22}" class="m" font-size="11" fill="{DIM}" letter-spacing="2">'
        f"3φ · AI FOR POWER SYSTEMS · NATIVE TOOLS FOR WINDOWS</text>"
    )
    return svg(w, h, body, css)


# ---------------------------------------------------------------- buttons
def button(label, hint, col):
    w, h = 214, 46
    body = (f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="23" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>'
            f'<circle cx="26" cy="23" r="5" fill="{col}"/><circle cx="26" cy="23" r="10" stroke="{col}" opacity=".35"/>'
            f'<text x="46" y="28.5" font-size="15" font-weight="600" fill="{TXT}">{label}</text>'
            f'<text x="{w - 20}" y="28" text-anchor="end" class="m" font-size="11" fill="{DIM}">{hint}</text>')
    return svg(w, h, body)


# ---------------------------------------------------------------- rating plate
def nameplate(created):
    w, h = 1000, 262
    rows = [
        ("TYPE", "Power engineer · ML engineer", "INPUT", "speech · text · images · power signals"),
        ("MFG", "Yarmouk University", "OUTPUT", "trained models · native Windows tools"),
        ("THESIS", "Partial-discharge detection with AI", "LANGUAGES", "Python · C++20 · Lua · PowerShell"),
        ("EVENTS", "NASA Space Apps 2023 · Sirius team", "LOCATION", "Jordan · 50 Hz grid"),
    ]
    css = (".row{opacity:0;animation:in .7s ease-out forwards}"
           "@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}")
    body = frame(w, h)
    for cx, cy in ((22, 22), (w - 22, 22), (22, h - 22), (w - 22, h - 22)):
        body += f'<circle cx="{cx}" cy="{cy}" r="5" fill="{PANEL}" stroke="{BORDER}"/>'
    body += (f'<rect x="44" y="40" width="{w - 88}" height="1" fill="{BORDER}"/>'
             + caption(44, 30, "01", "RATING PLATE")
             + f'<text x="{w - 44}" y="30" text-anchor="end" class="m" font-size="12" '
               f'letter-spacing="2" fill="{DIM}">S/N BM-{created}</text>')
    for i, (k1, v1, k2, v2) in enumerate(rows):
        y = 84 + i * 44
        body += (f'<g class="row" style="animation-delay:{0.15 + i * 0.15:.2f}s">'
                 f'<text x="48" y="{y}" class="m" font-size="12" letter-spacing="1.5" fill="{DIM}">{k1}</text>'
                 f'<text x="160" y="{y}" font-size="16" fill="{TXT}">{escape(v1)}</text>'
                 f'<text x="530" y="{y}" class="m" font-size="12" letter-spacing="1.5" fill="{DIM}">{k2}</text>'
                 f'<text x="650" y="{y}" font-size="16" fill="{TXT}">{escape(v2)}</text>'
                 f'<line x1="48" y1="{y + 16}" x2="{w - 48}" y2="{y + 16}" stroke="{GRID}"/></g>')
    return svg(w, h, body, css)


# ---------------------------------------------------------------- stack as single-line diagram
def stack():
    w, h = 1000, 330
    ml = ["TensorFlow", "PyTorch", "scikit-learn", "OpenCV", "NLTK · spaCy"]
    sysl = ["C++20", "Win32 · DX", "Qt", "Lua", "PowerShell"]
    css = (".flow{stroke-dasharray:5 9;animation:flow 1.1s linear infinite}"
           "@keyframes flow{to{stroke-dashoffset:-28}}"
           ".load{opacity:0;animation:in .6s ease-out forwards}"
           "@keyframes in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}")

    def wire(x1, y1, x2, y2, col, width=2):
        return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{width}" opacity=".35"/>'
                f'<line class="flow" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{width}"/>')

    body = frame(w, h) + caption(44, 34, "02", "SINGLE-LINE DIAGRAM · STACK")
    gx, gy = 500, 76
    body += (f'<circle cx="{gx}" cy="{gy}" r="21" fill="{PANEL}" stroke="{Y}" stroke-width="2"/>'
             f'<path d="{sine_path(gx - 12, gx + 12, gy, 6, 24, 0, 2)}" stroke="{Y}" stroke-width="2"/>'
             f'<text x="{gx + 34}" y="{gy - 2}" font-size="16" font-weight="600" fill="{TXT}">Python</text>'
             f'<text x="{gx + 34}" y="{gy + 16}" class="m" font-size="11" fill="{DIM}">GENERATOR · CORE LANGUAGE</text>')
    body += wire(gx, gy + 21, gx, 128, Y, 2.5)
    body += (f'<line x1="70" y1="128" x2="930" y2="128" stroke="{Y}" stroke-width="5" stroke-linecap="round"/>'
             f'<text x="70" y="118" class="m" font-size="11" letter-spacing="1.5" fill="{DIM}">MAIN BUS</text>')
    for fx, col, x0, x1, name, loads in ((270, B, 50, 490, "ML · DATA", ml), (730, R, 510, 950, "SYSTEMS", sysl)):
        body += wire(fx, 128, fx, 192, col)
        body += f'<rect x="{fx - 7}" y="153" width="14" height="14" rx="2" fill="{BG}" stroke="{col}" stroke-width="2"/>'
        body += (f'<line x1="{x0 + 8}" y1="192" x2="{x1 - 8}" y2="192" stroke="{col}" stroke-width="4" stroke-linecap="round"/>'
                 f'<text x="{x0 + 8}" y="182" class="m" font-size="11" letter-spacing="1.5" fill="{col}">{name}</text>')
        for i, label in enumerate(loads):
            cx = x0 + 44 + i * 88
            body += wire(cx, 192, cx, 236, col, 1.6)
            body += (f'<g class="load" style="animation-delay:{0.2 + i * 0.1:.1f}s">'
                     f'<rect x="{cx - 41}" y="236" width="82" height="38" rx="9" fill="{PANEL}" stroke="{BORDER}"/>'
                     f'<rect x="{cx - 41}" y="236" width="82" height="3" rx="1.5" fill="{col}" opacity=".8"/>'
                     f'<text x="{cx}" y="260" text-anchor="middle" font-size="12" fill="{TXT}">{escape(label)}</text></g>')
    body += (f'<text x="{w - 44}" y="{h - 22}" text-anchor="end" class="m" font-size="11" fill="{DIM}">'
             f"also on the bus: git · GitHub Actions · Anaconda · VS Code</text>")
    return svg(w, h, body, css)


# ---------------------------------------------------------------- project cards
def trace(kind, x0, x1, y0, amp):
    n = 120
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        if kind == "saw":
            v = 2 * ((t * 6) % 1) - 1
        elif kind == "pulse":
            v = 1 if (t * 9) % 1 < 0.12 else -0.6 + 0.15 * math.sin(t * 40)
        elif kind == "audio":
            v = math.sin(t * 2 * math.pi * 14) * (0.35 + 0.65 * abs(math.sin(t * math.pi * 3)))
        else:
            v = -1 + 2 / (1 + math.exp(-14 * (t - 0.5)))
        pts.append(f"{x:.1f} {y0 - amp * v:.1f}")
    return "M" + " L".join(pts)


def card(tag, col, title, lang, desc, kind, stars):
    w, h = 490, 186
    css = (".tr{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 2.2s ease-out .3s forwards}"
           "@keyframes draw{to{stroke-dashoffset:0}}"
           ".led{animation:blink 2s ease-in-out infinite}@keyframes blink{50%{opacity:.3}}")
    lines = textwrap.wrap(desc, 60)[:3]
    body = (frame(w, h, 14)
            + f'<rect x="24" y="24" width="46" height="22" rx="6" fill="{col}" opacity=".15"/>'
            f'<text x="47" y="39.5" text-anchor="middle" class="m" font-size="12" font-weight="700" fill="{col}">{tag}</text>'
            f'<text x="84" y="42" font-size="21" font-weight="700" fill="{TXT}">{escape(title)}</text>'
            f'<circle class="led" cx="{w - 30}" cy="35" r="5" fill="{col}"/>')
    for i, line in enumerate(lines):
        body += f'<text x="24" y="{76 + i * 21}" font-size="14" fill="{MUTED}">{escape(line)}</text>'
    body += (f'<line x1="24" y1="152" x2="{w - 150}" y2="152" stroke="{GRID}"/>'
             f'<path class="tr" pathLength="1" d="{trace(kind, 24, w - 150, 152, 13)}" stroke="{col}" stroke-width="2"/>'
             f'<text x="{w - 24}" y="157" text-anchor="end" class="m" font-size="12" fill="{MUTED}">'
             f'{lang}  <tspan fill="{Y}">★</tspan> {stars}</text>')
    return svg(w, h, body, css)


def section(num, label, note):
    w, h = 1000, 40
    body = (caption(4, 26, num, label)
            + f'<line x1="250" y1="21" x2="{w - 190}" y2="21" stroke="{BORDER}"/>'
              f'<text x="{w - 4}" y="26" text-anchor="end" class="m" font-size="11" fill="{DIM}">{note}</text>')
    return svg(w, h, body)


# ---------------------------------------------------------------- live readings
def nice_max(v):
    v = max(v * 1.4, 10)
    mag = 10 ** math.floor(math.log10(v))
    for m in (1, 2, 2.5, 5, 10):
        if v <= m * mag:
            return int(m * mag)
    return int(10 * mag)


def gauge(i, cx, cy, value, label, col):
    r = 70
    top = nice_max(value)
    f = min(value / top, 1)
    arc = f"M{cx - r} {cy} A{r} {r} 0 0 1 {cx + r} {cy}"
    ticks = ""
    for k in range(11):
        a = math.pi - k * math.pi / 10
        r1, r2 = (r - 14, r - 6) if k % 5 else (r - 18, r - 6)
        ticks += (f'<line x1="{cx + r1 * math.cos(a):.1f}" y1="{cy - r1 * math.sin(a):.1f}" '
                  f'x2="{cx + r2 * math.cos(a):.1f}" y2="{cy - r2 * math.sin(a):.1f}" stroke="{DIM}" stroke-width="1.5"/>')
    css = (f".a{i}{{stroke-dasharray:0 100;animation:a{i} 1.6s cubic-bezier(.2,.8,.2,1) .2s forwards}}"
           f"@keyframes a{i}{{to{{stroke-dasharray:{f * 100:.1f} 100}}}}"
           f".n{i}{{transform-origin:{cx}px {cy}px;animation:n{i} 1.6s cubic-bezier(.2,.8,.2,1) .2s forwards}}"
           f"@keyframes n{i}{{to{{transform:rotate({f * 180:.1f}deg)}}}}")
    body = (f'<path d="{arc}" stroke="{GRID}" stroke-width="9" stroke-linecap="round"/>'
            f'<path class="a{i}" d="{arc}" pathLength="100" stroke="{col}" stroke-width="9" stroke-linecap="round"/>'
            + ticks
            + f'<g class="n{i}"><line x1="{cx}" y1="{cy}" x2="{cx - r + 20}" y2="{cy}" stroke="{TXT}" stroke-width="2.5" stroke-linecap="round"/></g>'
              f'<circle cx="{cx}" cy="{cy}" r="6" fill="{BG}" stroke="{TXT}" stroke-width="2"/>'
              f'<text x="{cx - r}" y="{cy + 18}" text-anchor="middle" class="m" font-size="10" fill="{DIM}">0</text>'
              f'<text x="{cx + r}" y="{cy + 18}" text-anchor="middle" class="m" font-size="10" fill="{DIM}">{top}</text>'
              f'<text x="{cx}" y="{cy + 40}" text-anchor="middle" class="m" font-size="26" font-weight="700" fill="{TXT}">{value}</text>'
              f'<text x="{cx}" y="{cy + 60}" text-anchor="middle" class="m" font-size="11" letter-spacing="1.5" fill="{MUTED}">{label}</text>')
    return body, css


def readings(d, today):
    w, h = 1000, 470
    css_all = (".tr{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 2.6s ease-out .4s forwards}"
               "@keyframes draw{to{stroke-dashoffset:0}}"
               ".bar{transform-origin:50px 0;transform:scaleX(0);animation:grow 1.4s cubic-bezier(.2,.8,.2,1) .3s forwards}"
               "@keyframes grow{to{transform:scaleX(1)}}")
    body = frame(w, h) + caption(44, 34, "04", "LIVE READINGS")
    body += (f'<text x="{w - 44}" y="34" text-anchor="end" class="m" font-size="11" fill="{DIM}">'
             f"auto-refreshed daily · {today}</text>")
    meters = [(d["contrib"], "CONTRIBUTIONS · 12 MO", G), (d["commits"], f"COMMITS · {today[:4]}", Y),
              (d["stars"], "STARS EARNED", R), (d["repos"], "PUBLIC PROJECTS", B)]
    for i, (val, label, col) in enumerate(meters):
        g, c = gauge(i, 140 + i * 240, 150, val, label, col)
        body += g
        css_all += c

    # 52-week activity trace
    x0, x1, yb, ht = 50, 950, 330, 60
    weeks = d["weeks"] or [0]
    top = max(max(weeks), 1)
    pts = [(x0 + (x1 - x0) * k / max(len(weeks) - 1, 1), yb - ht * v / top) for k, v in enumerate(weeks)]
    body += (f'<text x="{x0}" y="254" class="m" font-size="11" letter-spacing="1.5" fill="{DIM}">'
             f'ACTIVITY TRACE · LAST 52 WEEKS <tspan fill="{MUTED}">· peak {top}/wk</tspan></text>')
    for k in range(3):
        yy = yb - ht * k / 2
        body += f'<line x1="{x0}" y1="{yy:.0f}" x2="{x1}" y2="{yy:.0f}" stroke="{GRID}" stroke-dasharray="2 5"/>'
    path = smooth_path(pts)
    body += (f'<path d="{path} L{x1} {yb} L{x0} {yb} Z" fill="{G}" opacity=".07"/>'
             f'<path class="tr" pathLength="1" d="{path}" stroke="{G}" stroke-width="2.2"/>')

    # language mix
    body += f'<text x="50" y="372" class="m" font-size="11" letter-spacing="1.5" fill="{DIM}">LANGUAGE MIX · PUBLIC REPOS</text>'
    langs = d["langs"]
    total = sum(v for _, v in langs) or 1
    palette = [B, Y, R, G, V, MUTED]
    x, bar, legend, lx = 50.0, "", "", 50
    for k, (name, size) in enumerate(langs):
        seg = 900 * size / total
        bar += f'<rect x="{x:.1f}" y="384" width="{max(seg - 2, 1):.1f}" height="12" fill="{palette[k]}"/>'
        x += seg
        pct = f"{100 * size / total:.1f}%"
        legend += (f'<circle cx="{lx + 5}" cy="426" r="5" fill="{palette[k]}"/>'
                   f'<text x="{lx + 16}" y="430.5" font-size="13" fill="{TXT}">{escape(name)} '
                   f'<tspan class="m" font-size="11" fill="{MUTED}">{pct}</tspan></text>')
        lx += 150
    body += (f'<defs><clipPath id="barclip"><rect x="50" y="384" width="900" height="12" rx="6"/></clipPath></defs>'
             f'<g clip-path="url(#barclip)"><g class="bar">{bar}</g></g>{legend}')
    return svg(w, h, body, css_all)


# ---------------------------------------------------------------- data
def fetch():
    token = os.environ["GITHUB_TOKEN"]
    year_start = dt.datetime(dt.date.today().year, 1, 1).isoformat() + "Z"
    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    query = """
    query($login:String!, $ys:DateTime!, $now:DateTime!) {
      user(login:$login) {
        createdAt
        contributionsCollection { contributionCalendar { totalContributions
          weeks { contributionDays { contributionCount } } } }
        thisYear: contributionsCollection(from:$ys, to:$now) { totalCommitContributions restrictedContributionsCount }
        repositories(first:100, ownerAffiliations:OWNER, privacy:PUBLIC, isFork:false) {
          nodes { name stargazerCount
            languages(first:10, orderBy:{field:SIZE, direction:DESC}) { edges { size node { name } } } } }
      }
    }"""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"login": LOGIN, "ys": year_start, "now": now}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if "errors" in payload:
        raise SystemExit(payload["errors"])
    u = payload["data"]["user"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    repos = [r for r in u["repositories"]["nodes"] if r["name"] != LOGIN]
    sizes = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            if e["node"]["name"] not in HIDE_LANGS:
                sizes[e["node"]["name"]] = sizes.get(e["node"]["name"], 0) + e["size"]
    ranked = sorted(sizes.items(), key=lambda kv: -kv[1])
    langs = ranked[:5]
    rest = sum(v for _, v in ranked[5:])
    if rest:
        langs.append(("Other", rest))
    return {
        "created": u["createdAt"][:7],
        "contrib": cal["totalContributions"],
        "weeks": [sum(day["contributionCount"] for day in wk["contributionDays"]) for wk in cal["weeks"]][-52:],
        "commits": u["thisYear"]["totalCommitContributions"] + u["thisYear"]["restrictedContributionsCount"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "repos": len(repos),
        "langs": langs,
        "star_map": {r["name"]: r["stargazerCount"] for r in repos},
    }


def main():
    d = fetch()
    today = dt.date.today().isoformat()
    OUT.mkdir(exist_ok=True)
    files = {
        "hero.svg": hero(),
        "btn-linkedin.svg": button("LinkedIn", "in/", B),
        "btn-kaggle.svg": button("Kaggle", "notebooks", Y),
        "btn-email.svg": button("Email", "gmail", R),
        "nameplate.svg": nameplate(d["created"]),
        "stack.svg": stack(),
        "section-projects.svg": section("03", "CHANNELS · FEATURED PROJECTS", "click a channel to open it"),
        "readings.svg": readings(d, today),
    }
    for tag, col, repo, title, lang, desc, kind in PROJECTS:
        files[f"card-{tag.lower()}.svg"] = card(tag, col, title, lang, desc, kind, d["star_map"].get(repo, 0))
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
    print(f"wrote {len(files)} panels to {OUT}")


if __name__ == "__main__":
    main()

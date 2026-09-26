from xml.sax.saxutils import escape

ART_FILE = "/home/claude/art.txt"

# ---------- CONTENT (edit here) ----------
HEADER = "zerowave-tech"          # shown as  user@name ----------
WIDTH_CHARS = 58               # width of the right column in characters

# (section, [(key, value), ...])
SECTIONS = [
    (None, [
        ("Languages.Programming", "Python, C#, JavaScript"),
        ("Languages.Web", "HTML, CSS"),
        ("Frameworks", "Django"),
        ("Database", "PostgreSQL, Supabase"),
    ]),
    (None, [
        ("Experience", "1 year"),
        ("Projects.Bots", "Telegram/Discord bots"),
        ("Projects.Games", "1 game"),
        ("Projects.Web", "sikra.agency, slapa.agency"),
    ]),
    (None, [
        ("Languages.Real", "English, Russian, Ukrainian, Hungarian"),
    ]),
]

THEMES = {
    "dark_mode": dict(mode="dark", bg="#0d1117", border="#30363d", art="#c9d1d9", key="#ffa657", val="#a5d6ff", dots="#616e7f", head="#c9d1d9"),
    "light_mode": dict(mode="light", bg="#f6f8fa", border="#d0d7de", art="#24292f", key="#953800", val="#0a3069", dots="#c2cfde", head="#24292f"),
}
# -----------------------------------------

DENS = {" ": 0.0, ".": 0.07, ":": 0.16, "-": 0.38, "=": 0.52, "+": 0.66, "*": 0.80, "#": 0.92, "%": 1.0, "@": 1.0}

import json
COLORS = json.load(open("/home/claude/art_colors.json"))


def tone(hexcol, mode):
    r, g, b = (int(hexcol[k:k + 2], 16) for k in (0, 2, 4))
    if mode == "dark":      # lift dark colours so they stay visible on a dark card
        f = 0.45
        r, g, b = (int(v * (1 - f) + 255 * f) for v in (r, g, b))
    else:                   # slightly deepen for a light card
        r, g, b = (int(v * 0.82) for v in (r, g, b))
    # quantise to keep the file small
    q = lambda v: min(255, (v // 8) * 8 + 4)
    return "#%02x%02x%02x" % (q(r), q(g), q(b))


art = open(ART_FILE).read().split("\n")
while art and not art[-1].strip():
    art.pop()

ART_FS = 7.0
ART_CW = 4.2            # width of one art character, px
ART_LH = 7.17           # art line height, px
TXT_FS = 17
TXT_CW = 10.2           # monospace char width at 16px (0.6 em)
TXT_LH = 46

pad = 22
art_w = len(art[0]) * ART_CW
art_h = len(art) * ART_LH
gap = 28
txt_w = WIDTH_CHARS * TXT_CW
W = int(pad + art_w + gap + txt_w + pad)
BAR = 34                # terminal title-bar height
H = int(art_h + 2 * pad + BAR)

# build right column rows: ("head", text) | ("kv", k, v) | ("blank",)
rows = [("head", HEADER)]
for title, items in SECTIONS:
    rows.append(("blank",))
    if title:
        rows.append(("sec", title))
    for k, v in items:
        rows.append(("kv", k, v))

col_x = pad + art_w + gap
start_y = BAR + (H - BAR - len(rows) * TXT_LH) / 2 + TXT_LH


def build(t):
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="1"/>')
    # terminal title bar
    o.append(f'<line x1="0.5" y1="{BAR}" x2="{W-0.5}" y2="{BAR}" stroke="{t["border"]}" stroke-width="1"/>')
    for cx, col in ((20, "#ff5f56"), (40, "#ffbd2e"), (60, "#27c93f")):
        o.append(f'<circle cx="{cx}" cy="{BAR/2:.1f}" r="6" fill="{col}"/>')
    o.append(f'<text x="{W/2:.1f}" y="{BAR/2+4.5:.1f}" text-anchor="middle" font-family="Consolas, \'Courier New\', monospace" font-size="13" fill="{t["dots"]}">{escape(HEADER)}@89.134.93.94 · Budapest</text>')
    # ASCII art
    o.append(f'<g font-family="Consolas, \'Courier New\', monospace" font-size="{ART_FS}" fill="{t["art"]}" xml:space="preserve">')
    for i, line in enumerate(art):
        y = BAR + pad + (i + 1) * ART_LH
        runs = []                      # [colour, start_col, text]
        for j, ch in enumerate(line):
            if ch == " ":
                continue
            c = tone(COLORS[i][j], t["mode"])
            if runs and runs[-1][0] == c and runs[-1][1] + len(runs[-1][2]) == j:
                runs[-1][2] += ch
            else:
                runs.append([c, j, ch])
        if not runs:
            continue
        spans = "".join(
            f'<tspan x="{pad + s * ART_CW:.1f}" fill="{c}" textLength="{len(txt) * ART_CW:.1f}" lengthAdjust="spacingAndGlyphs">{escape(txt)}</tspan>'
            for c, s, txt in runs
        )
        o.append(f'<text y="{y:.1f}">{spans}</text>')
    o.append("</g>")
    # Right column
    o.append(f'<g font-family="Consolas, \'Courier New\', monospace" font-size="{TXT_FS}" xml:space="preserve">')
    for i, r in enumerate(rows):
        y = start_y + i * TXT_LH
        if r[0] == "head":
            n = WIDTH_CHARS - len(r[1]) - 2
            o.append(f'<text x="{col_x:.1f}" y="{y:.1f}" textLength="{(WIDTH_CHARS-1)*TXT_CW:.1f}" fill="{t["head"]}">{escape(r[1])} <tspan fill="{t["dots"]}">{"-" * n}</tspan></text>')
        elif r[0] == "sec":
            n = WIDTH_CHARS - len(r[1]) - 3
            o.append(f'<text x="{col_x:.1f}" y="{y:.1f}" fill="{t["head"]}">- {escape(r[1])} <tspan fill="{t["dots"]}">{"-" * n}</tspan></text>')
        elif r[0] == "kv":
            k, v = r[1] + ":", r[2]
            n = max(2, WIDTH_CHARS - len(k) - len(v) - 3)
            o.append(
                f'<text x="{col_x:.1f}" y="{y:.1f}" textLength="{WIDTH_CHARS*TXT_CW:.1f}"><tspan fill="{t["dots"]}">. </tspan>'
                f'<tspan fill="{t["key"]}">{escape(k)}</tspan> '
                f'<tspan fill="{t["dots"]}">{"." * n}</tspan> '
                f'<tspan fill="{t["val"]}">{escape(v)}</tspan></text>'
            )
    o.append("</g>")
    o.append("</svg>")
    return "\n".join(o)


for name, t in THEMES.items():
    with open(f"/home/claude/out/{name}.svg", "w", encoding="utf-8") as f:
        f.write(build(t))
    print("wrote", name, W, H)

from xml.sax.saxutils import escape

ART_FILE = "/mnt/user-data/uploads/ascii-art.txt"

# ---------- CONTENT (edit here) ----------
HEADER = "zerowave-tech"          # shown as  user@name ----------
WIDTH_CHARS = 58               # width of the right column in characters

# (section, [(key, value), ...])
SECTIONS = [
    (None, [
        ("Languages.Programming", "Python, C#, JavaScript"),
        ("Languages.Web", "HTML, CSS"),
        ("Frameworks", "Django"),
        ("Database", "PostgreSQL"),
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
    "dark_mode": dict(bg="#161b22", art="#c9d1d9", key="#ffa657", val="#a5d6ff", dots="#616e7f", head="#c9d1d9"),
    "light_mode": dict(bg="#f6f8fa", art="#24292f", key="#953800", val="#0a3069", dots="#c2cfde", head="#24292f"),
}
# -----------------------------------------

DENS = {" ": 0.0, ".": 0.07, ":": 0.16, "-": 0.38, "=": 0.52, "+": 0.66, "*": 0.80, "#": 0.92, "%": 1.0, "@": 1.0}

art = open(ART_FILE).read().split("\n")
while art and not art[-1].strip():
    art.pop()

ART_FS = 5.7
ART_CW = 3.4            # width of one art character, px
ART_LH = 5.8            # art line height, px
TXT_FS = 15
TXT_CW = 9.0            # monospace char width at 16px (0.6 em)
TXT_LH = 22

pad = 22
art_w = len(art[0]) * ART_CW
art_h = len(art) * ART_LH
gap = 28
txt_w = WIDTH_CHARS * TXT_CW
W = int(pad + art_w + gap + txt_w + pad)
H = int(art_h + 2 * pad)

# build right column rows: ("head", text) | ("kv", k, v) | ("blank",)
rows = [("head", HEADER)]
for title, items in SECTIONS:
    rows.append(("blank",))
    if title:
        rows.append(("sec", title))
    for k, v in items:
        rows.append(("kv", k, v))

col_x = pad + art_w + gap
start_y = (H - len(rows) * TXT_LH) / 2 + TXT_LH


def build(t):
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    o.append(f'<rect width="{W}" height="{H}" rx="15" fill="{t["bg"]}"/>')
    # ASCII art
    o.append(f'<g font-family="Consolas, \'Courier New\', monospace" font-size="{ART_FS}" font-weight="bold" fill="{t["art"]}" xml:space="preserve">')
    for i, line in enumerate(art):
        y = pad + (i + 1) * ART_LH
        runs = []
        for ch in line:
            op = DENS.get(ch, 1.0)
            if runs and runs[-1][0] == op:
                runs[-1][1] += ch
            else:
                runs.append([op, ch])
        spans = "".join(
            f'<tspan fill-opacity="{op}">{escape(txt)}</tspan>' for op, txt in runs
        )
        o.append(f'<text x="{pad}" y="{y:.1f}" textLength="{art_w:.1f}" lengthAdjust="spacingAndGlyphs">{spans}</text>')
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

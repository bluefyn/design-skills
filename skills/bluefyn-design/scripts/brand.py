"""Bluefyn brand primitives, taken from the Figma brand guide (v1.0).

Standard library only. Every function returns an SVG string.

Tokens, the master logo artwork and the generators for the brand's own
graphics: the digit field, records and marks, the tower, the platform
plates and the record texture.
"""
import math
import os
import re
from html import escape

import base64

HERE = os.path.dirname(os.path.abspath(__file__))
# Assets sit in ../assets inside the skill, or in ./assets in a local kit made by `one_pager.py init`.
ASSETS = next((p for p in (os.path.join(HERE, "assets"), os.path.join(os.path.dirname(HERE), "assets"))
               if os.path.isdir(p)), os.path.join(os.path.dirname(HERE), "assets"))

# ---------------------------------------------------------------- tokens
INK = "#1C1919"
INK_SOFT = "#696969"
INK_FAINT = "#999999"
RULE = "#DCDCDC"
PAPER = "#F5F5F5"
CARD = "#EBEBEB"
NIGHT = "#0F0F0F"
BLUE = "#0035A6"
NAVY = "#00386D"
LIGHT_BLUE = "#91CFFF"
GREEN = "#00A83F"
RED = "#E8170C"
WHITE = "#FFFFFF"

MARK_FILL = {"checking": BLUE, "match": GREEN, "off": RED}

# ------------------------------------------------------------------ logo
with open(os.path.join(ASSETS, "bluefyn-logo.svg")) as fh:
    _LOGO_PATHS = re.findall(r'<path d="([^"]+)"', fh.read())
SYMBOL_PATHS = _LOGO_PATHS[:4]
WORDMARK_PATHS = _LOGO_PATHS[4:]
LOGO_W, LOGO_H = 503.58, 113.2
SYMBOL_W, SYMBOL_H = 116.38, 113.2


def _paths(paths, fill):
    return "".join(f'<path d="{d}" fill="{fill}"/>' for d in paths)


def logo(fill=INK, height=13, unit="pt", cls="logo"):
    w = height * LOGO_W / LOGO_H
    return (f'<svg class="{cls}" xmlns="http://www.w3.org/2000/svg" width="{w:.2f}{unit}" '
            f'height="{height}{unit}" viewBox="0 0 {LOGO_W} {LOGO_H}" role="img" '
            f'aria-label="Bluefyn">{_paths(_LOGO_PATHS, fill)}</svg>')


def symbol(fill=INK, height=13, unit="pt", cls="symbol"):
    w = height * SYMBOL_W / SYMBOL_H
    return (f'<svg class="{cls}" xmlns="http://www.w3.org/2000/svg" width="{w:.2f}{unit}" '
            f'height="{height}{unit}" viewBox="0 0 {SYMBOL_W} {SYMBOL_H}" role="img" '
            f'aria-label="Bluefyn symbol">{_paths(SYMBOL_PATHS, fill)}</svg>')


def wordmark(fill=INK, height=13, unit="pt", cls="wordmark"):
    # Wordmark bounds inside the logo artwork.
    x0, y0, x1, y1 = 172.98, 18.87, 503.58, 112.66
    w = height * (x1 - x0) / (y1 - y0)
    return (f'<svg class="{cls}" xmlns="http://www.w3.org/2000/svg" width="{w:.2f}{unit}" '
            f'height="{height}{unit}" viewBox="{x0} {y0} {x1 - x0:.2f} {y1 - y0:.2f}" role="img" '
            f'aria-label="Bluefyn">{_paths(WORDMARK_PATHS, fill)}</svg>')


# ---------------------------------------------------------- arial metrics
_AW = {c: 556 for c in "0123456789$"}
_AW.update({" ": 278, "/": 278, ".": 278, ",": 278, ":": 278, "-": 333, "+": 584,
            "=": 584, "x": 500, "%": 889, "(": 333, ")": 333, "|": 260, "&": 667,
            ">": 584, "I": 278, "J": 500, "L": 556, "F": 611, "T": 611, "Z": 611,
            "M": 833, "W": 944, "G": 778, "O": 778, "Q": 778, "C": 722, "D": 722,
            "H": 722, "N": 722, "R": 722, "U": 722})
for _c in "ABEKPSVXY":
    _AW[_c] = 667
DIGIT_EM = 0.556


def arial_width(text, size):
    return sum(_AW.get(c, 556) for c in text) * size / 1000.0


# ------------------------------------------------------------- randomness
class Rng:
    """Small deterministic generator so every build draws the same field."""

    def __init__(self, seed):
        self.x = seed & 0x7FFFFFFF

    def next(self):
        self.x = (self.x * 1103515245 + 12345) & 0x7FFFFFFF
        return self.x >> 8

    def below(self, n):
        return self.next() % n


def digit_row(cols, rng):
    """Digits that drift in short runs, the way the tower's rows do."""
    out = []
    d = rng.below(10)
    while len(out) < cols:
        run = 1 + rng.below(4)
        out.extend(str(d) * run)
        step = rng.below(7)
        if step < 3:
            d = (d + 1) % 10
        elif step < 5:
            d = (d - 1) % 10
        else:
            d = rng.below(10)
    return "".join(out[:cols])


# The brand's own sample records, as drawn in the guide's imagery.
REC_TX_CHECKING = (["TX-001 / CT-001:4.2", "ST-009 LINE 128", "CHECKING"], "checking")
REC_OFF = (["CHARGED 42.00", "CONTRACT 35.00", "VARIANCE +7.00", "OFF CONTRACT"], "off")
REC_MATCH = (["TX-002 / VOLUME USD", "8,000.00", "FEE USD 28.00", "MATCH"], "match")
REC_FX = (["FX-002 / EUR-USD", "MID 1.100000", "CHECKING"], "checking")
REC_INVOICE = (["INV-0318 / C-014", "1.2M TOKENS USED", "1M BILLED", "CHECKING"], "checking")
REC_MATH = (["10,000.00 x 35 BPS = 35.00", "42.00 - 35.00 = +7.00"], "plain")
REC_CLAUSE = (["CT-001 / CLAUSE 4.2", "RATE 35 BPS"], "plain")
REC_VOLUME = (["VOLUME USD 8,000.00", "FEE USD 28.00", "CHECKING"], "checking")


def field(w, h, fs, rng, records=(), paper=WHITE, ink=INK, lh=None, stripes=True, uid="f", rec_ink=None):
    """A digit field in local coordinates: rows of Arial digits with records
    set into them. records: (row, col, (lines, kind))."""
    lh = lh or fs * 1.16
    cw = fs * DIGIT_EM
    cols = int(math.ceil(w / cw)) + 1
    rows = int(math.ceil(h / lh)) + 1
    base = lambda r: r * lh + lh / 2 + fs * 0.358
    o = [f'<rect width="{w:.2f}" height="{h:.2f}" fill="{paper}"/>']
    o.append(f'<g font-family="Arial, Helvetica, sans-serif" font-size="{fs:.3f}" fill="{ink}" '
             f'style="font-kerning:none;font-variant-numeric:tabular-nums">')
    for r in range(rows):
        o.append(f'<text x="0" y="{base(r):.2f}">{digit_row(cols, rng)}</text>')
    for row, col, (lines, kind) in records:
        fill = MARK_FILL.get(kind, paper)
        tcol = (rec_ink or ink) if kind == "plain" else WHITE
        for i, line in enumerate(lines):
            cells = int(math.ceil((arial_width(line, fs) + fs * 0.35) / cw))
            x = col * cw
            y = (row + i) * lh
            o.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{cells * cw:.2f}" height="{lh + 0.05:.2f}" fill="{fill}"/>')
            o.append(f'<text x="{x + fs * 0.17:.2f}" y="{base(row + i):.2f}" fill="{tcol}">{escape(line)}</text>')
    o.append("</g>")
    if stripes:
        # The LCD finish: fine horizontal stripes over the paper.
        o.append(f'<pattern id="lcd-{uid}" width="4" height="{lh / 4:.3f}" patternUnits="userSpaceOnUse">'
                 f'<rect width="4" height="{lh / 16:.3f}" fill="{ink}" opacity="0.07"/></pattern>'
                 f'<rect width="{w:.2f}" height="{h:.2f}" fill="url(#lcd-{uid})"/>')
    return "".join(o)


COS30, SIN30 = math.cos(math.radians(30)), 0.5


def tower(box_w, box_h, cx, y_near, wl, wr, height, fs=6.0, seed=7, records=None, uid="t",
          angle_l=30.0, angle_r=30.0, shades=(WHITE, "#DFDFDF", "#EFEFEF")):
    """The block of records: three faces of one digit field. cx / y_near place
    the top corner nearest the viewer. At 30 degrees it is a true isometric
    block; shallower angles give the wide slab of the posters."""
    rng = Rng(seed)
    rec = records or {}
    cl, sl = math.cos(math.radians(angle_l)), math.sin(math.radians(angle_l))
    cr, sr = math.cos(math.radians(angle_r)), math.sin(math.radians(angle_r))
    lx, ly = cx - wl * cl, y_near - wl * sl                # left corner of the top face
    faces = []
    # top face: rows run along the back-left edge, stack toward the viewer
    faces.append((f"matrix({cr:.5f} {-sr:.5f} {cl:.5f} {sl:.5f} {lx:.2f} {ly:.2f})",
                  wr, wl, rec.get("top", ()), shades[0], "top"))
    faces.append((f"matrix({cl:.5f} {sl:.5f} 0 1 {lx:.2f} {ly:.2f})",
                  wl, height, rec.get("left", ()), shades[1], "left"))
    faces.append((f"matrix({cr:.5f} {-sr:.5f} 0 1 {cx:.2f} {y_near:.2f})",
                  wr, height, rec.get("right", ()), shades[2], "right"))
    o = [f'<svg class="tower" xmlns="http://www.w3.org/2000/svg" width="{box_w}pt" height="{box_h}pt" '
         f'viewBox="0 0 {box_w} {box_h}" aria-hidden="true"><defs>']
    for _, w, h, _, _, name in faces:
        o.append(f'<clipPath id="{uid}-{name}"><rect width="{w:.2f}" height="{h:.2f}"/></clipPath>')
    o.append("</defs>")
    for tf, w, h, records_, paper, name in faces:
        o.append(f'<g transform="{tf}"><g clip-path="url(#{uid}-{name})">'
                 f'{field(w, h, fs, rng, records_, paper=paper, uid=f"{uid}-{name}")}</g></g>')
    o.append("</svg>")
    return "".join(o)


def plates(labels, w=152, h=88, side=60.0, ink=INK, soft=INK_SOFT, line=INK_FAINT,
           paper=PAPER, top_fill=WHITE, label_size=6.8, uid="p", label_ink=None, font="Geist"):
    """The platform stack: Bluefyn as the top plate above the tools it reads,
    one record at a time. Square plates in a true isometric view.
    labels[0] names the top plate."""
    ca, sa = COS30, SIN30
    pu = pv = side
    n = len(labels)
    step = (h - (pu + pv) * sa - 2) / max(n - 1, 1)
    x0 = w - (pu + pv) * ca - 1
    y0 = pu * sa + 1
    rows = [("TX-002 28.00", "MATCH", "match"), ("ST-009 128", "CHECKING", "checking"),
            ("FX-002 1.10", "MATCH", "match")]
    fs = side * 0.07
    lh = side * 0.2
    o = [f'<svg class="plates" xmlns="http://www.w3.org/2000/svg" width="{w}pt" height="{h}pt" '
         f'viewBox="0 0 {w} {h}" role="img" aria-label="Bluefyn sits as a layer above {", ".join(labels[1:])}">']
    for i in reversed(range(n)):
        y = y0 + i * step
        tf = f"matrix({ca:.5f} {-sa:.5f} {ca:.5f} {sa:.5f} {x0:.2f} {y:.2f})"
        o.append(f'<g transform="{tf}">')
        if i == 0:
            o.append(f'<rect width="{pu}" height="{pv}" fill="{top_fill}" stroke="{ink}" stroke-width="0.5"/>'
                     f'<g font-family="Arial, Helvetica, sans-serif" font-size="{fs:.2f}" style="font-kerning:none">')
            for r, (text, verdict, kind) in enumerate(rows):
                by = side * 0.32 + r * lh
                vw = arial_width(verdict, fs) + fs * 0.6
                o.append(f'<text x="{side * 0.07:.2f}" y="{by:.2f}" fill="{ink}">{escape(text)}</text>'
                         f'<rect x="{pu - side * 0.07 - vw:.2f}" y="{by - fs * 0.95:.2f}" width="{vw:.2f}" height="{fs * 1.3:.2f}" fill="{MARK_FILL[kind]}"/>'
                         f'<text x="{pu - side * 0.07 - vw + fs * 0.3:.2f}" y="{by:.2f}" fill="{WHITE}">{verdict}</text>')
                o.append(f'<line x1="{side * 0.07:.2f}" x2="{pu - side * 0.07:.2f}" y1="{by - lh * 0.62:.2f}" y2="{by - lh * 0.62:.2f}" stroke="{RULE}" stroke-width="0.3"/>')
            o.append("</g>")
        else:
            o.append(f'<rect width="{pu}" height="{pv}" fill="{paper}" stroke="{line}" stroke-width="0.4"/>')
            for r in range(3):
                o.append(f'<rect x="{side * 0.07:.2f}" y="{side * 0.26 + r * lh:.2f}" width="{side * (0.5, 0.38, 0.44)[r]:.2f}" height="{side * 0.035:.2f}" fill="{RULE}"/>')
        o.append("</g>")
    for i, label in enumerate(labels):
        y = y0 + i * step
        lead = label_ink or ink
        o.append(f'<line x1="{arial_width(label, label_size) * 1.02 + 5:.2f}" y1="{y:.2f}" x2="{x0:.2f}" y2="{y:.2f}" '
                 f'stroke="{lead if i == 0 else line}" stroke-width="0.4"/>')
        o.append(f'<text x="0" y="{y + label_size * 0.34:.2f}" font-family="{font}, sans-serif" font-size="{label_size}" '
                 f'fill="{lead if i == 0 else soft}">{escape(label)}</text>')
    o.append("</svg>")
    return "".join(o)


def record_texture(w, h, fs=3.6, seed=11, fill=WHITE, opacity=0.11, cls="texture"):
    """The record texture on poster navy: the check log, line after line."""
    rng = Rng(seed)
    lh = fs * 1.38
    rows = int(h / lh) + 2
    o = [f'<svg class="{cls}" xmlns="http://www.w3.org/2000/svg" width="{w}pt" height="{h}pt" '
         f'viewBox="0 0 {w} {h}" preserveAspectRatio="xMinYMin slice" aria-hidden="true">'
         f'<g font-family="Arial, Helvetica, sans-serif" font-size="{fs}" fill="{fill}" opacity="{opacity}">']
    usd = 4.14
    for r in range(rows):
        parts = []
        length = 0
        while length < w / (fs * 0.5) + 60:
            pct = 80 + rng.below(21)
            n = 3669 * pct // 100
            verdict = "OFF CONTRACT" if rng.below(6) == 0 else "MATCH"
            seg = f"{verdict} Checking transactions: {pct}% ({n}/3669), USD {usd:.2f}M"
            parts.append(seg)
            length += len(seg) + 3
            usd += rng.below(60) / 100.0
        line = " | ".join(parts)
        o.append(f'<text x="{-rng.below(60)}" y="{r * lh + fs:.2f}">{escape(line)}</text>')
    o.append("</g></svg>")
    return "".join(o)


def data_uri(name, mime):
    """An asset as a data URI, so the built HTML needs no files beside it."""
    with open(os.path.join(ASSETS, name), "rb") as fh:
        return f"data:{mime};base64," + base64.b64encode(fh.read()).decode("ascii")


def geist_face():
    return ('@font-face{font-family:"Geist";src:url("' + data_uri("fonts/Geist-Variable.woff2", "font/woff2")
            + '") format("woff2");font-weight:100 900;font-style:normal;font-display:block}')


def texture():
    """The record texture as an image (see texture.py for why it is not live text)."""
    return data_uri("texture.png", "image/png")


def grain(kind):
    """The fine grain tile: "dark" has white specks for dark grounds, "light" has ink specks for paper."""
    return data_uri(f"grain-{kind}.png", "image/png")


# ------------------------------------------------- more of the guide's graphics
REC_TX_MATCH = (["TX-001 / CT-001:4.2", "ST-009 LINE 128", "MATCH"], "match")
REC_FX_MATCH = (["FX-002 / EUR-USD", "MID 1.100000", "MATCH"], "match")


def scan_band(w, h, scan_x, fs=6.4, seed=61, uid="scan"):
    """The check, mid-scan: a flat digit field. Left of the scan line every
    record has its verdict; right of it the records are still CHECKING."""
    rng = Rng(seed)
    cw = fs * DIGIT_EM
    col = lambda x: int(x / cw)
    left, right = scan_x, w - scan_x
    recs = [(2, col(left * 0.07), REC_TX_MATCH), (1, col(left * 0.50), REC_OFF),
            (3, col(scan_x + right * 0.03), REC_TX_CHECKING), (1, col(scan_x + right * 0.27), REC_FX),
            (2, col(scan_x + right * 0.53), REC_INVOICE), (4, col(scan_x + right * 0.80), REC_VOLUME),
            (6, col(scan_x + right * 0.30), REC_MATH)]
    return (f'<svg class="scanfield" xmlns="http://www.w3.org/2000/svg" width="{w}pt" height="{h}pt" '
            f'viewBox="0 0 {w} {h}" aria-hidden="true"><defs><clipPath id="{uid}-c"><rect width="{w}" height="{h}"/></clipPath></defs>'
            f'<g clip-path="url(#{uid}-c)">{field(w, h, fs, rng, recs, paper=WHITE, uid=uid)}'
            f'<line x1="{scan_x}" x2="{scan_x}" y1="0" y2="{h}" stroke="{BLUE}" stroke-width="1"/></g></svg>')


def slanted_field(w, h, fs=7.0, angle=-24, seed=83, paper=INK, ink="#DCDCDC", uid="sl"):
    """The dark slab of records, cropped: one large field turned on the page,
    with a record every few rows placed where the crop will show it."""
    rng = Rng(seed)
    lh = fs * 1.16
    cw = fs * DIGIT_EM
    t = math.tan(math.radians(-angle))
    c = math.cos(math.radians(-angle))
    fw = w / c + h * t + 60
    fh = h / c + w * t + 60
    half = w / (2 * c)
    cycle = [REC_OFF, REC_TX_CHECKING, REC_MATCH, REC_FX, REC_MATH, REC_INVOICE, REC_TX_MATCH, REC_VOLUME, REC_CLAUSE]
    recs = []
    r, i = 3, 0
    while r * lh < fh - 6 * lh:
        yc = r * lh - fh / 2
        xc = fw / 2 - t * yc                  # where the crop's centre line crosses this row
        x = xc - half * (0.78 - 0.5 * (rng.below(100) / 100.0))
        recs.append((r, max(0, int(x / cw)), cycle[i % len(cycle)]))
        i += 1
        r += 6 + rng.below(3)
    return (f'<svg class="slanted" xmlns="http://www.w3.org/2000/svg" width="{w}pt" height="{h}pt" viewBox="0 0 {w} {h}" '
            f'aria-hidden="true"><defs><clipPath id="{uid}-c"><rect width="{w}" height="{h}"/></clipPath></defs>'
            f'<g clip-path="url(#{uid}-c)"><rect width="{w}" height="{h}" fill="{paper}"/>'
            f'<g transform="translate({w / 2:.2f} {h / 2:.2f}) rotate({angle}) translate({-fw / 2:.2f} {-fh / 2:.2f})">'
            f'{field(fw, fh, fs, rng, recs, paper=paper, ink=ink, uid=uid)}</g></g></svg>')


def discs(w, h, r, pitch, cy, fill=WHITE, stripe=NAVY, seed=19, notch=42, offset=0.0, uid="d"):
    """The discs: a row of full circles, each with one notch cut out, under the LCD finish."""
    rng = Rng(seed)
    o = [f'<svg class="discs" xmlns="http://www.w3.org/2000/svg" width="{w}pt" height="{h}pt" viewBox="0 0 {w} {h}" '
         f'aria-hidden="true"><defs><pattern id="{uid}-lcd" width="4" height="2.2" patternUnits="userSpaceOnUse">'
         f'<rect width="4" height="0.55" fill="{stripe}" opacity="0.22"/></pattern>'
         f'<clipPath id="{uid}-c"><rect width="{w}" height="{h}"/></clipPath></defs><g clip-path="url(#{uid}-c)">']
    x = offset
    while x - r < w:
        a0 = math.radians(200 + rng.below(140))            # notches open upward, where the crop shows them
        a1, a2 = a0 - math.radians(notch / 2), a0 + math.radians(notch / 2)
        p1 = (x + r * math.cos(a2), cy + r * math.sin(a2))
        p2 = (x + r * math.cos(a1), cy + r * math.sin(a1))
        o.append(f'<path d="M{x:.2f} {cy:.2f}L{p1[0]:.2f} {p1[1]:.2f}A{r} {r} 0 1 1 {p2[0]:.2f} {p2[1]:.2f}Z" fill="{fill}"/>')
        x += pitch
    o.append(f'<rect width="{w}" height="{h}" fill="url(#{uid}-lcd)"/></g></svg>')
    return "".join(o)


def stream(w, h, fs=3.6, seed=31, fill=WHITE, opacity=0.1, cls="texture"):
    """The checking stream: the record texture run in vertical columns."""
    inner = record_texture(h, w, fs=fs, seed=seed, fill=fill, opacity=opacity)
    inner = inner[inner.index("<g "):inner.rindex("</svg>")]
    return (f'<svg class="{cls}" xmlns="http://www.w3.org/2000/svg" width="{w}pt" height="{h}pt" viewBox="0 0 {w} {h}" '
            f'aria-hidden="true"><g transform="translate(0 {h}) rotate(-90)">{inner}</g></svg>')


def ellipses(w, h, n, rx, ry, gap, top, paper=PAPER, ink=INK, fs=5.4, angle=-34,
             words="contracts. evidence. ", font="Geist", seed=47, uid="el"):
    """The ellipses poster: a stack of paper ellipses, each filled with the
    same two words of contract language set on a slant."""
    rng = Rng(seed)
    lh = fs * 1.42
    cx = w / 2.0
    o = [f'<svg class="ellipses" xmlns="http://www.w3.org/2000/svg" width="{w}pt" height="{h}pt" viewBox="0 0 {w} {h}" '
         f'aria-hidden="true"><defs>']
    cys = [top + ry + i * (2 * ry + gap) for i in range(n)]
    for i, cy in enumerate(cys):
        o.append(f'<clipPath id="{uid}-{i}"><ellipse cx="{cx}" cy="{cy:.2f}" rx="{rx}" ry="{ry}"/></clipPath>')
    o.append("</defs>")
    line = words * (int(4 * rx / (len(words) * fs * 0.46)) + 3)
    for i, cy in enumerate(cys):
        o.append(f'<ellipse cx="{cx}" cy="{cy:.2f}" rx="{rx}" ry="{ry}" fill="{paper}"/>'
                 f'<g clip-path="url(#{uid}-{i})"><g transform="rotate({angle} {cx} {cy:.2f})" font-family="{font}, sans-serif" '
                 f'font-size="{fs}" fill="{ink}">')
        y = cy - rx - lh
        while y < cy + rx + lh:
            o.append(f'<text x="{cx - rx * 1.6 - rng.below(40):.2f}" y="{y:.2f}">{escape(line)}</text>')
            y += lh
        o.append("</g></g>")
    o.append("</svg>")
    return "".join(o)


def slab(w, h, x0, y0, length, rise=3.5, depth=(46.0, -27.0), rows_deep=15, fs=6.2, seed=71,
         records=(), top_records=(), shades=(WHITE, "#EDEDED"), uid="slab", ink=INK, rec_ink=None):
    """The slab of the poster: a long block of records seen from the front and
    a little above. A front face of level rows, and a top face running away
    behind it. x0 / y0 place the front face's top-left corner."""
    rng = Rng(seed)
    r = math.radians(rise)
    cr, sr = math.cos(r), math.sin(r)
    lh = fs * 1.16
    deep = rows_deep * lh                              # the top face's depth, in its own plane
    dx, dy = depth
    front_h = h + length * sr + 20
    o = [f'<svg class="tower slab" xmlns="http://www.w3.org/2000/svg" width="{w}pt" height="{h}pt" viewBox="0 0 {w} {h}" '
         f'aria-hidden="true"><defs><clipPath id="{uid}-t"><rect width="{length}" height="{deep:.2f}"/></clipPath>'
         f'<clipPath id="{uid}-f"><rect width="{length}" height="{front_h:.2f}"/></clipPath></defs>']
    # top face: far edge first, rows stacking toward the front edge
    o.append(f'<g transform="matrix({cr:.5f} {-sr:.5f} {-dx / deep:.5f} {-dy / deep:.5f} {x0 + dx:.2f} {y0 + dy:.2f})">'
             f'<g clip-path="url(#{uid}-t)">{field(length, deep, fs, rng, top_records, paper=shades[0], ink=ink, rec_ink=rec_ink, uid=uid + "-t")}</g></g>')
    o.append(f'<g transform="matrix({cr:.5f} {-sr:.5f} 0 1 {x0:.2f} {y0:.2f})">'
             f'<g clip-path="url(#{uid}-f)">{field(length, front_h, fs, rng, records, paper=shades[1], ink=ink, rec_ink=rec_ink, uid=uid + "-f")}</g></g>')
    o.append("</svg>")
    return "".join(o)

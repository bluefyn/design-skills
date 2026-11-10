#!/usr/bin/env python3
"""Build a Bluefyn one pager (US Letter, one page) from a content JSON file.

    python3 one_pager.py content.json --out ./out [--mode light|dark|both] [--density auto|roomy|regular|tight]
    python3 one_pager.py init ./my-one-pager        copy the template into a folder you can tune

Writes <name>-<mode>.html, .pdf and .png into --out, and prints a report: the
spacing it chose, the space left above the footer, the page count and anything
to fix. Standard library only; needs Chrome, Chromium, Edge or Brave for the PDF
(set CHROME=/path/to/browser if it is not found).

The brand colors, logo, font and drawings come from the bluefyn-design skill,
which must be installed next to this one. A kit made by `init` carries its own copy.

Exit codes: 0 fits with nothing to fix, 2 built but there is a problem or a copy warning to deal with,
1 could not build. Lines marked "note" are advice and do not change the exit code.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from html import escape as _escape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True          # keep __pycache__ out of the installed skills


def find_brand():
    """The folder that holds brand.py: this folder (a local kit), $BLUEFYN_DESIGN_DIR, or the bluefyn-design skill."""
    skills = os.path.dirname(os.path.dirname(HERE))
    env = os.environ.get("BLUEFYN_DESIGN_DIR")
    candidates = [HERE] + ([os.path.join(env, "scripts"), env] if env else []) + [
        os.path.join(skills, "bluefyn-design", "scripts"),
        os.path.join(os.path.expanduser("~"), ".claude", "skills", "bluefyn-design", "scripts")]
    for folder in candidates:
        if os.path.isfile(os.path.join(folder, "brand.py")):
            return folder
    raise SystemExit("Cannot find the bluefyn-design skill. Install it next to bluefyn-one-pager "
                     "(the pack's install.sh installs both), or set BLUEFYN_DESIGN_DIR to its folder.")


BRAND_DIR = find_brand()
sys.path.insert(0, BRAND_DIR)
import brand as b  # noqa: E402


def esc(text):
    """Escape text for HTML and keep hyphenated words (usage-based) on one line."""
    return re.sub(r"\b\w+(?:-\w+)+\b", lambda m: f'<span class="nb">{m.group(0)}</span>', _escape(str(text)))


G_DARK = f'url("{b.grain("dark")}") 0 0 / 108pt 108pt'
G_LIGHT = f'url("{b.grain("light")}") 0 0 / 108pt 108pt'

TOKENS = {"$INK": b.INK, "$SOFT": b.INK_SOFT, "$FAINT": b.INK_FAINT, "$RULE": b.RULE, "$PAPER": b.PAPER,
          "$NIGHT": b.NIGHT, "$BLUE": b.BLUE, "$NAVY": b.NAVY, "$LIGHT": b.LIGHT_BLUE,
          "$GDARK": G_DARK, "$GLIGHT": G_LIGHT, "$TEX": f'url("{b.texture()}")'}

# Spacing presets. The builder tries them in this order and keeps the first that fits.
DENSITY = {
    "roomy":   {"gap": 22, "row": 4.4, "flag": 4.6, "withfig": 28, "withdesc": 15.5, "withpad": 17, "closing": 9.5, "foot": 74},
    "regular": {"gap": 18, "row": 3.8, "flag": 3.7, "withfig": 26, "withdesc": 15.0, "withpad": 14, "closing": 9.2, "foot": 70},
    "tight":   {"gap": 13, "row": 2.4, "flag": 2.6, "withfig": 21, "withdesc": 13.5, "withpad": 10, "closing": 9.0, "foot": 64},
}
MIN_SPARE = {"roomy": 16, "regular": 12, "tight": 8}     # points that must stay free above the footer
MAX_STRETCH = 14                                         # most extra space added between two sections

CSS = """
@page{size:612pt 792pt;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:612pt;height:792pt}
body{font-family:"Geist",Arial,sans-serif;font-weight:400;color:$INK;font-size:9.1pt;line-height:1.42;
  -webkit-print-color-adjust:exact;print-color-adjust:exact;font-synthesis:none;text-rendering:geometricPrecision}
.page{position:relative;width:612pt;height:792pt;overflow:hidden;background:$PAPER $GLIGHT}
h1,h2{font-weight:400}
ul{list-style:none}
p,li,.desc,.then{text-wrap:pretty}
a{color:inherit;text-decoration:none}
.nb{white-space:nowrap}
svg{display:block}
.grain{position:absolute;left:0;top:0;right:0;bottom:0;background:$GDARK}
.label{font-size:7.8pt;line-height:1.2;color:$BLUE}
.num{font-variant-numeric:tabular-nums}
.mark{font-family:Arial,Helvetica,sans-serif;font-size:6.1pt;line-height:1;text-transform:uppercase;background:$BLUE;
  color:#fff;padding:1.9pt 3.2pt 1.5pt;white-space:nowrap;letter-spacing:0}

/* poster header: navy, the record texture, grain */
.poster{position:relative;background:$NAVY;color:#fff;overflow:hidden;padding-bottom:22pt}
.texture{position:absolute;left:0;top:0;right:0;bottom:0;background:$TEX 0 0 / 612pt auto;opacity:.11}
.top{position:relative;display:flex;justify-content:space-between;align-items:center;margin:0 36pt;padding:22pt 0 0}
.lockup{display:flex;align-items:center;gap:9pt}
.lockup .x{font-size:10pt;line-height:1;color:rgba(255,255,255,.8)}
.lockup .partner{font-size:12.4pt;line-height:1;letter-spacing:-.02em}
.meta{display:flex;gap:16pt;font-size:7.8pt;line-height:1;color:rgba(255,255,255,.92)}
.pgrid{position:relative;display:grid;grid-template-columns:172pt 356pt;column-gap:12pt;margin:22pt 36pt 0;align-items:start}
.pgrid.solo{grid-template-columns:1fr}
h1{font-size:27pt;line-height:1.03;letter-spacing:-.038em;word-spacing:.04em}
.lede{margin-top:10pt;font-size:9.3pt;line-height:1.46;color:#fff;max-width:340pt}
.poster .label,.next .label,.layer .label{color:$LIGHT}
.told .label{margin-bottom:4pt}
.told .row{padding:4pt 0 4.4pt;border-top:.5pt solid rgba(255,255,255,.5)}
.told .fig{font-size:16pt;line-height:1.05;letter-spacing:-.035em}
.told .desc{font-size:8.6pt;line-height:1.28;color:#fff;margin-top:1.5pt}

/* everything below sits on three columns at 36, 220 and 404 pt */
.g3{display:grid;grid-template-columns:172pt 172pt 172pt;column-gap:12pt;margin-left:36pt;margin-right:36pt}
.g2{display:grid;grid-template-columns:264pt 264pt;column-gap:12pt;margin-left:36pt;margin-right:36pt}

.with{margin:var(--gap) 36pt 0;padding-bottom:var(--withpad);border-bottom:.5pt solid $FAINT}
.with .g3{margin:0;align-items:end}
.with .label{margin-bottom:5pt}
.with .fig{font-size:var(--withfig);line-height:1;letter-spacing:-.04em}
.with .desc{grid-column:2 / span 2;font-size:var(--withdesc);line-height:1.15;letter-spacing:-.025em;padding-bottom:2.4pt}

.sidesrow{margin-top:var(--gap);grid-template-rows:auto 1fr;row-gap:7pt}
.sidesrow .l1{grid-column:1;grid-row:1}
.sidesrow .l2{grid-column:2;grid-row:1;white-space:nowrap}
.sidesrow .c1{grid-column:1;grid-row:2}
.sidesrow .c2{grid-column:2;grid-row:2}
.col{border-top:.75pt solid $INK;padding-top:8pt}
.col h2{display:flex;justify-content:space-between;align-items:center;gap:6pt;font-size:13.4pt;line-height:1.15;letter-spacing:-.02em}
.col .sub{margin-top:3pt;font-size:9pt;line-height:1.34;min-height:24.2pt}
.col ul{margin-top:7pt}
.col li{font-size:9pt;line-height:1.3;padding:var(--row) 0 calc(var(--row) - .2pt);border-top:.5pt solid $FAINT}
.layer{grid-column:3;grid-row:1 / span 2;background:$NIGHT $GDARK;color:#fff;padding:10pt 11pt 11pt;display:flex;
  flex-direction:column;justify-content:space-between}
.layer p{font-size:11pt;line-height:1.24;letter-spacing:-.015em}

.flags{margin:var(--gap) 36pt 0}
.flags .label{margin-bottom:6pt}
.flag{display:grid;grid-template-columns:172pt 1fr;column-gap:12pt;padding:var(--flag) 0 calc(var(--flag) - .2pt);
  border-top:.5pt solid $FAINT;font-size:9.3pt;line-height:1.3}
.flag:last-child{border-bottom:.5pt solid $FAINT}

.closing{margin-top:var(--gap)}
.closing .label{margin-bottom:5pt}
.closing p,.closing li{font-size:var(--closing);line-height:1.42}
.closing p{padding-right:2pt}
.closing.one > div{grid-column:1 / span 2}

/* full-width footer */
.next{position:absolute;left:0;right:0;bottom:0;height:var(--foot);background:$NAVY;color:#fff;overflow:hidden}
.next .texture{background-position:0 -150pt;opacity:.1}
.next .g3{position:relative;height:100%;align-items:center}
.next .say{grid-column:1 / span 2}
.next .say.full{grid-column:1 / span 3}
.next .label{margin-bottom:4pt}
.next p{font-size:12.4pt;line-height:1.22;letter-spacing:-.02em;max-width:344pt}
.tag{border:.5pt solid rgba(255,255,255,.6);background:$NAVY}
.tag .name{display:flex;align-items:center;gap:6pt;padding:6pt 8pt 5.5pt;font-size:10.6pt;line-height:1.1;letter-spacing:-.012em;
  border-bottom:.5pt solid rgba(255,255,255,.6)}
.tag .who{display:flex;justify-content:space-between;gap:8pt;padding:5.5pt 8pt;font-size:7.3pt;line-height:1.1;white-space:nowrap;
  overflow:hidden;color:#fff}
.tag .who > span:last-child{color:$LIGHT}

/* dark mode: the same page on ink */
.dark{background:$INK $GDARK;color:#EBEBEB}
.dark .label{color:#BDBDBD}
.dark .poster .label,.dark .next .label,.dark .layer .label,.dark .with .label{color:$LIGHT}
.dark .with{border-bottom-color:rgba(255,255,255,.28)}
.dark .with .fig,.dark .with .desc{color:$LIGHT}
.dark .col{border-top-color:#EBEBEB}
.dark .col h2,.dark .flag .if{color:#fff}
.dark .col .sub{color:#BDBDBD}
.dark .col li,.dark .flag{border-top-color:rgba(255,255,255,.28)}
.dark .flag:last-child{border-bottom-color:rgba(255,255,255,.28)}
.dark .layer{border:.5pt solid rgba(255,255,255,.28)}
"""

# Runs in the browser at build time and reports the fit. It is not part of the PDF.
MEASURE = """<script>
addEventListener('load',()=>{document.fonts.ready.then(()=>{
  const pt=v=>Math.round(v*75)/100, r=document.documentElement, q=s=>[...document.querySelectorAll(s)];
  const lines=e=>Math.round(e.getBoundingClientRect().height/parseFloat(getComputedStyle(e).lineHeight));
  const foot=document.querySelector('.next').getBoundingClientRect().top;
  const kids=[...document.querySelector('.content').children];
  const bottom=kids.length?Math.max(...kids.map(k=>k.getBoundingClientRect().bottom)):0;
  const wide=q('[data-fit]').filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>e.dataset.fit);
  const cols=q('.col ul').map(e=>e.getBoundingClientRect().bottom);
  const lock=document.querySelector('.lockup').getBoundingClientRect(), meta=document.querySelector('.meta').getBoundingClientRect();
  if(meta.width>0&&meta.left-lock.right<12) wide.push('partner and meta (the top line)');
  r.dataset.wide=wide.join('|'); r.dataset.spare=pt(foot-bottom); r.dataset.gaps=kids.length;
  r.dataset.h1=lines(document.querySelector('h1'));
  r.dataset.titles=q('.col h2').map(e=>e.getBoundingClientRect().height>parseFloat(getComputedStyle(e).lineHeight)*1.6?1:0).join('');
  r.dataset.coldiff=cols.length===2?pt(Math.abs(cols[0]-cols[1])):0;
  r.dataset.figs=q('.told .fig,.with .fig').filter(e=>lines(e)>1).length;
})});
</script>"""

BANNED = {"\u2014": "an em dash", "\u2013": "an en dash", "\u00b7": "a middle dot", "\u2022": "a bullet", "\u2192": "an arrow",
          "!": "an exclamation point"}


# ------------------------------------------------------------------ content
def need(obj, key, where):
    if not isinstance(obj, dict) or key not in obj or obj[key] in (None, "", []):
        raise SystemExit(f"content error: {where}.{key} is required")
    return obj[key]


def strings(node, path=""):
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, list):
        for i, item in enumerate(node):
            yield from strings(item, f"{path}[{i}]")
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from strings(value, f"{path}.{key}" if path else key)


def copy_warnings(content):
    out = []
    for path, text in strings(content):
        for ch, name in BANNED.items():
            if ch in text:
                out.append(f"{path}: contains {name} ({text[:60]!r})")
        if re.search(r"\b[A-Z]{2,}(?:\s+[A-Z]{2,})+\b", text) and "mark" not in path:
            out.append(f"{path}: reads as an all-caps label, set it in sentence case ({text[:60]!r})")
    return out


def looks_numeric(text):
    return bool(re.match(r"^[\s$€£]*\d", text))


# ------------------------------------------------------------------- markup
def poster(c):
    told = c.get("told")
    told_html = ""
    if told:
        rows = "".join(
            f'<div class="row"><div class="fig{" num" if looks_numeric(r["figure"]) else ""}">{esc(r["figure"])}</div>'
            f'<div class="desc">{esc(r["text"])}</div></div>' for r in need(told, "rows", "told"))
        told_html = f'<div class="told"><div class="label">{esc(need(told, "label", "told"))}</div>{rows}</div>'
    lede = f'<p class="lede">{esc(c["lede"])}</p>' if c.get("lede") else ""
    meta = "".join(f"<span>{esc(m)}</span>" for m in c.get("meta", []))
    partner = (f'<span class="x">×</span><span class="partner">{esc(c["partner"])}</span>' if c.get("partner") else "")
    return (f'<section class="poster"><div class="texture"></div><div class="grain"></div>'
            f'<header class="top"><div class="lockup">{b.logo(b.WHITE, 13)}{partner}</div><div class="meta">{meta}</div></header>'
            f'<div class="pgrid{"" if told else " solo"}">{told_html}<div><h1>{esc(need(c, "headline", "content"))}</h1>{lede}</div></div>'
            f'</section>')


def with_block(c):
    w = c.get("with")
    if not w:
        return ""
    return (f'<div class="with"><div class="g3"><div><div class="label">{esc(need(w, "label", "with"))}</div>'
            f'<div class="fig">{esc(need(w, "figure", "with"))}</div></div><div class="desc">{esc(need(w, "text", "with"))}</div></div></div>')


def plates(stack, dark):
    svg = b.plates(stack, w=150, h=92, side=60, font="Geist", label_size=7, uid="pl", ink=b.INK, label_ink="#FFFFFF",
                   soft="#DCDCDC", line="#999999", paper="#1A1A1A", top_fill="#FFFFFF")
    return svg.replace(f'fill="{b.RULE}"/>', 'fill="#3A3A3A"/>')


def sides(c, dark):
    s = c.get("sides")
    if not s:
        return ""
    cols = need(s, "columns", "sides")
    if len(cols) != 2:
        raise SystemExit("content error: sides.columns needs exactly two columns")
    layer = c.get("layer")
    label, note = s.get("label", ""), s.get("note", "")
    if note and not label:                 # a lone note sits over the first column, not beside a hole
        label, note = note, ""
    out = [f'<div class="{"g3" if layer else "g2"} sidesrow">',
           f'<div class="label l1">{esc(label)}</div>',
           f'<div class="label l2" data-fit="sides.note">{esc(note)}</div>']
    for i, col in enumerate(cols, 1):
        mark = f' <span class="mark">{esc(col["mark"])}</span>' if col.get("mark") else ""
        sub = f'<p class="sub">{esc(col["sub"])}</p>' if col.get("sub") else ""
        items = "".join(f"<li>{esc(t)}</li>" for t in need(col, "items", f"sides.columns[{i - 1}]"))
        out.append(f'<div class="col c{i}"><h2>{esc(need(col, "title", "sides.columns"))}{mark}</h2>{sub}<ul>{items}</ul></div>')
    if layer:
        stack = need(layer, "stack", "layer")
        out.append(f'<aside class="layer"><div class="label">{esc(need(layer, "label", "layer"))}</div>{plates(stack, dark)}'
                   f'<p>{esc(need(layer, "text", "layer"))}</p></aside>')
    out.append("</div>")
    return "".join(out)


def flags(c):
    f = c.get("flags")
    if not f:
        return ""
    rows = "".join(f'<div class="flag"><div class="if">{esc(r[0])}</div><div class="then">{esc(r[1])}</div></div>'
                   for r in need(f, "rows", "flags"))
    return f'<section class="flags"><div class="label">{esc(need(f, "label", "flags"))}</div>{rows}</section>'


def closing(c):
    blocks = c.get("closing") or []
    if not blocks:
        return ""
    if len(blocks) > 3:
        raise SystemExit("content error: closing takes at most three blocks")
    cells = []
    for blk in blocks:
        body = (f'<p>{esc(blk["text"])}</p>' if blk.get("text")
                else "<ul>" + "".join(f"<li>{esc(t)}</li>" for t in need(blk, "items", "closing")) + "</ul>")
        cells.append(f'<div><div class="label">{esc(need(blk, "label", "closing"))}</div>{body}</div>')
    grid = {1: "g3 one", 2: "g3", 3: "g3"}[len(blocks)]
    return f'<div class="{grid} closing">{"".join(cells)}</div>'


def footer(c, foot):
    n = need(c, "next", "content")
    contact = n.get("contact")
    tag = ""
    if contact:
        email = contact.get("email", "")
        role = esc(contact.get("role", ""))
        mail = f'<span><a href="mailto:{_escape(email)}">{_escape(email)}</a></span>' if email else ""
        tag = (f'<div class="tag"><div class="name">{b.symbol(b.WHITE, 9)}<span>{esc(need(contact, "name", "next.contact"))}</span></div>'
               f'<div class="who" data-fit="next.contact"><span>{role}</span>{mail}</div></div>')
    return (f'<footer class="next"><div class="texture"></div><div class="grain"></div>'
            f'<div class="g3"><div class="say{"" if contact else " full"}"><div class="label">{esc(need(n, "label", "next"))}</div>'
            f'<p>{esc(need(n, "text", "next"))}</p></div>{tag}</div></footer>')


def build_html(c, mode, density, extra_gap=0.0):
    d = dict(DENSITY[density])
    d["gap"] = round(d["gap"] + extra_gap, 1)
    css = CSS
    for key, value in TOKENS.items():
        css = css.replace(key, value)
    style = (f'--gap:{d["gap"]}pt;--row:{d["row"]}pt;--flag:{d["flag"]}pt;--withfig:{d["withfig"]}pt;'
             f'--withdesc:{d["withdesc"]}pt;--withpad:{d["withpad"]}pt;--closing:{d["closing"]}pt;--foot:{d["foot"]}pt')
    dark = mode == "dark"
    title = _escape(c.get("title") or ("Bluefyn for " + c["partner"] if c.get("partner") else "Bluefyn"))
    body = (f'<div class="page{" dark" if dark else ""}" style="{style}">{poster(c)}'
            f'<main class="content">{with_block(c)}{sides(c, dark)}{flags(c)}{closing(c)}</main>{footer(c, d["foot"])}</div>')
    return (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><title>{title}</title>'
            f'<style>{b.geist_face()}{css}</style></head>\n<body>{body}{MEASURE}</body></html>\n')


# ------------------------------------------------------------------ browser
def find_chrome():
    env = os.environ.get("CHROME")
    if env:
        return env
    mac = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Chromium.app/Contents/MacOS/Chromium",
           "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge", "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"]
    for path in mac:
        if os.path.exists(path):
            return path
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "brave-browser"):
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit("No Chrome, Chromium, Edge or Brave found. Install one, or set CHROME=/path/to/browser.")


def chrome(args, capture=False):
    profile = tempfile.mkdtemp(prefix="bluefyn-one-pager-")
    cmd = [find_chrome(), "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
           f"--user-data-dir={profile}", "--virtual-time-budget=5000"] + args
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=120)
        return res.stdout.decode("utf-8", "replace") if capture else ""
    finally:
        shutil.rmtree(profile, ignore_errors=True)


def measure(html_path):
    dom = chrome(["--dump-dom", "file://" + html_path], capture=True)
    head = dom[:6000]
    get = lambda key: (re.search(rf'data-{key}="([^"]*)"', head) or [None, None])[1]
    if get("spare") is None:
        raise SystemExit("Could not measure the page in the browser. Is the browser able to run headless?")
    return {"spare": float(get("spare")), "wide": [w for w in (get("wide") or "").split("|") if w],
            "gaps": int(get("gaps") or 0), "h1": int(get("h1") or 0), "titles": get("titles") or "",
            "coldiff": float(get("coldiff") or 0), "figs": int(get("figs") or 0)}


def page_count(pdf_path):
    with open(pdf_path, "rb") as fh:
        data = fh.read()
    counts = [int(n) for n in re.findall(rb"/Type\s*/Pages\b[^>]*?/Count\s+(\d+)", data)]
    counts += [int(n) for n in re.findall(rb"/Count\s+(\d+)[^>]*?/Type\s*/Pages\b", data)]
    return max(counts) if counts else len(re.findall(rb"/Type\s*/Page\b(?!s)", data))


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "bluefyn"


def build(content, mode, density, out_dir, slug, reuse=None):
    """Build one mode. `reuse` is the (preset, stretch) another mode settled on, so light and dark match."""
    base = os.path.join(out_dir, f"{slug}-{mode}")
    html_path = base + ".html"

    def attempt(name, extra_gap=0.0):
        with open(html_path, "w") as fh:
            fh.write(build_html(content, mode, name, extra_gap))
        return measure(html_path)

    chosen = m = None
    extra = 0.0
    if reuse:
        chosen, extra = reuse
        m = attempt(chosen, extra)
        if m["spare"] < MIN_SPARE[chosen]:
            reuse = None                     # this mode needs its own spacing after all
    if not reuse:
        order = ["roomy", "regular", "tight"] if density == "auto" else [density]
        for name in order:
            chosen, m = name, attempt(name)
            if m["spare"] >= MIN_SPARE[name]:
                break
        # Spare room goes between the sections, so a short page does not end in a blank band.
        extra = 0.0
        if m["gaps"] and m["spare"] > MIN_SPARE[chosen] + 12:
            extra = round(min(MAX_STRETCH, (m["spare"] - MIN_SPARE[chosen] - 4) / m["gaps"]), 1)
            stretched = attempt(chosen, extra)
            if stretched["spare"] >= MIN_SPARE[chosen]:
                m = stretched
            else:
                extra, m = 0.0, attempt(chosen)
    need_spare = MIN_SPARE[chosen]

    chrome(["--no-pdf-header-footer", f"--print-to-pdf={base}.pdf", "file://" + html_path])
    chrome(["--hide-scrollbars", "--window-size=816,1056", "--force-device-scale-factor=2", f"--screenshot={base}.png",
            "file://" + html_path])
    pages = page_count(base + ".pdf") if os.path.exists(base + ".pdf") else 0

    problems = []
    if m["spare"] < need_spare:
        problems.append(f"too tall: the content is {round(need_spare - m['spare'], 1)}pt over even at '{chosen}'. "
                        f"Ask the author what to shorten or drop; do not cut copy on your own.")
    if pages != 1:
        problems.append(f"the PDF has {pages} pages, expected 1.")
    for item in m["wide"]:
        problems.append(f"too wide: {item} does not fit on its line. Shorten it.")
    if m["h1"] > 3:
        problems.append(f"headline runs {m['h1']} lines. Aim for two or three (about 75 characters or fewer at the standard size).")
    for i, wrapped in enumerate(m["titles"]):
        if wrapped == "1":
            problems.append(f"sides.columns[{i}].title wraps onto a second line. Shorten the title or drop its mark.")
    if m["figs"]:
        problems.append(f"{m['figs']} figure(s) wrap onto a second line. A figure is a number or two or three short words.")
    notes = []
    if m["h1"] == 1:
        notes.append("headline is one line, which looks thin. Two or three lines is the target.")
    if m["coldiff"] > 16:
        notes.append(f"the two 'sides' columns differ by {m['coldiff']}pt in height. Even them out if the author agrees.")
    if m["spare"] > 60:
        notes.append(f"{m['spare']}pt is still empty above the footer. The page has little content; suggest the missing sections.")

    stretch = f" stretch=+{extra}pt" if extra else ""
    print(f"[{mode}] density={chosen}{stretch} spare={m['spare']}pt (needs {need_spare}pt) pages={pages} "
          f"headline={m['h1']} lines fits={'yes' if not problems else 'NO'}")
    for line in problems:
        print(f"[{mode}] problem: {line}")
    for line in notes:
        print(f"[{mode}] note: {line}")
    print(f"[{mode}] wrote {base}.pdf, {base}.png, {base}.html")
    return not problems, (chosen, extra)


KIT_README = """# One pager kit

A local copy of the Bluefyn one pager template. Change it freely; the installed skill is not affected.

    python3 one_pager.py content.json --out out --mode both

- `content.json`: the words. See the bluefyn-one-pager skill's `references/content-schema.md`.
- `one_pager.py`: the layout. The `CSS` block near the top holds every size, color and gap. `DENSITY`
  holds the three spacing presets. The functions under "markup" build each section.
- `brand.py` and `assets/`: brand colors, logo, font, textures and drawings.

After a change, rebuild and open the PNG in `out/`. If you want the change for everyone, bring it to
whoever owns the brand and update the skill.
"""


def init_kit(target):
    """Copy the template, the brand primitives and the assets into a folder the user can tune."""
    target = os.path.abspath(target)
    if os.path.exists(target) and os.listdir(target):
        raise SystemExit(f"{target} already has files in it. Pick an empty or new folder.")
    os.makedirs(target, exist_ok=True)
    shutil.copy2(os.path.abspath(__file__), os.path.join(target, "one_pager.py"))
    shutil.copy2(os.path.join(BRAND_DIR, "brand.py"), os.path.join(target, "brand.py"))
    shutil.copytree(b.ASSETS, os.path.join(target, "assets"))
    example = os.path.join(os.path.dirname(HERE), "examples", "acme.json")
    if os.path.isfile(example):
        shutil.copy2(example, os.path.join(target, "content.json"))
    with open(os.path.join(target, "README.md"), "w") as fh:
        fh.write(KIT_README)
    print(f"wrote a one pager kit to {target}")
    print(f"build it with: python3 {os.path.join(target, 'one_pager.py')} {os.path.join(target, 'content.json')} "
          f"--out {os.path.join(target, 'out')} --mode both")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        if len(sys.argv) != 3:
            raise SystemExit("usage: one_pager.py init <folder>")
        return init_kit(sys.argv[2])

    ap = argparse.ArgumentParser(description="Build a Bluefyn one pager from a content JSON file.")
    ap.add_argument("content", help="path to the content JSON (see references/content-schema.md)")
    ap.add_argument("--out", default=".", help="output folder (default: current folder)")
    ap.add_argument("--mode", choices=["light", "dark", "both"], help="overrides the mode in the content file")
    ap.add_argument("--density", choices=["auto", "roomy", "regular", "tight"], default="auto")
    ap.add_argument("--name", help="output file name stem (default: one-pager-<partner>)")
    args = ap.parse_args()

    with open(args.content) as fh:
        content = json.load(fh)
    os.makedirs(args.out, exist_ok=True)
    out_dir = os.path.abspath(args.out)
    mode = args.mode or content.get("mode", "light")
    slug = args.name or "one-pager-" + slugify(content.get("partner") or content.get("title") or "bluefyn")

    warnings = copy_warnings(content)
    for w in warnings:
        print("copy warning:", w)
    ok, settled = True, None
    for m in (["light", "dark"] if mode == "both" else [mode]):
        fits, settled = build(content, m, args.density, out_dir, slug, reuse=settled)
        ok = ok and fits
    if warnings:
        print(f"{len(warnings)} copy warning(s) above. Fix the wording with the author before you send this.")
    sys.exit(0 if ok and not warnings else 2)


if __name__ == "__main__":
    main()

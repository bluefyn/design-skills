#!/usr/bin/env python3
"""Three new Bluefyn designs from one content file, each in light and dark.

    python3 dream.py new DIR [--content content.json]     start a dream folder
    python3 dream.py build DIR [a b c] [--mode both]       render, check and compare the concepts
    python3 dream.py primitives                            list every brand primitive you can use

A dream folder holds the content file, a plan (`dream.md`) and three concept files in `concepts/`.
Each concept is a Python file that turns the content into one US Letter page:

    CONCEPT = {"name": "Spine", "idea": "One sentence.", "hero": "stream"}

    def render(c, mode, k):
        return css, body_html

`c` is the content (the bluefyn-one-pager schema), `mode` is "light" or "dark", and `k` is the kit
(see `Kit` below): the brand module as `k.b`, escaping, grain, texture, brand files and rasterizing.

`build` writes, for each concept and mode, a PDF, a PNG preview and the HTML into DIR/out, then a
contact sheet of all of them (DIR/out/sheet.png), and reports what does not fit, what content is
missing from the page, which primitives each concept used and whether the concepts are different
enough from each other and from the shipped examples.

Python standard library and a Chromium-based browser. It reuses the browser and PDF helpers of the
bluefyn-one-pager skill and the brand code of the bluefyn-design skill, so install the pack together.
"""
import argparse
import difflib
import glob
import hashlib
import html as _html
import importlib.util
import inspect
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.dont_write_bytecode = True          # keep __pycache__ out of the installed skills


def find_one_pager():
    """The folder that holds one_pager.py: $BLUEFYN_ONE_PAGER_DIR, the sibling skill, or ~/.claude/skills."""
    skills = os.path.dirname(SKILL)
    env = os.environ.get("BLUEFYN_ONE_PAGER_DIR")
    candidates = ([os.path.join(env, "scripts"), env] if env else []) + [
        os.path.join(skills, "bluefyn-one-pager", "scripts"),
        os.path.join(os.path.expanduser("~"), ".claude", "skills", "bluefyn-one-pager", "scripts")]
    for folder in candidates:
        if os.path.isfile(os.path.join(folder, "one_pager.py")):
            return folder
    raise SystemExit("Cannot find the bluefyn-one-pager skill. Install the whole pack (install.sh installs all "
                     "the skills together), or set BLUEFYN_ONE_PAGER_DIR to its folder.")


sys.path.insert(0, find_one_pager())
import one_pager as op  # noqa: E402  (this also loads brand.py from bluefyn-design)

b = op.b
PAGE_W, PAGE_H = 612, 792

# ------------------------------------------------------------- primitives
# Everything the brand has to draw with, by family. `build` reports which ones each concept used.
CATALOGUE = {
    "logo": ["logo", "symbol", "wordmark"],
    "drawings": ["field", "tower", "plates", "slab", "scan_band", "slanted_field", "discs", "ellipses"],
    "textures": ["record_texture", "stream", "texture", "grain"],
    "records": [n for n in dir(b) if n.startswith("REC_")],
    "brand files": ["logo files", "avatars", "banners", "patterns"],
}
DRAWN = CATALOGUE["logo"] + CATALOGUE["drawings"] + CATALOGUE["textures"]
_used = set()
_depth = [0]          # count only the calls a concept makes, not the ones a brand function makes inside itself


def _track(name, fn):
    def wrapped(*args, **kwargs):
        if _depth[0] == 0:
            if name == "brand_uri" or name == "brand_file":
                _used.add("file:" + (args[0] if args else kwargs.get("rel", "")))
            else:
                _used.add(name)
        _depth[0] += 1
        try:
            return fn(*args, **kwargs)
        finally:
            _depth[0] -= 1
    wrapped.__wrapped__ = fn
    wrapped.__doc__ = fn.__doc__
    return wrapped


for _name in DRAWN + ["brand_uri", "brand_file"]:
    setattr(b, _name, _track(_name, getattr(b, _name)))


def family_of(item):
    """The catalogue entry a used item counts for: a function name, a record, or a brand file folder."""
    if item.startswith("file:"):
        top = item[5:].split("/")[0]
        return {"logo": "logo files"}.get(top, top)
    return item


# ------------------------------------------------------------------- kit
class Kit:
    """What a concept's render() gets as `k`.

    k.b                      the brand module: tokens (k.b.INK, k.b.NAVY ...), logo, drawings, records
    k.mode, k.dark           "light" or "dark", and True in dark mode
    k.esc(text)              escape copy for HTML, keeping hyphenated words on one line
    k.numeric(text)          True when a figure starts with a number (set it with class "num")
    k.grain(kind=None)       CSS background for the fine grain; kind "light" or "dark", default by mode
    k.texture()              CSS background-image for the record texture, an image made for navy grounds
    k.file(rel)              a ready-made brand file as a data URI ("patterns/bluefyn-pattern-tower-night.svg")
    k.image(src, w, h, ...)  an <img> of a drawing or a brand file, rasterized, so digits and record words
                             stay out of the PDF's text. Use it for every texture-like graphic.
    k.mark(word, kind)       a verdict mark: kind "match", "off" or "checking"; the word is required
    k.lockup(c, fill, size)  the logo with " × partner" beside it, as the one pager sets it
    """

    def __init__(self, mode, cache):
        self.b = b
        self.mode = mode
        self.dark = mode == "dark"
        self._cache = cache

    esc = staticmethod(op.esc)
    numeric = staticmethod(op.looks_numeric)

    def grain(self, kind=None):
        kind = kind or ("dark" if self.dark else "light")
        return f'url("{b.grain(kind)}") 0 0 / 108pt 108pt'

    def texture(self):
        return f'url("{b.texture()}")'

    def file(self, rel):
        return b.brand_uri(rel)

    def mark(self, word, kind="checking"):
        if not word:
            raise ValueError("a verdict mark always carries its word")
        return f'<span class="mark {kind}">{op.esc(word)}</span>'

    def lockup(self, c, fill=None, size=13, cls="lockup"):
        fill = fill or (b.WHITE if self.dark else b.INK)
        partner = (f'<span class="x">×</span><span class="partner">{op.esc(c["partner"])}</span>'
                   if c.get("partner") else "")
        return f'<div class="{cls}">{b.logo(fill, size)}{partner}</div>'

    def image(self, src, w, h, fit="cover", position="center", scale=3, cls="", style="", clear=None):
        """An <img> w x h points. `src` is SVG markup from a brand.py drawing or a brand file path.
        The picture is rendered once in the browser at `scale` and cached, so rebuilds are quick.

        clear: where the drawing is, so the build reports copy that runs over it. True means the whole
        picture; a tuple (left, top, right, bottom) in fractions of the picture marks part of it, such
        as (0.3, 0, 0.7, 1) for a tower in the middle of a pattern. Leave it out for a texture that
        copy is meant to sit on."""
        if src.lstrip().startswith("<svg"):
            inner = src
        else:
            inner = f'<img src="{self.file(src)}" style="width:100%;height:100%;object-fit:{fit};object-position:{position}">'
        key = hashlib.sha1(f"{inner}|{w}|{h}|{scale}".encode()).hexdigest()[:16]
        png = os.path.join(self._cache, key + ".png")
        if not os.path.exists(png):
            os.makedirs(self._cache, exist_ok=True)
            page = os.path.join(self._cache, key + ".html")
            with open(page, "w") as fh:
                fh.write('<!doctype html><html><head><meta charset="utf-8"><style>' + b.geist_face() +
                         f'*{{margin:0;padding:0}}html,body{{background:transparent}}div{{width:{w}pt;height:{h}pt;overflow:hidden}}'
                         f'div>svg{{width:100%;height:100%;display:block}}</style></head><body><div>{inner}</div></body></html>')
            op.chrome(["--hide-scrollbars", "--default-background-color=00000000",
                       f"--window-size={int(w * 4 / 3 + .999)},{int(h * 4 / 3 + .999)}",
                       f"--force-device-scale-factor={scale}", f"--screenshot={png}", "file://" + page])
            os.remove(page)
            if not os.path.exists(png):
                raise SystemExit("The browser did not render a picture for k.image(). Is it able to run headless?")
        uri = _png_uri(png)
        box = (0, 0, 1, 1) if clear is True else clear
        mark = f' data-clear="{",".join(str(v) for v in box)}"' if box else ""
        return (f'<img class="{cls}" src="{uri}" alt="" aria-hidden="true"{mark} '
                f'style="display:block;width:{w}pt;height:{h}pt;{style}">')


def _png_uri(path):
    import base64
    with open(path, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode("ascii")


# ------------------------------------------------------------------ page
BASE_CSS = """
@page{size:612pt 792pt;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:612pt;height:792pt}
body{font-family:"Geist",Arial,sans-serif;font-weight:400;font-size:9.1pt;line-height:1.42;
  -webkit-print-color-adjust:exact;print-color-adjust:exact;font-synthesis:none;text-rendering:geometricPrecision}
.page{position:relative;width:612pt;height:792pt;overflow:hidden}
h1,h2,h3{font-weight:400}
ul{list-style:none}
p,li{text-wrap:pretty}
a{color:inherit;text-decoration:none}
svg,img{display:block}
.nb{white-space:nowrap}
.num{font-variant-numeric:tabular-nums}
.lockup{display:flex;align-items:center;gap:9pt}
.lockup .x{font-size:10pt;line-height:1;opacity:.8}
.lockup .partner{font-size:12.4pt;line-height:1;letter-spacing:-.02em}
.mark{font-family:Arial,Helvetica,sans-serif;font-size:6.1pt;line-height:1;text-transform:uppercase;color:#fff;
  padding:1.9pt 3.2pt 1.5pt;white-space:nowrap;letter-spacing:0;background:$BLUE}
.mark.match{background:$GREEN}
.mark.off{background:$RED}
"""

# Runs in the browser before printing and leaves a JSON report in the DOM. It is not part of the PDF.
MEASURE = r"""<script>
addEventListener('load',()=>{document.fonts.ready.then(()=>{
  const pt=v=>Math.round(v*75)/100, page=document.querySelector('.page'), pr=page.getBoundingClientRect(), out={};
  out.geist=document.fonts.check('12px "Geist"');
  out.ground=getComputedStyle(page).backgroundColor;
  out.boxes=[...document.querySelectorAll('[data-box]')].filter(e=>e.scrollHeight>e.clientHeight+1||e.scrollWidth>e.clientWidth+1)
    .map(e=>e.dataset.box+' by '+pt(Math.max(e.scrollHeight-e.clientHeight,e.scrollWidth-e.clientWidth))+'pt');
  const walk=document.createTreeWalker(page,NodeFilter.SHOW_TEXT), runs=[]; let n, min=99, minText='';
  const off=[];
  while((n=walk.nextNode())){
    const t=n.textContent.trim(); if(!t) continue;
    const el=n.parentElement; if(el.closest('svg')||el.closest('[aria-hidden="true"]')) continue;
    const isMark=!!el.closest('.mark');
    const cs=getComputedStyle(el); if(cs.visibility==='hidden'||cs.display==='none'||+cs.opacity===0) continue;
    const fs=parseFloat(cs.fontSize)*.75; if(!isMark&&fs<min){min=fs;minText=t.slice(0,48);}
    const range=document.createRange(); range.selectNodeContents(n);
    for(const r of range.getClientRects()){
      if(!r.width||!r.height) continue;
      if(r.right>pr.right+.5||r.bottom>pr.bottom+.5||r.left<pr.left-.5||r.top<pr.top-.5){off.push(t.slice(0,48));break;}
      const k=r.height*.22; runs.push({r:{left:r.left,right:r.right,top:r.top+k,bottom:r.bottom-k}, t:t.slice(0,48), el});
    }
  }
  const hits=[];
  for(let i=0;i<runs.length&&hits.length<6;i++) for(let j=i+1;j<runs.length&&hits.length<6;j++){
    const a=runs[i], c=runs[j]; if(a.el===c.el||a.el.contains(c.el)||c.el.contains(a.el)) continue;
    const w=Math.min(a.r.right,c.r.right)-Math.max(a.r.left,c.r.left), h=Math.min(a.r.bottom,c.r.bottom)-Math.max(a.r.top,c.r.top);
    if(w>1.5&&h>1.5) hits.push(a.t+'  /  '+c.t);
  }
  const clear=[...page.querySelectorAll('[data-clear]')].map(e=>{const r=e.getBoundingClientRect(), f=e.dataset.clear.split(',').map(Number);
    return {l:r.left+r.width*f[0], t:r.top+r.height*f[1], r:r.left+r.width*f[2], b:r.top+r.height*f[3]};});
  out.over=[...new Set(runs.filter(x=>clear.some(c=>Math.min(x.r.right,c.r)-Math.max(x.r.left,c.l)>1.5&&Math.min(x.r.bottom,c.b)-Math.max(x.r.top,c.t)>1.5)).map(x=>x.t))].slice(0,6);
  out.minFont=Math.round(min*10)/10; out.minText=minText; out.off=off; out.overlaps=hits;
  out.text=page.innerText+' '+[...page.querySelectorAll('svg text')].map(e=>e.textContent).join(' ');
  out.w=pt(pr.width); out.h=pt(pr.height);
  const s=document.createElement('script'); s.type='application/json'; s.id='dream-report';
  s.textContent=JSON.stringify(out).replace(/</g,'\\u003c'); document.body.appendChild(s);
})});
</script>"""

TOKENS = {"$INK": b.INK, "$PAPER": b.PAPER, "$NIGHT": b.NIGHT, "$BLUE": b.BLUE, "$NAVY": b.NAVY,
          "$GREEN": b.GREEN, "$RED": b.RED}


def page_html(concept, c, mode, css, body):
    base = BASE_CSS
    for key, value in TOKENS.items():
        base = base.replace(key, value)
    title = _html.escape(f'{concept["name"]} for {c["partner"]}' if c.get("partner") else concept["name"])
    return (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><title>{title}</title>'
            f'<style>{b.geist_face()}{base}{css}</style></head>\n'
            f'<body><div class="page {mode}">{body}</div>{MEASURE}</body></html>\n')


def luminance(css_color):
    nums = [float(x) for x in re.findall(r"[\d.]+", css_color or "")]
    if len(nums) < 3 or (len(nums) == 4 and nums[3] == 0):
        return None
    lin = [((v / 255) / 12.92 if v / 255 <= 0.04045 else ((v / 255 + 0.055) / 1.055) ** 2.4) for v in nums[:3]]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def norm(text):
    return re.sub(r"\s+", " ", text.replace(" ", " ")).strip().lower()


# ---------------------------------------------------------------- concepts
class Unfinished(Exception):
    """A concept file that is still the template."""


def load_concept(path):
    name = "dream_concept_" + hashlib.sha1(path.encode()).hexdigest()[:8]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    meta = getattr(mod, "CONCEPT", None)
    if not isinstance(meta, dict) or not all(meta.get(k) for k in ("name", "idea", "hero")):
        raise SystemExit(f"{path}: CONCEPT needs a name, an idea and a hero.")
    if "TODO" in (meta["name"], meta["idea"], meta["hero"]):
        raise Unfinished(f"{os.path.basename(path)} is still the template")
    if not callable(getattr(mod, "render", None)):
        raise SystemExit(f"{path}: define render(c, mode, k) returning (css, body_html).")
    return mod


def example_sources(folder):
    """The shipped example concepts, except the ones in `folder` itself (when you rebuild an example)."""
    out = {}
    for path in sorted(glob.glob(os.path.join(SKILL, "examples", "*", "concepts", "*.py"))):
        if os.path.realpath(os.path.dirname(os.path.dirname(path))) == os.path.realpath(folder):
            continue
        rel = os.path.relpath(path, SKILL)
        with open(path) as fh:
            out[rel] = fh.read()
    return out


def similarity(a, b_):
    strip = lambda s: [ln.strip() for ln in s.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    return difflib.SequenceMatcher(None, strip(a), strip(b_), autojunk=False).ratio()


# -------------------------------------------------------------------- build
def build_one(folder, key, mod, c, mode, out_dir, slug):
    concept = mod.CONCEPT
    kit = Kit(mode, os.path.join(folder, ".cache"))
    _used.clear()
    result = mod.render(c, mode, kit)
    if not (isinstance(result, tuple) and len(result) == 2):
        raise SystemExit(f"concepts/{key}.py: render() must return (css, body_html).")
    css, body = result
    used = set(_used)
    base = os.path.join(out_dir, f"{slug}-{key}-{op.slugify(concept['name'])}-{mode}")
    html_path = base + ".html"
    with open(html_path, "w") as fh:
        fh.write(page_html(concept, c, mode, css, body))

    dom = op.chrome(["--dump-dom", "file://" + html_path], capture=True)
    found = re.search(r'<script type="application/json" id="dream-report">(.*?)</script>', dom, re.S)
    if not found:
        raise SystemExit("Could not measure the page in the browser. Is the browser able to run headless?")
    m = json.loads(_html.unescape(found.group(1)))

    op.chrome(["--no-pdf-header-footer", f"--print-to-pdf={base}.pdf", "file://" + html_path])
    op.chrome(["--hide-scrollbars", "--window-size=816,1056", "--force-device-scale-factor=2",
               f"--screenshot={base}.png", "file://" + html_path])
    pdf = open(base + ".pdf", "rb").read() if os.path.exists(base + ".pdf") else b""
    pages = op.page_count(base + ".pdf") if pdf else 0

    problems, notes = [], []
    if not pdf or b"Geist" not in pdf or not m["geist"]:
        problems.append("Geist is not in the PDF. Load the font through the page (dream.py embeds it) and "
                        "do not set another font-family on copy.")
    if pages != 1:
        problems.append(f"the PDF has {pages} pages, expected 1. Something is taller than the page.")
    if abs(m["w"] - PAGE_W) > 1 or abs(m["h"] - PAGE_H) > 1:
        problems.append(f".page is {m['w']} x {m['h']}pt; keep it 612 x 792pt.")
    lum = luminance(m["ground"])
    if lum is None:
        problems.append("the .page element has no background color. Give each mode a ground (paper, night, ink).")
    elif mode == "light" and lum < 0.5:
        problems.append(f"light mode reads dark (ground {m['ground']}). Light mode is on paper or white.")
    elif mode == "dark" and lum > 0.2:
        problems.append(f"dark mode reads light (ground {m['ground']}). Dark mode is on night, ink or navy.")
    for item in m["boxes"]:
        problems.append(f"overflow: the box '{item}' is too small for its content.")
    for item in m["off"][:6]:
        problems.append(f"off the page: '{item}' runs past the edge.")
    for item in m["overlaps"]:
        problems.append(f"text on text: {item}")
    for item in m.get("over", []):
        problems.append(f"text on the graphic: '{item}' runs over a picture marked clear.")
    if m["minFont"] < 7:
        problems.append(f"copy at {m['minFont']}pt ('{m['minText']}'). Nothing a person reads goes under 7pt.")
    text = norm(m["text"])
    for path, value in op.strings(c):
        if path in ("mode", "title") or not value.strip():
            continue
        if norm(value) not in text:
            problems.append(f"content missing from the page: {path} ({value[:50]!r})")
    for ch, label in op.BANNED.items():
        if ch in m["text"]:
            problems.append(f"the page text contains {label}. Rewrite that copy.")
    hero = concept["hero"]
    if hero not in {family_of(u) for u in used} | {u[5:] for u in used if u.startswith("file:")} | used:
        problems.append(f"the declared hero '{hero}' was not used on the {mode} page.")
    if m["minFont"] < 8.5:
        notes.append(f"smallest copy is {m['minFont']}pt ('{m['minText']}'). Body copy reads best at 9pt or more.")

    print(f"[{key} {mode}] {concept['name']}: pages={pages} smallest={m['minFont']}pt "
          f"fits={'yes' if not problems else 'NO'}")
    for line in problems:
        print(f"[{key} {mode}] problem: {line}")
    for line in notes:
        print(f"[{key} {mode}] note: {line}")
    return {"ok": not problems, "used": used, "png": base + ".png", "pdf": base + ".pdf"}


SHEET_CSS = """*{margin:0;padding:0;box-sizing:border-box}
body{background:#E6E6E6;font-family:"Geist",Arial,sans-serif;color:#1C1919;padding:28px;width:1360px}
h1{font-size:20px;font-weight:400;letter-spacing:-.02em;margin-bottom:4px}
.sub{font-size:12px;color:#696969;margin-bottom:20px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px 24px}
.head{font-size:14px;line-height:1.3}
.head span{color:#696969}
.idea{font-size:11px;line-height:1.35;color:#3A3A3A;min-height:30px;margin:2px 0 8px}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:8px}
img{width:100%;display:block;box-shadow:0 0 0 .5px rgba(0,0,0,.25)}
.mode{font-size:10px;color:#696969;margin-top:4px}"""


def contact_sheet(out_dir, c, rows):
    cells = []
    for key, concept, pngs in rows:
        pair = "".join(f'<div><img src="{os.path.basename(p)}"><div class="mode">{mode}</div></div>'
                       for mode, p in pngs if os.path.exists(p))
        cells.append(f'<div><div class="head">{_html.escape(key)}. {_html.escape(concept["name"])} '
                     f'<span>hero: {_html.escape(concept["hero"])}</span></div>'
                     f'<div class="idea">{_html.escape(concept["idea"])}</div><div class="pair">{pair}</div></div>')
    title = _html.escape(c.get("partner") or "Bluefyn")
    page = (f'<!doctype html><html><head><meta charset="utf-8"><title>Dream sheet</title><style>{b.geist_face()}{SHEET_CSS}'
            f'</style></head><body><h1>Three designs for {title}</h1><div class="sub">Each concept in light and dark. '
            f'Open the PDFs in this folder for print.</div><div class="grid">{"".join(cells)}</div></body></html>')
    path = os.path.join(out_dir, "sheet.html")
    with open(path, "w") as fh:
        fh.write(page)
    op.chrome(["--hide-scrollbars", "--window-size=1360,480", "--force-device-scale-factor=1.5",
               f"--screenshot={os.path.join(out_dir, 'sheet.png')}", "file://" + path])
    return os.path.join(out_dir, "sheet.png")


def build(folder, keys, mode):
    folder = os.path.abspath(folder)
    content_path = os.path.join(folder, "content.json")
    if not os.path.isfile(content_path):
        raise SystemExit(f"{content_path} is missing. Start with: dream.py new {folder} --content <file>")
    with open(content_path) as fh:
        c = json.load(fh)
    op.need(c, "headline", "content")
    op.need(c, "next", "content")
    for line in op.copy_warnings(c):
        print(f"[content] note: {line}")
    paths = sorted(glob.glob(os.path.join(folder, "concepts", "*.py")))
    all_keys = [os.path.splitext(os.path.basename(p))[0] for p in paths if not os.path.basename(p).startswith("_")]
    keys = keys or all_keys
    missing = [k for k in keys if k not in all_keys]
    if missing:
        raise SystemExit(f"no concept named {', '.join(missing)} in {folder}/concepts")
    mods, waiting = {}, []
    for k in all_keys:
        try:
            mods[k] = load_concept(os.path.join(folder, "concepts", k + ".py"))
        except Unfinished:
            waiting.append(k)
    asked = [k for k in keys if k in waiting]
    if asked:
        raise SystemExit(f"concepts/{asked[0]}.py is still the template. Design it first (see dream.md).")
    keys = [k for k in keys if k in mods]
    done = [k for k in all_keys if k in mods]
    out_dir = os.path.join(folder, "out")
    os.makedirs(out_dir, exist_ok=True)
    slug = op.slugify(c.get("partner") or "bluefyn")
    modes = ["light", "dark"] if mode == "both" else [mode]

    results = {}
    for k in keys:
        results[k] = [build_one(folder, k, mods[k], c, md, out_dir, slug) for md in modes]

    # The sheet shows every concept that has been built, not only the ones built this time.
    rows = []
    for k in done:
        concept = mods[k].CONCEPT
        base = os.path.join(out_dir, f"{slug}-{k}-{op.slugify(concept['name'])}")
        rows.append((k, concept, [(md, f"{base}-{md}.png") for md in ("light", "dark")]))
    sheet = contact_sheet(out_dir, c, rows)

    # ------------------------------------------------------------ comparison
    print()
    problems = []
    if len(all_keys) != 3:
        problems.append(f"a dream has three concepts; this folder has {len(all_keys)}.")
    for k in waiting:
        problems.append(f"concepts/{k}.py is not designed yet.")
    heroes = {}
    for k in done:
        heroes.setdefault(mods[k].CONCEPT["hero"], []).append(k)
    for hero, ks in heroes.items():
        if len(ks) > 1:
            problems.append(f"concepts {', '.join(ks)} share the hero '{hero}'. Give each concept its own.")
    sources = {k: open(os.path.join(folder, "concepts", k + ".py")).read() for k in done}
    for i, a in enumerate(done):
        for other in done[i + 1:]:
            r = similarity(sources[a], sources[other])
            if r > 0.5:
                problems.append(f"concepts {a} and {other} are {round(r * 100)}% the same code. Rework one from scratch.")
        for rel, src in example_sources(folder).items():
            r = similarity(sources[a], src)
            if r > 0.45:
                problems.append(f"concept {a} is {round(r * 100)}% the same as the shipped example {rel}. "
                                f"The examples are taken: design something new.")
    used_all = set()
    for k in keys:
        used = set().union(*(r["used"] for r in results[k]))
        recs = sorted(set(re.findall(r"\bREC_[A-Z_]+\b", sources[k])))
        used_all |= {family_of(u) for u in used} | set(recs)
        files = sorted(u[5:] for u in used if u.startswith("file:"))
        names = sorted(u for u in used if not u.startswith("file:"))
        print(f"[{k}] {mods[k].CONCEPT['name']} / hero {mods[k].CONCEPT['hero']} / uses: "
              f"{', '.join(names + recs + files) or 'nothing from the brand'}")
    if set(keys) == set(all_keys) and not waiting:
        unused = {fam: [x for x in items if x not in used_all] for fam, items in CATALOGUE.items()}
        unused = {fam: xs for fam, xs in unused.items() if xs}
        if unused:
            print("not used in this dream: " + "; ".join(f"{fam}: {', '.join(xs)}" for fam, xs in unused.items()))
    for line in problems:
        print(f"[dream] problem: {line}")
    ok = all(r["ok"] for rs in results.values() for r in rs) and not problems
    print(f"[dream] sheet: {sheet}")
    print(f"[dream] {'ready to show' if ok else 'not ready: fix the problems above'}")
    return ok


# ---------------------------------------------------------------- commands
PLAN = """# Dream: {partner}

Three concepts for the same content. Fill this in before you write any concept code, then review it:
would a person who sees the three side by side say they are three different ideas?

## The page has to make one reader do one thing

Reader:
The one thing:

## Concept a

- Name:
- The idea, in one sentence:
- Hero (one drawing, texture or file from `dream.py primitives`):
- Structure (what leads, the grid, where each section goes):
- Ground and contrast (light, then dark):
- Type (headline size and treatment):
- What it is remembered for:

## Concept b

(same list)

## Concept c

(same list)

## Why these are three different designs

Different hero, different structure, different first impression. Say how each differs from the other two
and from the template of bluefyn-one-pager.
"""

TEMPLATE = '''"""Concept {key}. Replace this file with your design. See SKILL.md and the examples."""

CONCEPT = {{
    "name": "TODO",       # two or three words
    "idea": "TODO",       # the one sentence a person would use to describe it
    "hero": "TODO",       # one drawing, texture or file from `dream.py primitives`, such as "tower" or "patterns"
}}


def render(c, mode, k):
    """Return (css, body_html) for one US Letter page. dream.py wraps body_html in <div class="page {{mode}}">."""
    raise NotImplementedError
'''


def cmd_new(folder, content):
    folder = os.path.abspath(folder)
    if os.path.exists(folder) and os.listdir(folder):
        raise SystemExit(f"{folder} already has files in it. Pick an empty or new folder.")
    os.makedirs(os.path.join(folder, "concepts"), exist_ok=True)
    src = content or os.path.join(os.path.dirname(find_one_pager()), "examples", "acme.json")
    with open(src) as fh:
        c = json.load(fh)
    with open(os.path.join(folder, "content.json"), "w") as fh:
        json.dump(c, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    with open(os.path.join(folder, "dream.md"), "w") as fh:
        fh.write(PLAN.format(partner=c.get("partner") or "Bluefyn"))
    for key in "abc":
        with open(os.path.join(folder, "concepts", key + ".py"), "w") as fh:
            fh.write(TEMPLATE.format(key=key))
    print(f"started a dream in {folder}")
    print("next: fill in dream.md, design concepts/a.py, b.py and c.py, then run")
    print(f"  python3 {os.path.abspath(__file__)} build {folder}")


def first_line(fn):
    doc = inspect.getdoc(fn) or ""
    return doc.split("\n\n")[0].replace("\n", " ")


def cmd_primitives():
    print("TOKENS (k.b.<NAME>)")
    for name in ("INK", "INK_SOFT", "INK_FAINT", "RULE", "PAPER", "CARD", "NIGHT", "BLUE", "NAVY", "LIGHT_BLUE",
                 "GREEN", "RED", "WHITE"):
        print(f"  {name:11s} {getattr(b, name)}")
    for fam in ("logo", "drawings", "textures"):
        print(f"\n{fam.upper()} (k.b.<name>, every one returns SVG unless noted)")
        for name in CATALOGUE[fam]:
            fn = getattr(b, name)
            fn = getattr(fn, "__wrapped__", fn)
            print(f"  {name}{inspect.signature(fn)}")
            if first_line(fn):
                print(f"      {first_line(fn)}")
    print("\nRECORDS (k.b.<NAME>, for field, tower and slab: (lines, kind))")
    for name in CATALOGUE["records"]:
        lines, kind = getattr(b, name)
        print(f"  {name:16s} {kind:9s} {' / '.join(lines)}")
    print("\nBRAND FILES (k.file(rel) for a data URI, k.image(rel, w, h) for a placed picture)")
    for folder in ("logo", "avatars", "banners", "patterns"):
        files = b.brand_files(folder)
        print(f"  {folder}/  {len(files)} files")
        if folder in ("patterns",):
            for rel in files:
                print(f"    {rel}")
    print("\nThe bluefyn-design skill's references/assets.md and references/graphics.md say what each is for.")


def main():
    ap = argparse.ArgumentParser(description="Three new Bluefyn designs from one content file, light and dark.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new", help="start a dream folder")
    n.add_argument("folder")
    n.add_argument("--content", help="content JSON in the one pager schema (default: the Acme Pay example)")
    bd = sub.add_parser("build", help="render, check and compare the concepts")
    bd.add_argument("folder")
    bd.add_argument("concepts", nargs="*", help="concept keys to build (default: all)")
    bd.add_argument("--mode", choices=["light", "dark", "both"], default="both")
    sub.add_parser("primitives", help="list every brand primitive")
    args = ap.parse_args()
    if args.cmd == "new":
        cmd_new(args.folder, args.content)
    elif args.cmd == "build":
        sys.exit(0 if build(args.folder, args.concepts, args.mode) else 1)
    else:
        cmd_primitives()


if __name__ == "__main__":
    main()

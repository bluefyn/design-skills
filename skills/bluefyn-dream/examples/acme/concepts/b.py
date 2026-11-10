"""Concept b: Ledger.

No bands and no cards: one ground, a strict twelve-column grid and large type. The dark slanted field is
cut into the top-right corner as a block of evidence, and the proof figures hang under it like a ledger.
The layer stack is set as type, Bluefyn as the one filled row.
"""

CONCEPT = {
    "name": "Ledger",
    "idea": "Swiss grid and big type on one ground, with a block of slanted evidence cut into the corner.",
    "hero": "slanted_field",
}

M, COL, GUT = 36, 34, 12                       # margin, column, gutter: twelve columns across 540pt


def span(n):
    return n * COL + (n - 1) * GUT


def x(col):                                    # left edge of a 1-based column
    return M + (col - 1) * (COL + GUT)


def render(c, mode, k):
    b, e = k.b, k.esc
    dark = k.dark
    ground = b.INK if dark else "#FFFFFF"
    ink = "#F0EEEE" if dark else b.INK
    soft = "#A9A3A3" if dark else b.INK_SOFT
    hair = "rgba(255,255,255,.24)" if dark else "#CFCFCF"
    rule = "#F0EEEE" if dark else b.INK
    accent = b.LIGHT_BLUE if dark else b.BLUE

    slab_x = x(9) + 10
    slab_w, slab_h = 612 - slab_x, 200
    slab = k.image(b.slanted_field(slab_w, slab_h, fs=6.6, angle=-24, seed=29,
                                   paper="#2B2727" if dark else b.INK, ink="#8A8383" if dark else "#D6D6D6", uid="lg"),
                   slab_w, slab_h, cls="slab")

    css = f"""
.page{{background:{ground} {k.grain()};color:{ink}}}
.slab{{position:absolute;left:{slab_x}pt;top:0}}
.label{{font-size:7.8pt;line-height:1.2;color:{accent}}}
.top{{position:absolute;left:{M}pt;top:32pt;width:{span(8)}pt}}
.meta{{margin-top:6pt;display:flex;gap:14pt;font-size:7.8pt;line-height:1.2;color:{soft}}}
h1{{margin-top:30pt;font-size:30pt;line-height:1.0;letter-spacing:-.042em}}
.lede{{margin-top:11pt;width:{span(7)}pt;font-size:9.2pt;line-height:1.44}}
.told{{position:absolute;left:{x(9)}pt;top:{slab_h + 14}pt;width:{span(4)}pt}}
.told .row{{padding:4pt 0 5pt;border-top:.5pt solid {hair}}}
.told .row:first-of-type{{border-top:1.5pt solid {rule}}}
.told .fig{{font-size:17pt;line-height:1.05;letter-spacing:-.035em}}
.told .desc{{margin-top:1.5pt;font-size:8.6pt;line-height:1.28;color:{soft}}}
.told .label{{margin-bottom:5pt}}
.with{{position:absolute;left:{M}pt;top:270pt;width:{span(8)}pt;padding-top:6pt;border-top:1.5pt solid {rule}}}
.with .fig{{margin-top:2pt;font-size:46pt;line-height:.98;letter-spacing:-.05em}}
.with .desc{{margin-top:5pt;font-size:13pt;line-height:1.16;letter-spacing:-.022em;color:{ink}}}

.lower{{position:absolute;left:{M}pt;top:374pt;width:540pt;bottom:26pt;display:flex;flex-direction:column;justify-content:space-between}}
.g12{{display:grid;grid-template-columns:repeat(12,{COL}pt);column-gap:{GUT}pt}}
.sides .l1{{grid-column:1 / span 4}}
.sides .l2{{grid-column:5 / span 4;text-align:right}}
.sides .stack{{grid-column:9 / span 4;grid-row:1 / span 2}}
.col{{margin-top:6pt;border-top:1.5pt solid {rule};padding-top:6pt}}
.c1{{grid-column:1 / span 4}}
.c2{{grid-column:5 / span 4}}
.col h2{{font-size:13pt;line-height:1.12;letter-spacing:-.022em}}
.col .tag{{display:block;margin-top:1pt;font-size:7.8pt;line-height:1.2;color:{accent}}}
.col .sub{{margin-top:3pt;font-size:8.6pt;line-height:1.3;color:{soft};min-height:22.4pt}}
.col ul{{margin-top:4pt}}
.col li{{font-size:8.9pt;line-height:1.28;padding:3pt 0 2.8pt;border-top:.5pt solid {hair}}}
.stack .rows{{margin-top:6pt;border-top:1.5pt solid {rule}}}
.stack .row{{font-size:10pt;line-height:1;padding:5.2pt 6pt 4.8pt;border-bottom:.5pt solid {hair};color:{soft}}}
.stack .row.lead{{background:{b.BLUE};color:#fff;border-bottom:0}}
.stack p{{margin-top:7pt;font-size:10pt;line-height:1.26;letter-spacing:-.012em}}
.flags .label{{margin-bottom:5pt}}
.flag{{padding:3.6pt 0 3.4pt;border-top:.5pt solid {hair};font-size:9pt;line-height:1.28}}
.flag:first-of-type{{border-top:1.5pt solid {rule}}}
.flag .if{{grid-column:1 / span 4}}
.flag .then{{grid-column:5 / span 8;color:{soft}}}
.closing > div{{grid-column:span 4}}
.closing .label{{margin-bottom:4pt}}
.closing p,.closing li{{font-size:8.6pt;line-height:1.36}}
.next{{border-top:1.5pt solid {rule};padding-top:7pt;align-items:start}}
.next .say{{grid-column:1 / span 8}}
.next .say p{{margin-top:3pt;font-size:13.4pt;line-height:1.2;letter-spacing:-.02em}}
.next .who{{grid-column:9 / span 4;font-size:8.6pt;line-height:1.38}}
.next .who .name{{display:flex;align-items:center;gap:5pt;font-size:10.4pt;margin-bottom:2pt}}
.next .who .mail{{color:{accent}}}
"""

    meta = "".join(f"<span>{e(m)}</span>" for m in c.get("meta", []))
    out = [slab, f'<header class="top">{k.lockup(c, ink, 12.5)}<div class="meta">{meta}</div>'
                 f'<h1>{e(c["headline"])}</h1>' + (f'<p class="lede">{e(c["lede"])}</p>' if c.get("lede") else "") + "</header>"]

    told = c.get("told")
    if told:
        rows = "".join(f'<div class="row"><div class="fig{" num" if k.numeric(r["figure"]) else ""}">{e(r["figure"])}</div>'
                       f'<div class="desc">{e(r["text"])}</div></div>' for r in told["rows"])
        out.append(f'<section class="told"><div class="label">{e(told["label"])}</div>{rows}</section>')
    w = c.get("with")
    if w:
        out.append(f'<section class="with"><div class="label">{e(w["label"])}</div><div class="fig">{e(w["figure"])}</div>'
                   f'<p class="desc">{e(w["text"])}</p></section>')

    lower = []
    s, layer = c.get("sides"), c.get("layer")
    if s or layer:
        row = []
        if s:
            row.append(f'<div class="label l1">{e(s.get("label", ""))}</div><div class="label l2">{e(s.get("note", ""))}</div>')
            for i, col in enumerate(s["columns"], 1):
                tag = f'<span class="tag">{e(col["mark"])}</span>' if col.get("mark") else ""
                sub = f'<p class="sub">{e(col["sub"])}</p>' if col.get("sub") else ""
                items = "".join(f"<li>{e(t)}</li>" for t in col["items"])
                row.append(f'<div class="col c{i}" style="grid-row:2"><h2>{e(col["title"])}{tag}</h2>{sub}<ul>{items}</ul></div>')
        if layer:
            stack = layer["stack"]
            rows = "".join(f'<div class="row{" lead" if i == 0 else ""}">{e(name)}</div>' for i, name in enumerate(stack))
            row.append(f'<div class="stack"><div class="label">{e(layer["label"])}</div><div class="rows">{rows}</div>'
                       f'<p>{e(layer["text"])}</p></div>')
        lower.append(f'<section class="g12 sides">{"".join(row)}</section>')
    f = c.get("flags")
    if f:
        rows = "".join(f'<div class="g12 flag"><div class="if">{e(r[0])}</div><div class="then">{e(r[1])}</div></div>' for r in f["rows"])
        lower.append(f'<section class="flags"><div class="label">{e(f["label"])}</div>{rows}</section>')
    blocks = c.get("closing") or []
    if blocks:
        cells = ""
        for blk in blocks:
            body = (f'<p>{e(blk["text"])}</p>' if blk.get("text")
                    else "<ul>" + "".join(f"<li>{e(t)}</li>" for t in blk["items"]) + "</ul>")
            cells += f'<div><div class="label">{e(blk["label"])}</div>{body}</div>'
        lower.append(f'<section class="g12 closing">{cells}</section>')
    n = c["next"]
    contact = n.get("contact") or {}
    who = ""
    if contact:
        who = (f'<div class="who"><div class="name">{b.symbol(ink, 8.5)}<span>{e(contact["name"])}</span></div>'
               f'<div>{e(contact.get("role", ""))}</div><div class="mail">{e(contact.get("email", ""))}</div></div>')
    lower.append(f'<footer class="g12 next"><div class="say"><div class="label">{e(n["label"])}</div><p>{e(n["text"])}</p></div>{who}</footer>')
    out.append(f'<main class="lower" data-box="lower">{"".join(lower)}</main>')
    return css, "".join(out)

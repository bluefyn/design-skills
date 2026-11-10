"""Concept c: Tower.

The design team's tower pattern is the top of the page, on the same ground as the page, so the tower of
records rises out of the paper (or out of the night in dark mode). Under it the problem and the answer
read as one row, left to right, and a Bluefyn blue band closes the page with the next step.
"""

CONCEPT = {
    "name": "Tower",
    "idea": "The finished tower pattern rises out of the page; problem and answer read across one row below it.",
    "hero": "patterns",
}

M = 36
HERO_H = 272
FOOT_H = 66


def render(c, mode, k):
    b, e = k.b, k.esc
    dark = k.dark
    ground = b.NIGHT if dark else b.PAPER
    ink = "#EDEDED" if dark else b.INK
    soft = "#A8A8A8" if dark else b.INK_SOFT
    hair = "rgba(255,255,255,.22)" if dark else "#CFCFCF"
    rule = "#EDEDED" if dark else b.INK
    accent = b.LIGHT_BLUE if dark else b.BLUE
    pattern = "patterns/bluefyn-pattern-tower-night.svg" if dark else "patterns/bluefyn-pattern-tower-paper.svg"
    # The pattern is 2:1 with the tower in its middle (about 30 to 70 percent across). Set smaller and
    # pushed right, the tower stands at the page edge and the left of the hero stays clear for type.
    pic_w, pic_h, pic_x = 560, 280, 210
    hero = k.image(pattern, pic_w, pic_h, fit="cover", cls="tower", clear=(0.3, 0, 0.7, 1))

    css = f"""
.page{{background:{ground} {k.grain()};color:{ink}}}
.hero{{position:absolute;left:0;top:0;width:612pt;height:{HERO_H}pt;overflow:hidden}}
.hero .tower{{position:absolute;left:{pic_x}pt;top:-4pt}}
.hero .grainy{{position:absolute;inset:0;background:{k.grain()}}}
.hero .copy{{position:absolute;left:{M}pt;top:32pt;width:298pt}}
.meta{{margin-top:6pt;font-size:7.8pt;line-height:1.35;color:{soft}}}
h1{{margin-top:22pt;font-size:26pt;line-height:1.03;letter-spacing:-.038em}}
.lede{{margin-top:9pt;font-size:9pt;line-height:1.42}}
.label{{font-size:7.8pt;line-height:1.2;color:{accent}}}

.lower{{position:absolute;left:{M}pt;right:{M}pt;top:{HERO_H + 8}pt;bottom:{FOOT_H + 14}pt;display:flex;flex-direction:column;justify-content:space-between}}
.g12{{display:grid;grid-template-columns:repeat(12,1fr);column-gap:12pt}}
.proof .label{{grid-column:1 / span 12;margin-bottom:5pt}}
.cell{{grid-column:span 3;border-top:.75pt solid {rule};padding-top:5pt}}
.cell .fig{{font-size:20pt;line-height:1.05;letter-spacing:-.035em}}
.cell .desc{{margin-top:2pt;font-size:8.6pt;line-height:1.28;color:{soft}}}
.cell.answer{{border-top:2pt solid {b.BLUE};{'' if not dark else ''}}}
.cell.answer .fig{{color:{accent}}}
.cell.answer .desc{{color:{ink}}}
.cell.answer .tagline{{font-size:7.8pt;line-height:1.2;color:{accent};margin-bottom:2pt}}

.sides .l1{{grid-column:1 / span 4}}
.sides .l2{{grid-column:5 / span 4;text-align:right}}
.sides .col{{grid-row:2;margin-top:5pt}}
.c1{{grid-column:1 / span 4}}
.c2{{grid-column:5 / span 4}}
.col h2{{display:flex;align-items:baseline;justify-content:space-between;gap:6pt;font-size:12.4pt;line-height:1.15;letter-spacing:-.02em;
  padding-bottom:4pt;border-bottom:.75pt solid {rule}}}
.col .tag{{font-size:7.8pt;letter-spacing:0;color:{accent}}}
.col .sub{{margin-top:4pt;font-size:8.6pt;line-height:1.3;color:{soft};min-height:22.4pt}}
.col ul{{margin-top:3pt}}
.col li{{font-size:8.8pt;line-height:1.27;padding:2.8pt 0 2.6pt;border-top:.5pt solid {hair}}}
.layer{{grid-column:9 / span 4;grid-row:1 / span 2;display:flex;flex-direction:column}}
.layer svg{{margin:6pt 0 4pt}}
.layer p{{font-size:9.6pt;line-height:1.26;letter-spacing:-.01em}}
.flags .label{{margin-bottom:4pt}}
.flag{{padding:3.2pt 0 3pt;border-top:.5pt solid {hair};font-size:8.9pt;line-height:1.27}}
.flag:last-child{{border-bottom:.5pt solid {hair}}}
.flag .if{{grid-column:1 / span 4}}
.flag .then{{grid-column:5 / span 8}}
.closing > div{{grid-column:span 4}}
.closing .label{{margin-bottom:3pt}}
.closing p,.closing li{{font-size:8.5pt;line-height:1.34}}

.foot{{position:absolute;left:0;right:0;bottom:0;height:{FOOT_H}pt;background:{b.BLUE} {k.grain('dark')};color:#fff}}
.foot .g12{{height:100%;margin:0 {M}pt;align-items:center}}
.foot .say{{grid-column:1 / span 8}}
.foot .say .label{{color:{b.LIGHT_BLUE};margin-bottom:3pt}}
.foot .say p{{font-size:12.2pt;line-height:1.2;letter-spacing:-.018em}}
.foot .who{{grid-column:9 / span 4;font-size:8pt;line-height:1.36;padding-left:10pt;border-left:.5pt solid rgba(255,255,255,.6)}}
.foot .who .name{{display:flex;align-items:center;gap:5pt;font-size:10.4pt;margin-bottom:1pt}}
.foot .who .mail{{color:{b.LIGHT_BLUE}}}
"""

    meta = "<br>".join(e(m) for m in c.get("meta", []))
    lede = f'<p class="lede">{e(c["lede"])}</p>' if c.get("lede") else ""
    out = [f'<section class="hero">{hero}<div class="grainy"></div><div class="copy">{k.lockup(c, ink, 12.5)}'
           f'<div class="meta">{meta}</div><h1>{e(c["headline"])}</h1>{lede}</div></section>']

    lower = []
    told, w = c.get("told"), c.get("with")
    if told or w:
        cells = []
        rows = (told or {}).get("rows", [])[:3]
        for r in rows:
            cells.append(f'<div class="cell"><div class="fig{" num" if k.numeric(r["figure"]) else ""}">{e(r["figure"])}</div>'
                         f'<div class="desc">{e(r["text"])}</div></div>')
        if w:
            cells.append(f'<div class="cell answer"><div class="tagline">{e(w["label"])}</div><div class="fig">{e(w["figure"])}</div>'
                         f'<div class="desc">{e(w["text"])}</div></div>')
        head = f'<div class="label">{e(told["label"])}</div>' if told else ""
        lower.append(f'<section class="g12 proof">{head}{"".join(cells)}</section>')

    s, layer = c.get("sides"), c.get("layer")
    if s or layer:
        row = []
        if s:
            row.append(f'<div class="label l1">{e(s.get("label", ""))}</div><div class="label l2">{e(s.get("note", ""))}</div>')
            for i, col in enumerate(s["columns"], 1):
                tag = f'<span class="tag">{e(col["mark"])}</span>' if col.get("mark") else ""
                sub = f'<p class="sub">{e(col["sub"])}</p>' if col.get("sub") else ""
                items = "".join(f"<li>{e(t)}</li>" for t in col["items"])
                row.append(f'<div class="col c{i}"><h2><span>{e(col["title"])}</span>{tag}</h2>{sub}<ul>{items}</ul></div>')
        if layer:
            if dark:
                plates = b.plates(layer["stack"], w=172, h=92, side=62, font="Geist", label_size=7.2, uid="pc", ink=b.INK,
                                  label_ink="#FFFFFF", soft="#DCDCDC", line="#8A8A8A", paper="#1A1A1A", top_fill="#FFFFFF")
                plates = plates.replace(f'fill="{b.RULE}"/>', 'fill="#3A3A3A"/>')
            else:
                plates = b.plates(layer["stack"], w=172, h=92, side=62, font="Geist", label_size=7.2, uid="pc",
                                  paper=b.PAPER, top_fill="#FFFFFF")
            row.append(f'<div class="layer"><div class="label">{e(layer["label"])}</div>{plates}<p>{e(layer["text"])}</p></div>')
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
    out.append(f'<main class="lower" data-box="lower">{"".join(lower)}</main>')

    n = c["next"]
    contact = n.get("contact") or {}
    who = ""
    if contact:
        who = (f'<div class="who"><div class="name">{b.symbol(b.WHITE, 8.5)}<span>{e(contact["name"])}</span></div>'
               f'<div>{e(contact.get("role", ""))}</div><div class="mail">{e(contact.get("email", ""))}</div></div>')
    out.append(f'<footer class="foot"><div class="g12"><div class="say"><div class="label">{e(n["label"])}</div>'
               f'<p>{e(n["text"])}</p></div>{who}</div></footer>')
    return css, "".join(out)

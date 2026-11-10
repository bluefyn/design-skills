"""Concept a: Spine.

A full-height navy rail on the left carries who it is for, what they told us and the next step, over
the checking stream running top to bottom. The argument reads down the right in one narrow column.
"""

CONCEPT = {
    "name": "Spine",
    "idea": "A navy spine holds the proof and the next step; the argument runs down the page beside it.",
    "hero": "stream",
}

RAIL = 196          # rail width, pt
BODY_X = 222        # body column starts here
BODY_W = 612 - BODY_X - 34


def render(c, mode, k):
    b, e = k.b, k.esc
    dark = k.dark
    ink = "#EBEBEB" if dark else b.INK
    soft = "#BDBDBD" if dark else b.INK_SOFT
    hair = "rgba(255,255,255,.26)" if dark else b.INK_FAINT
    label = b.LIGHT_BLUE if dark else b.BLUE

    stream = k.image(b.stream(RAIL, 792, fs=3.4, seed=5, fill=b.WHITE, opacity=0.13 if dark else 0.16),
                     RAIL, 792, cls="stream")

    css = f"""
.page{{background:{b.NIGHT if dark else b.PAPER} {k.grain()};color:{ink}}}
.rail{{position:absolute;left:0;top:0;bottom:0;width:{RAIL}pt;background:{b.NAVY} {k.grain('dark')};color:#fff;overflow:hidden}}
.rail .stream{{position:absolute;left:0;top:0}}
.rail .in{{position:relative;height:100%;display:flex;flex-direction:column;padding:30pt 20pt 28pt 32pt}}
.rail .label{{font-size:7.8pt;line-height:1.2;color:{b.LIGHT_BLUE}}}
.rail .lockup .partner{{font-size:11.6pt}}
.meta{{margin-top:9pt;font-size:7.8pt;line-height:1.4;color:rgba(255,255,255,.86)}}
.told{{margin-top:58pt}}
.told .row{{padding:8pt 0 10pt;border-top:.5pt solid rgba(255,255,255,.45)}}
.told .fig{{font-size:27pt;line-height:1.05;letter-spacing:-.035em}}
.told .desc{{margin-top:2pt;font-size:8.6pt;line-height:1.3}}
.next{{margin-top:auto}}
.next p{{margin-top:5pt;font-size:11.4pt;line-height:1.24;letter-spacing:-.015em}}
.who{{margin-top:14pt;padding-top:8pt;border-top:.5pt solid rgba(255,255,255,.6)}}
.who .name{{display:flex;align-items:center;gap:6pt;font-size:10.4pt;line-height:1.2}}
.who .role,.who .mail{{font-size:7.8pt;line-height:1.4;margin-top:2pt}}
.who .mail{{color:{b.LIGHT_BLUE}}}

.body{{position:absolute;left:{BODY_X}pt;top:30pt;width:{BODY_W}pt;height:{792 - 30 - 26}pt;display:flex;flex-direction:column}}
.body .label{{font-size:7.8pt;line-height:1.2;color:{label}}}
h1{{font-size:25pt;line-height:1.04;letter-spacing:-.036em}}
.lede{{margin-top:9pt;font-size:9.2pt;line-height:1.44;color:{ink}}}
.with{{margin-top:auto;display:grid;grid-template-columns:118pt 1fr;column-gap:12pt;align-items:end;padding-top:8pt;border-top:.75pt solid {ink}}}
.with .label{{grid-column:1 / span 2;margin-bottom:4pt}}
.with .fig{{font-size:22pt;line-height:1;letter-spacing:-.04em}}
.with .desc{{font-size:12.6pt;line-height:1.16;letter-spacing:-.02em;padding-bottom:1.5pt}}
.sides{{margin-top:auto}}
.sides .heads{{display:flex;justify-content:space-between;gap:12pt}}
.cols{{margin-top:6pt;display:grid;grid-template-columns:1fr 1fr;column-gap:12pt}}
.col{{border-top:.75pt solid {ink};padding-top:6pt}}
.col h2{{display:flex;justify-content:space-between;align-items:center;gap:6pt;font-size:12pt;line-height:1.15;letter-spacing:-.02em}}
.col .sub{{margin-top:2pt;font-size:8.6pt;line-height:1.3;color:{soft};min-height:22.4pt}}
.col li{{font-size:8.8pt;line-height:1.28;padding:3pt 0 2.8pt;border-top:.5pt solid {hair}}}
.col ul{{margin-top:4pt}}
.layer{{margin-top:auto;display:grid;grid-template-columns:150pt 1fr;column-gap:14pt;align-items:center;
  background:{'#1A1A1A' if dark else b.NIGHT} {k.grain('dark')};color:#fff;padding:9pt 12pt 9pt 10pt;{'border:.5pt solid rgba(255,255,255,.26);' if dark else ''}}}
.layer .label{{color:{b.LIGHT_BLUE};margin-bottom:5pt}}
.layer p{{font-size:10.4pt;line-height:1.24;letter-spacing:-.012em}}
.flags{{margin-top:auto}}
.flag{{display:grid;grid-template-columns:150pt 1fr;column-gap:14pt;padding:3.4pt 0 3.2pt;border-top:.5pt solid {hair};font-size:8.9pt;line-height:1.28}}
.flag:last-child{{border-bottom:.5pt solid {hair}}}
.flags .label{{margin-bottom:5pt}}
.closing{{margin-top:auto;display:grid;grid-template-columns:repeat({max(1, len(c.get('closing') or []))},1fr);column-gap:12pt}}
.closing .label{{margin-bottom:4pt}}
.closing p,.closing li{{font-size:8.6pt;line-height:1.36}}
"""

    told = c.get("told")
    told_html = ""
    if told:
        rows = "".join(f'<div class="row"><div class="fig{" num" if k.numeric(r["figure"]) else ""}">{e(r["figure"])}</div>'
                       f'<div class="desc">{e(r["text"])}</div></div>' for r in told["rows"])
        told_html = f'<div class="told"><div class="label">{e(told["label"])}</div>{rows}</div>'
    meta = "<br>".join(e(m) for m in c.get("meta", []))
    n = c["next"]
    contact = n.get("contact") or {}
    who = ""
    if contact:
        who = (f'<div class="who"><div class="name">{b.symbol(b.WHITE, 9)}<span>{e(contact["name"])}</span></div>'
               f'<div class="role">{e(contact.get("role", ""))}</div><div class="mail">{e(contact.get("email", ""))}</div></div>')
    rail = (f'<aside class="rail">{stream}<div class="in">{k.lockup(c, b.WHITE, 12)}<div class="meta">{meta}</div>'
            f'{told_html}<div class="next"><div class="label">{e(n["label"])}</div><p>{e(n["text"])}</p>{who}</div></div></aside>')

    parts = [f'<h1>{e(c["headline"])}</h1>']
    if c.get("lede"):
        parts.append(f'<p class="lede">{e(c["lede"])}</p>')
    w = c.get("with")
    if w:
        parts.append(f'<div class="with"><div class="label">{e(w["label"])}</div><div class="fig">{e(w["figure"])}</div>'
                     f'<div class="desc">{e(w["text"])}</div></div>')
    s = c.get("sides")
    if s:
        cols = ""
        for col in s["columns"]:
            mark = k.mark(col["mark"], "checking") if col.get("mark") else ""
            sub = f'<p class="sub">{e(col["sub"])}</p>' if col.get("sub") else ""
            items = "".join(f"<li>{e(t)}</li>" for t in col["items"])
            cols += f'<div class="col"><h2>{e(col["title"])}{mark}</h2>{sub}<ul>{items}</ul></div>'
        heads = f'<div class="heads"><div class="label">{e(s.get("label", ""))}</div><div class="label">{e(s.get("note", ""))}</div></div>'
        parts.append(f'<section class="sides">{heads}<div class="cols">{cols}</div></section>')
    layer = c.get("layer")
    if layer:
        plates = b.plates(layer["stack"], w=150, h=84, side=58, font="Geist", label_size=7, uid="pa", ink=b.INK,
                          label_ink="#FFFFFF", soft="#DCDCDC", line="#999999", paper="#1A1A1A", top_fill="#FFFFFF")
        plates = plates.replace(f'fill="{b.RULE}"/>', 'fill="#3A3A3A"/>')
        parts.append(f'<section class="layer">{plates}<div><div class="label">{e(layer["label"])}</div>'
                     f'<p>{e(layer["text"])}</p></div></section>')
    f = c.get("flags")
    if f:
        rows = "".join(f'<div class="flag"><div>{e(r[0])}</div><div>{e(r[1])}</div></div>' for r in f["rows"])
        parts.append(f'<section class="flags"><div class="label">{e(f["label"])}</div>{rows}</section>')
    blocks = c.get("closing") or []
    if blocks:
        cells = ""
        for blk in blocks:
            body = (f'<p>{e(blk["text"])}</p>' if blk.get("text")
                    else "<ul>" + "".join(f"<li>{e(t)}</li>" for t in blk["items"]) + "</ul>")
            cells += f'<div><div class="label">{e(blk["label"])}</div>{body}</div>'
        parts.append(f'<section class="closing">{cells}</section>')

    return css, rail + f'<main class="body" data-box="body">{"".join(parts)}</main>'

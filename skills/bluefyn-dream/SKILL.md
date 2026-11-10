---
name: bluefyn-dream
description: Design three new and different Bluefyn pages from one content file, each in light and dark mode, using the brand's logo, drawings, textures, records, finished patterns and brand files, and the frontend design method. Use it when someone asks for design options, alternatives, concepts, explorations, "something different", "three versions", "dream up" a page, or wants to see what else a one pager could look like. The content uses the bluefyn-one-pager schema. Needs bluefyn-design and bluefyn-one-pager installed next to it.
---

# Bluefyn dream

This skill produces three designs for the same content. Each is a one-page US Letter PDF in light and
dark mode, so one run gives six PDFs and a contact sheet that shows them side by side. The person picks a
direction, and the chosen one can be refined or turned into a template.

The bluefyn-one-pager template is the approved layout. A dream is the opposite: three new layouts, each
with its own idea. They follow the brand book exactly and differ in composition.

## Read first

Read these before you plan. They are the rules the three designs share.

1. bluefyn-design `SKILL.md` and `references/brand.md`: colors, Geist, the logo, the leave-out list and
   the review points.
2. bluefyn-design `references/frontend-design.md`: the design method. Follow its order: ground the work in
   the subject, plan, review the plan, build, critique.
3. bluefyn-design `references/graphics.md` and `references/assets.md`: what each drawing and each finished
   brand file is for.
4. bluefyn-one-pager `references/content-schema.md`: the content fields.
5. One of the concepts in `examples/acme/concepts/`, to learn the interface. Read it for how the code is
   built. Do not reuse its composition.

Then list everything the brand has to draw with:

```bash
python3 <this skill's folder>/scripts/dream.py primitives
```

## Workflow

### 1. Get the content

The dream takes a content file in the bluefyn-one-pager schema. If the person has one, use it. If they
gave notes, an email or a document, turn it into a content file first with the bluefyn-copywriter skill
if it is installed, or by following bluefyn-one-pager's steps 1 to 3. All three designs show the same
words. The dream changes the design, not the copy.

### 2. Start the dream folder

```bash
python3 <this skill's folder>/scripts/dream.py new <folder> --content <content.json>
```

The folder gets `content.json`, a plan file `dream.md` and three concept files, `concepts/a.py`, `b.py`
and `c.py`. In a Bluefyn design workspace, use `dreams/<name>` as the folder.

### 3. Plan the three concepts

Fill in `dream.md` before you write code. For each concept, write down its name, the idea in one
sentence, the hero, the structure, the ground and contrast in each mode, the type, and what it will be
remembered for.

The three must be different designs, not three colorways of one design. Make them differ in all of these:

- **The hero.** Each concept has one hero graphic, and no two share it. Pick from the drawings (`tower`,
  `slab`, `scan_band`, `slanted_field`, `ellipses`, `discs`, `field` with records), the textures
  (`stream`, `record_texture`), the plate stack (`plates`), or a finished brand file (`patterns`,
  `banners`). Across the three, reach into different families: for example one drawing, one texture
  and one finished pattern.
- **The structure.** What leads and where things sit. A vertical rail, a poster top, a Swiss grid with
  large type, a centered cube, a full-bleed ground, a two-column paper, a ledger table: pick three that
  change how the eye moves down the page.
- **The first impression.** Squint at the three side by side. If two read the same at that distance,
  rework one.

They must also differ from the bluefyn-one-pager template (navy header, three columns, navy footer) and
from the shipped examples (Spine, Ledger and Tower). The build reports a concept whose code is too close
to an example or to another concept.

Review the plan against the brand's leave-out list before you build. Spend each concept's boldness in one
place: one hero, one large type moment, or one strong contrast.

### 4. Write the concepts

Each concept file holds `CONCEPT` and `render(c, mode, k)`:

```python
CONCEPT = {"name": "Spine", "idea": "One sentence.", "hero": "stream"}

def render(c, mode, k):
    css = "..."          # styles for .page and everything inside it
    body = "..."         # the page's HTML; dream.py wraps it in <div class="page light|dark">
    return css, body
```

`c` is the content, `mode` is `"light"` or `"dark"`, and `k` is the kit:

| Kit | What it gives you |
| --- | --- |
| `k.b` | The brand module: tokens such as `k.b.INK` and `k.b.NAVY`, `logo`, `symbol`, `wordmark`, every drawing and the `REC_*` records |
| `k.esc(text)` | Copy escaped for HTML, with hyphenated words kept on one line. Use it on every content string |
| `k.numeric(text)` | True when a figure starts with a number, so you can give it the class `num` |
| `k.lockup(c, fill, size)` | The logo with "× partner" beside it |
| `k.mark(word, kind)` | A verdict mark, kind `match`, `off` or `checking`. The word is required |
| `k.grain(kind)` | The fine grain as a CSS background. Every ground gets it |
| `k.texture()` | The record texture image for navy grounds |
| `k.file(rel)` | A finished brand file as a data URI |
| `k.image(src, w, h, clear=...)` | A drawing or a brand file placed as a picture. It renders once and is cached |

Rules for the code:

- **Use `k.image()` for anything made of digits or record words.** That means the stream, the slanted
  field, the tower and the patterns. It turns the drawing into a picture, so those words stay out of the
  PDF's text. Keep the plate stack and the logo as inline SVG, because their labels are content.
- **Mark where a drawing is with `clear`.** Pass `True` for the whole picture or a fraction box such as
  `(0.3, 0, 0.7, 1)`. The build then reports copy that runs over it. Leave `clear` out only for a texture
  that copy is meant to sit on.
- **Put every content field on the page.** The build compares the page text with the content file and
  reports anything missing. Do not add copy that is not in the content.
- **Mark regions with `data-box="name"`.** A box that has a fixed height and holds a stack of sections is
  reported if its content overflows it.
- **Each mode has its own ground.** Light is paper or white, dark is night, ink or navy. The build checks
  the ground of `.page`. Do not invert one mode to get the other. Tone the graphics down on dark grounds:
  charcoal faces and gray digits.
- **Geist for every word, Arial for data.** dream.py loads Geist. Do not set another font on copy.
- **Sizes.** Body copy 8.6pt or more, labels 7.8pt, nothing a person reads under 7pt. Verdict marks are
  6.1pt by brand rule, and the size check skips them.

### 5. Build

```bash
python3 <this skill's folder>/scripts/dream.py build <folder>
```

It builds every concept in light and dark, then writes `out/sheet.png`, the contact sheet. To rebuild one
concept, name it: `dream.py build <folder> b`. Add `--mode light` while you iterate.

The report has one line per concept and mode, then the problems:

```
[a light] Spine: pages=1 smallest=7.8pt fits=yes
[b dark] Ledger: pages=1 smallest=6.6pt fits=NO
[b dark] problem: text on text: CHECKS  /  ERP
[c light] problem: text on the graphic: 'Every vendor and customer...' runs over a picture marked clear.
[a] Spine / hero stream / uses: grain, logo, plates, stream, symbol
not used in this dream: drawings: field, tower, slab ...
[dream] ready to show
```

The build reports these problems:

- the page is more than one page, or is not 612 by 792pt
- Geist is missing from the PDF
- a ground is wrong for its mode
- a box overflows, or text runs off the page
- text sits on other text, or on a picture marked clear
- copy under 7pt
- a content field is missing from the page
- the copy contains an em dash, an en dash, a bullet, an arrow or an exclamation point
- the declared hero is not used
- two concepts share a hero, or a concept's code is too close to another concept or to an example

The `uses` lines and the `not used` line show which drawings, textures and files the dream drew on. Use them to check that
the three concepts reach into different families.

Exit code 0 means every concept is ready. Exit code 1 means there is a problem to fix.

### 6. Look and critique

The checks catch broken pages, not weak ones. Open `out/sheet.png` and every PNG, and judge them as the
frontend-design method says:

- Does each concept have one clear idea that you could say in a sentence?
- Is the hierarchy right: the claim first, then the proof, then the next step?
- Does every block start on a shared edge? Are the columns even?
- Is the dark mode a real design on its own ground, with graphics toned down, rather than a copy of light?
- Go through the bluefyn-design "Check before you show it" list for each page.

Fix and rebuild until you would show all three. If one concept stays weak, replace it with a new idea
rather than polishing it.

### 7. Hand over

Send the contact sheet and the six PDFs from `out/`. For each concept, give its name and its idea in one
line. Say which drawings, textures and files each one used, what you checked by eye, and anything you were not sure of.
Ask which direction to take further.

## When the person picks one

- To refine it, keep working in its concept file and rebuild that concept.
- To make it a reusable template for future pages, say so and offer to turn the concept into a local
  one pager kit. Do not change the shared bluefyn-one-pager template without the brand owner's sign-off.

## Files

- `scripts/dream.py`: starts a dream, builds and checks it. It reuses bluefyn-one-pager's browser and PDF code and bluefyn-design's
  `brand.py`.
- `examples/acme/`: three finished concepts (Spine, Ledger, Tower) with their plan and contact sheet. Every
  new dream must design something other than these three.

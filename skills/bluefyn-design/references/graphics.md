# Brand graphics in `scripts/brand.py`

Every function returns an SVG string you can place in HTML. Sizes are in points. All drawings are
deterministic: the same arguments draw the same picture, and `seed` changes the digits. Python standard
library only.

```python
import sys
sys.path.insert(0, "<bluefyn-design skill folder>/scripts")
import brand as b
```

Read the function's docstring and signature in `brand.py` before you use one. This page says what each is
for and where it has been used.

## Tokens

`b.INK`, `b.INK_SOFT`, `b.INK_FAINT`, `b.RULE`, `b.PAPER`, `b.CARD`, `b.NIGHT`, `b.BLUE`, `b.NAVY`,
`b.LIGHT_BLUE`, `b.GREEN`, `b.RED`, `b.WHITE`. Use these, not hex values typed by hand.

## Logo

- `b.logo(fill, height)`: symbol and wordmark.
- `b.symbol(fill, height)`: the symbol alone, for tags and small spaces.
- `b.wordmark(fill, height)`: the wordmark alone.

## Assets as data URIs

- `b.geist_face()`: the `@font-face` rule for Geist with the font embedded.
- `b.grain("dark")`, `b.grain("light")`: the grain tiles. Use as
  `background: <color> url("...") 0 0 / 108pt 108pt`.

Embedding keeps the HTML self-contained, so it prints the same from any folder.

## Fields and records

- `b.field(w, h, fs, rng, records, paper, ink)`: a flat digit field with records set into it. `records` is
  a list of `(row, column, record)`.
- Ready-made records: `b.REC_TX_CHECKING`, `b.REC_OFF`, `b.REC_MATCH`, `b.REC_FX`, `b.REC_INVOICE`,
  `b.REC_MATH`, `b.REC_CLAUSE`, `b.REC_VOLUME`. A record is `(lines, kind)` where kind is `"checking"`,
  `"match"`, `"off"` or `"plain"`. The last line of a verdict record is the verdict word.
- `b.Rng(seed)`: the small generator the drawings share.

Keep record text plausible and generic (transaction IDs, clause numbers, amounts). Never put a real
customer's data in a drawing.

## Drawings

| Function | What it draws | Used in |
| --- | --- | --- |
| `b.record_texture(w, h, fs, seed, fill, opacity)` | The check log as a low-contrast texture, as SVG text | Brand book cover. For PDFs use `b.texture()`, the same texture as an image, so its words stay out of the document text |
| `b.plates(labels, w, h, side, ...)` | The isometric plate stack, Bluefyn on top | The "A layer above" card on the one pager |
| `b.tower(box_w, box_h, cx, y_near, wl, wr, height, ...)` | The cube of records. Set `wl == wr == height` for a true cube | Brand book imagery page |
| `b.scan_band(w, h, scan_x, ...)` | A flat field mid-check, with a blue scan line | Brand book graphics page |
| `b.ellipses(w, h, n, rx, ry, gap, top, ...)` | Stacked ellipses filled with slanted words | Brand book graphics page |
| `b.stream(w, h, ...)` | The record texture in vertical columns | Brand book graphics page |
| `b.slab(w, h, x0, y0, length, ...)` | A long block of records seen from the front | Brand book graphics page. Tried on the one pager and removed as too loud |
| `b.slanted_field(w, h, ...)`, `b.discs(w, h, ...)` | A turned dark field; notched discs | Not used in an approved page yet |

## Choosing one

- One hero drawing per page. The others stay small or stay out.
- On navy or dark grounds, prefer the record texture and the plate stack. A white slab or cube on a dark
  page was judged too bright in review; if you need one there, pass charcoal faces and gray digits
  (`shades=("#2E2B2B", b.INK), ink="#7A7A7A", rec_ink="#FFFFFF"`).
- Draw the cube whole, with three equal faces. Do not crop it into a tower.
- Every verdict color carries its word. Do not use the blue, green or red blocks as plain decoration.

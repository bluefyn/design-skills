---
name: bluefyn-one-pager
description: Turn any text into a Bluefyn one pager, a one-page print-ready PDF (US Letter) in the Bluefyn brand, light or dark, built from the bundled template. Use it whenever someone asks for a one pager, one-pager, sales sheet, leave-behind, prospect or customer brief, or "something to send to <company>", and whenever they hand over notes, an email, a call summary, a doc or an old PDF and want it as a one pager, even if they do not mention brand or design. Also use it to adjust the one pager template locally. Needs the bluefyn-design skill installed next to it.
---

# Bluefyn one pager

This skill turns text into a one-page PDF in the Bluefyn brand. The layout, type, colors and graphics are
already coded in `scripts/one_pager.py`, a template built from the brand book and a design review. Your
work is the content: decide what goes on the page, put it in a content file, build, look at the result
and fix what does not fit.

Do not hand-write the HTML for a normal request. The template is the approved design, and a page you
lay out from scratch will drift from it. When someone wants the design itself changed, use a local kit
(see "Tuning the template locally").

The brand rules and the design method live in the **bluefyn-design** skill. Read its `SKILL.md` and
`references/brand.md` once per session before your first one pager, so you know why the template looks
the way it does and can judge the result.

## What you produce

- `one-pager-<partner>-light.pdf` and/or `-dark.pdf`: the deliverable, one US Letter page. The copy is
  real text that can be selected and searched.
- A `.png` preview of each, which you open and look at before you say it is done.
- A `.html` of each, self-contained.

The file name comes from `partner` ("Acme Pay" gives `one-pager-acme-pay-light.pdf`). Pass `--name <stem>`
to choose another.

## Workflow

### 1. Read the source and find the page in it

The source can be anything: a finished draft, rough notes, an email thread, a call summary, a long
document, a web page, an old PDF. A one pager answers eight questions, and each has a place in the
template. Go through the source and find the answer to each.

| The reader asks | Section | What goes there |
| --- | --- | --- |
| What is this and why should I care? | `headline`, `lede` | One claim, then one short paragraph about their situation |
| What do you know about us? | `told` | Two to four facts with a figure each, in their words |
| What do you do about it? | `with` | One short figure and one line |
| How, concretely? | `sides` | Two columns of three points, such as money out and money in |
| Does it fit what we have? | `layer` | The tools it sits above, and one line |
| What will it catch? | `flags` | Three to five rows: a trigger and what they get |
| Who are you, why now, what else? | `closing` | Up to three short blocks |
| What happens next? | `next` | One concrete step and a contact |

Only `headline` and `next` are required. A section the source says nothing about stays off the page. Do
not fill it with something plausible.

Thin sources are common: call notes often hold five claims and the template has room for fifteen. Say
each thing once, in the section where it is strongest, and drop the sections you cannot fill. A page that
repeats the same line in the headline, the answer and a list reads as padding. When you have to choose,
`flags` and `layer` go first, then the third `closing` block. A shorter page with more space is fine;
the builder spreads the room out.

If the page cannot work without something the source lacks, ask for it. That is usually who the page is
for, the next step, or the contact. Ask once, with all your questions together.

### 2. Decide what you are allowed to change

How much you may touch the words depends on what you were given.

**A finished draft or an old one pager.** The copy belongs to the author. Keep the wording and the numbers
exactly. You may make these small edits, and you list them when you hand over:

- Punctuation the brand leaves out: an em dash becomes a comma or a period, an exclamation point becomes
  a period.
- Separators that are really structure. Dots, arrows, colons and dashes between items in a rough draft
  mark where one field ends and the next begins. Split there and drop the separator.
- A capital letter at the start of each list item, table cell and sentence. No period at the end of a
  list item, table cell or label.
- Moving a sentence into the section it fits.

**Raw material** (notes, a transcript, a long document). Now you are writing, because the source is not
shaped like a page. Rules for that:

- Every fact, number, name and claim on the page comes from the source. Keep each figure's value. You
  may tidy how it is written: "$85k" becomes "$85K", "~300" becomes "about 300" in a sentence.
- Prefer the source's own phrases, cut down, over new sentences.
- Keep dates as the source gives them. If it says "next Thursday" and you know the actual date, use the
  date, because a page gets read later than it is written. If you do not know it, keep their words and
  mention it when you hand over.
- A page holds 250 to 300 words, labels included.
- Write plainly: short sentences, plain verbs, no hype. If the bluefyn-unslop skill is installed, run the
  sentences through it before you build: the lede, the closing paragraphs and the next step. List items,
  table cells and figure lines are short fragments by design ("Every vendor invoice checked against its
  contract"), so leave their shape alone and only check their words.
- When you hand over, say that you wrote the copy from their material, and list anything you were unsure
  of so they can check it against what they know.

**In both cases**, section labels and the line beside the logo are structure, not claims. If the source
gives no label for a section, use a plain one in the style of the example ("What your team told us",
"Who we are") and say that you added it. "Prepared for <partner>" in `meta` is standard and can be added
the same way.

### 3. Write the content file

Copy `examples/acme.json` and replace its text. `references/content-schema.md` lists every field, which
ones are optional, and how long each can be before it stops fitting. Read it before your first build.

### 4. Build

```bash
python3 <this skill's folder>/scripts/one_pager.py content.json --out ./out --mode both
```

`--mode` is `light`, `dark` or `both`. If the user did not say, build both and let them pick. The script
needs Python 3 and a Chromium-based browser (Chrome, Chromium, Edge or Brave). If it reports that no
browser was found, ask the user to install one or to set `CHROME=/path/to/browser`. If it reports that it
cannot find the bluefyn-design skill, that skill is not installed beside this one.

### 5. Read the report

The script prints one summary line per mode, then anything it found:

```
[light] density=regular spare=23.02pt (needs 12pt) pages=1 headline=3 lines fits=yes
[light] problem: sides.columns[0].title wraps onto a second line. Shorten the title or drop its mark.
[light] note: the two 'sides' columns differ by 27pt in height. Even them out if the author agrees.
copy warning: headline: contains an em dash ('Every processor fee ...')
```

- `density` is the spacing preset it chose. It tries `roomy`, then `regular`, then `tight`, and keeps the
  first one that leaves enough room above the footer. `stretch=+Npt` means it had room to spare and put
  it between the sections.
- `problem` lines are things to fix before the page goes out: too tall, a line too wide for its column, a
  headline over three lines, a column title or a figure that wraps, or Geist missing from the PDF. Any
  problem sets `fits=NO`.
- `note` lines are advice: uneven columns, a one-line headline, a page with little on it.
- `copy warning` lines point at punctuation or typed capitals that the brand leaves out. The quoted text
  is the start of the string, not the exact spot.

Exit code 0 means there is nothing to fix. Exit code 2 means the files were written but there is a
problem or a copy warning. Notes do not change the exit code. Exit code 1 means the content file is
invalid, or the browser or the bluefyn-design skill could not be found.

### 6. Fix what does not fit

The fix for a page that is too tall, a headline that runs four lines or a title that wraps is fewer or
shorter words.

- If you wrote the copy from raw material, tighten it yourself and rebuild.
- If the copy is the author's, the cut is theirs to make. Build the faithful version first. Tell them how
  far over it is (one body line is about 12pt, one table row about 19pt). If you can see a small cut that
  solves it, build that as a second file with `--name <stem>-proposal` and show both, with the cut
  spelled out.

When a line is too wide (`sides.note` or the contact line), shorten that string.

When the page is mostly empty, suggest the sections that are missing, or tell the user that a short
message may be better as an email than as a one pager.

### 7. Look at it

Open the PNG preview and check it against this list. The report covers some of it, but a person will
judge the page by eye, so you do too:

- The headline is two or three lines, and no line holds a single word.
- No heading or figure wraps in an ugly place.
- The two columns under "sides" are about the same height, and the closing blocks end at similar heights.
- Nothing is said twice on the page.
- Nothing touches the footer. A gap above it about the size of the gaps between sections is right; a
  band more than twice that means the page is short of content.
- The page says what the source says. It prints the strings in your content file exactly, so compare the
  content file with the source once, fact by fact.

Then send the PDF. Say what you changed or wrote, and what you could not verify.

## Copy rules

The builder warns about the ones it can detect. The reasons are in bluefyn-design's `references/brand.md`.

- No em dashes or en dashes. Use a comma, a period or a new line.
- No middle dots or bullets as separators, no arrows, no exclamation points.
- Labels are sentence case ("What your team told us"). Capitals belong to data marks such as MONEY OUT,
  which the builder sets from a normal-case string.
- No bold for emphasis, no emoji, no hype words.
- Figures are short: "40+", "$120K", "Every bill". A figure is a number or two or three words.
- Say what Bluefyn does in plain terms. Assume the reader knows payments and contracts.

## Tuning the template locally

The installed template is shared, so do not edit it for one person's page. When someone wants to change
the design for their own use, such as a larger headline, another section order, a different header or a
new block, make a local kit and change that:

```bash
python3 <this skill's folder>/scripts/one_pager.py init ./one-pager-kit
```

The kit is a folder with its own `one_pager.py`, `brand.py`, `assets/` and a `content.json` holding the
example. It has no ties to the installed skills. Put it next to the content file it is for. Build your own
content with the kit's script, and give the output its own name so it is not confused with the standard
build:

```bash
python3 ./one-pager-kit/one_pager.py ./content.json --out ./one-pager-kit/out --mode both --name <stem>-tuned
```

Where things are in the kit's `one_pager.py`:

- `CSS`: every size, color, gap and rule. Section spacing uses the variables set from `DENSITY`.
- `DENSITY` and `MIN_SPARE`: the three spacing presets and the room each must leave above the footer.
- The functions under "markup" (`poster`, `with_block`, `sides`, `flags`, `closing`, `footer`): one per
  section. `build_html` sets their order.
- `brand.py`: colors, the logo and the drawings. `references/graphics.md` in bluefyn-design lists them.

Change one thing, rebuild, and look at the PNG before the next change. A kit may change sizes, order and
spacing; the sizes in bluefyn-design's `references/brand.md` are the shared template's defaults. What
still holds in a kit is the rest of that file: the palette, the two typefaces at weight 400, the grid and
the leave-out list. The report still checks the result. For example, the headline sits in a column 356pt
wide, so a headline near 75 characters can grow only a point or two before it runs four lines. If the change should become the default for everyone, it goes to whoever owns the brand and
then into the shared template.

## Example

`examples/acme.json` builds `examples/acme-light.pdf` and `examples/acme-dark.pdf`. Acme Pay is a made-up
company with made-up figures. Look at `acme-light.jpg` and `acme-dark.jpg` to see the target, and use the
JSON as your starting point.

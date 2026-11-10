---
name: bluefyn-design
description: Bluefyn's design system for anything a person will look at. It holds the brand book (colors, type, logo, graphics, layout rules, what to leave out) and a design method for layout, hierarchy and copy. Use it whenever you design or restyle something for Bluefyn, such as a document, deck slide, poster, social image, landing or marketing page, email, or a branded PDF, and whenever someone asks what the Bluefyn brand allows, even if they only say "make it look like us" or "make this nicer". For a one pager, use the bluefyn-one-pager skill, which builds on this one.
---

# Bluefyn design

This skill holds two things, and you need both.

- **The brand book.** It decides the identity: which colors, which typeface, how the logo is used, which
  graphics exist and what never appears. These are settled. Do not invent a palette, a second typeface or
  a new graphic style.
- **A design method.** It decides whether the page is good: what leads, what sits where, how much is on
  it, what the words say. The brand book cannot do this for you. Two pages can follow every brand rule and
  one can still be cluttered and flat.

Work in the brand's vocabulary and spend your judgment on composition.

## Before you design

Read these, in this order. They are short.

1. `references/brand.md`: the brand rules, with the hex values, the type sizes, the grid, the list of things
   to leave out, and the nine points from design review that explain why the rules are what they are.
2. `references/frontend-design.md`: the design method. It is Anthropic's `frontend-design` skill, included
   here whole. The next section says how to apply it under a fixed brand.
3. `references/graphics.md`, when the piece needs a drawing: what each brand graphic is and how to draw it
   with `scripts/brand.py`.
4. `references/assets.md`, when the piece needs a logo file, a profile picture, a social banner or a
   background pattern: the finished files in `assets/brand/` and which one to pick.

When the job is a one pager through the bluefyn-one-pager template, this file and `brand.md` are enough:
the template has already made the layout decisions.

`references/brand-book.pdf` is the illustrated brand book. Open it when you need to see a rule applied, or
give it to a person who asks for the brand guide.

## How the method applies under a fixed brand

`frontend-design.md` asks you to choose a palette and typefaces for each brief and to take aesthetic risks.
For Bluefyn those choices are made. Use the method like this:

- **Ground it in the subject.** Still the first step. Bluefyn checks fees and invoices against contracts,
  and its readers work in finance and payments. Start from what this piece has to make one reader do.
- **Plan, then review the plan, then build, then critique.** Keep that order. Write the plan as the
  method says, but its color and type sections come from `brand.md` instead of from you. Your plan is the
  layout concept, the hierarchy and the one thing the page is remembered for.
- **Spend your boldness in one place.** Under this brand that place is composition: one large headline,
  one hero graphic, one strong contrast between a navy poster area and a quiet body. It is never a new
  color, a new font or decoration.
- **Its warnings about generated-looking pages apply in full.** They overlap with the brand's own
  leave-out list: no capital-letter eyebrow labels, no dot separators, no identical card grids, no accent
  word in a headline, no numbering for things that are not a sequence.
- **Its advice on words applies in full.** Plain verbs, sentence case, one job per line of text.
- **Where the two disagree, the brand book wins.** The method's suggestions for typefaces, radii, shadows
  and motion do not override `brand.md`.

## Building

- **Colors and type.** `assets/tokens.css` has every color and the type stacks as CSS variables. In Python,
  `scripts/brand.py` has the same values as constants (`b.BLUE`, `b.NAVY`, and so on). Use them instead of
  typing hex values.
- **Font.** Geist, weight 400, for every word. It ships in `assets/fonts/`: `Geist-Variable.woff2` for
  HTML and PDF, and `Geist-Regular.ttf` to install on a computer for Figma, Keynote or Word. Load it from
  these files or embed it with `b.geist_face()`. Do not rely on Geist being installed on the reader's
  machine, and do not substitute Inter, Helvetica or a system font. If Geist does not load, the piece is
  not finished: fix the font before you show it. Arial is the data face and needs no file.
- **Logo.** In HTML, `b.logo()`, `b.symbol()` and `b.wordmark()` draw it in any palette color. As a file,
  take it from `assets/brand/logo/`, which has the logo, the symbol, a symbol for small sizes and the
  wordmark, each in ink, white and blue, as SVG, PNG and PDF. Never retype or redraw it.
- **Ready-made files.** `assets/brand/` also holds the profile pictures (LinkedIn, Slack, X), the header
  banners (LinkedIn page, LinkedIn profile, X) and five vector patterns. When someone asks for one of
  these, hand over the file instead of building a new one. `b.brand_file()`, `b.brand_files()` and
  `b.brand_uri()` find them, and `references/assets.md` lists every file.
- **Graphics.** `scripts/brand.py` draws them as SVG: digit fields with records and verdict marks, the cube
  of records, the plate stack, the scan band, the ellipses, the record texture. `assets/brand/patterns/`
  has finished ones at 1600 x 800. Use one hero graphic per piece.
- **Textures.** `assets/grain-light.png` and `grain-dark.png` are the fine grain for paper and dark
  grounds. `assets/texture.png` is the record texture for navy.
- **Documents and print.** Lay the page out in HTML with fixed point sizes and print it with a headless
  Chromium browser. `scripts/brand.py` embeds the font and images as data URIs so the HTML stands alone.
  The bluefyn-one-pager skill's builder is a complete worked example of this.

## Check before you show it

Render the piece and look at it. Then go through this list, which is the brand's review in short form:

1. Every block starts on a shared edge of the grid. Nothing floats.
2. The most important things are the largest and have the most contrast: the claim, the proof, the next step.
3. Body text is ink (or near-white on dark), at a size people can read without effort.
4. One accent. Green and red appear only as verdicts, with their word.
5. Nothing from the leave-out list: dashes as punctuation, dot separators, capital-letter labels, pills,
   rounded tinted cards, metric-card rows, shadows, gradients, bold for emphasis, emoji, stock imagery.
6. Graphics are quiet enough that type reads first. On dark grounds they are toned down.
7. The logo is from the master file, small, with clear space, and not inside a line of text.
8. Any copy you wrote is plain. If the bluefyn-unslop skill is installed, run your copy through it.

Say what you checked and what you could not check when you hand the work over.

## Scope

This skill covers brand and marketing work. A product codebase that has its own component library and
design tokens keeps using them for product screens; use this skill there only for the method and for
brand surfaces such as a login panel or an email.

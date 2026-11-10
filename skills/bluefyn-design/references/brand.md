# Bluefyn brand rules for documents

Source: the Brand Guide page of the Bluefyn Figma file (v1.0), the master logo artwork, and the design
review of the first one pager built from it. `brand-book.pdf` in this folder is the illustrated version.
`../assets/tokens.css` has the colors and type as CSS variables.

Contents: idea, color, typography, logo, graphics, page layout, what to leave out, what the review taught us.

## The idea

Bluefyn checks every fee a company pays and every invoice it sends against its contracts. The brand works
the way the product does: every finding shows its work. So the visuals are real records, plain checks and
clear verdicts, and nothing asks to be taken on faith.

## Color

| Name | Hex | Use |
| --- | --- | --- |
| Ink | `#1C1919` | Type and the logo on light grounds. The ground of the dark mode. |
| Ink soft | `#696969` | Quiet second-order text, sparingly. Body copy is ink, not gray. |
| Ink faint | `#999999` | Hairlines on paper. |
| Rule | `#DCDCDC` | The lightest hairlines and outlines. |
| Paper | `#F5F5F5` | The light page. |
| Night | `#0F0F0F` | Dark cards. |
| Bluefyn blue | `#0035A6` | The one accent on light grounds: labels, marks, CHECKING. Pantone 286 C. |
| Navy | `#00386D` | Poster grounds: the header and the footer. Print and documents only. |
| Light blue | `#91CFFF` | The accent on navy, night and ink. Pantone 2905 C. |
| Match green | `#00A83F` | The verdict MATCH. Pantone 354 C. |
| Off contract red | `#E8170C` | The verdict OFF CONTRACT. |
| White | `#FFFFFF` | Type and the logo on dark grounds. |

- Neutrals do most of the work. Blue is the accent, used for labels and the marks.
- Green and red are verdicts, never decoration, and each always carries its word.
- On dark grounds, body text is `#EBEBEB` and headings are white. Second-order lines, such as the line under
  a column heading, may be `#BDBDBD`. Labels on navy and night, and the answer
  line, are light blue. The other section labels on the ink ground are `#BDBDBD`, so the answer stays the accent.
- No gradients and no second accent color.

## Typography

- **Geist, weight 400, for every word.** Size and tracking carry the hierarchy. No bold, no italics.
  (The Figma guide sets Inter. Documents and this pack use Geist.)
- **Arial for data only**: amounts, IDs, verdicts and marks, in capitals and figures, with tabular numbers
  and no kerning so digits keep their columns.
- Headlines run tight (about -0.03em to -0.04em). Body text keeps normal tracking.

Sizes on a US Letter page:

| Role | Size | Line height | Tracking |
| --- | --- | --- | --- |
| Page headline | 27pt | 1.03 | -0.038em |
| Answer figure | 21 to 28pt | 1.0 | -0.04em |
| Proof figure | 16pt | 1.05 | -0.035em |
| Section heading | 13.4pt | 1.15 | -0.02em |
| Statement (answer line, footer call) | 12.4 to 15.5pt | 1.15 to 1.22 | -0.02em |
| Body | 9 to 9.5pt | 1.3 to 1.46 | 0 |
| Label | 7.8pt | 1.2 | 0, sentence case |
| Mark | 6.1pt Arial capitals | 1.0 | 0, white on the verdict color |

Body copy is 9pt or larger. Short supporting lines may be smaller: figure descriptions at 8.6pt, labels at
7.8pt, the contact line at 7.3pt. These are the shared one pager's sizes; other pieces scale from them.

## Logo

- Two parts: the symbol (four fins set as a B) and the wordmark. Use `assets/bluefyn-logo.svg` through
  `brand.logo()`, `brand.symbol()` or `brand.wordmark()`. Never retype the wordmark or redraw the symbol.
- One color from the palette: ink on paper, white on navy, night or blue.
- Clear space: the cap height of the B on every side. The symbol alone keeps a quarter of its height.
- Smallest logo is 15px tall. Below that, use the symbol. Smallest symbol is 16px.
- In documents the logo sits small in the top-left corner (13pt tall on the one pager).
- Do not stretch, recolor, outline, shadow or place it on a busy image.
- Do not put the logo inside a line of body text. Write the word "Bluefyn" there.

## Graphics

There is no photography, no stock imagery and no illustration of people. The imagery is the product made
visible, all built from one material: Arial digits, records and verdict marks.

- **Digit field.** Rows of digits that drift in short runs, with records set into them.
- **Records and marks.** A record is two to four short lines in Arial capitals ("TX-001 / CT-001:4.2").
  Its last line is a verdict mark: CHECKING in blue, MATCH in green, OFF CONTRACT in red.
- **Record texture.** The check log, line after line, very small and low contrast, on navy. Used on the
  header and footer of the one pager. In a PDF it is placed as an image (`assets/texture.png`), not as text,
  so its words do not show up when someone searches or copies the page.
- **Plate stack.** Bluefyn as the top plate above the tools it reads. Square plates in true isometric.
- **Cube of records.** One digit field on three equal faces. Draw it whole and boxy. Never stretch or crop it.
- **Scan band, ellipses, stream.** From the posters. See `graphics.md`.
- **Grain.** A very fine grain (specks of about 0.4pt) on every ground, light specks on dark and ink specks
  on paper. It should be barely visible at normal zoom.

Use one hero graphic per page and keep it quiet enough that type reads first. A bright graphic on a dark
page is too loud: on dark grounds, graphics use charcoal faces and gray digits.

## Page layout

- US Letter, 36pt side margins, three columns of 172pt with 12pt gaps (left edges at 36, 220 and 404pt).
  Every block starts on one of those edges. Blocks that span columns still start on them.
- The page opens as a poster: navy header with the logo small in the corner, proof points on the left and
  the headline on the right.
- The body is paper (light) or ink (dark). Sections are separated by space and hairlines, not by boxes.
- The page closes with a full-width navy footer: the next step on the left, the contact in a tag on the right.
- Square corners everywhere. Hairlines are 0.5pt; the rule above a column heading is 0.75pt.
- Space between sections is even down the page (13 to 22pt depending on how much content there is).
- Figures are set as a ledger (figure, then what it means), not as a row of cards.
- Tables use the grid: the first column is one grid column wide, the second takes the rest.

## What to leave out

These are what make a page look machine made. They come from the Figma guide's things to avoid and from
design review.

- Em dashes and en dashes as punctuation. Middle dots, bullets and arrows as separators.
- Letterspaced capital labels above sections. Capitals belong to records and marks.
- Pill chips. Rounded, tinted cards. Rows of identical metric cards.
- Shadows, glows, gradients and gradient text. Side-stripe borders.
- Colored full-width bands used only to shout one line. The answer line is plain text with a hairline under it.
- Bold for emphasis. Second accent colors. Green or red as decoration.
- Emoji, decorative icons, stock photos.
- Gray body text on paper. If people need to read it, it is ink.
- Exclamation points and hype words.

## What the review taught us

These came out of reviewing the first one pager, in this order. They explain why the design is the way it
is, and they are the first things to check on anything new.

1. Keep the author's text. Change only the formatting.
2. Blocks must sit on shared edges. Content that floats off the grid reads as misaligned.
3. The cube must be boxy and whole, never stretched.
4. It is a sales piece. The headline, the proof points, the answer and the next step are the loudest things.
5. Easy to read and investor friendly: ink body text, 9pt or larger, calm hierarchy.
6. A full-width footer closes the page.
7. No colored band for the answer line. No logo inside body text. No rule under the header.
8. Bright graphics on a dark page are too much. Tone them down or leave them out.
9. A fine grain on both light and dark grounds.

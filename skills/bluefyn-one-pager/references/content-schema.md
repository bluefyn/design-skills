# Content file

The builder reads one JSON file. `examples/acme.json` is a complete, working example. Only `headline` and
`next` are required. Leave out any other section and the page closes up around it.

Lengths below are what fits comfortably at the fixed type sizes. They are guides, not hard limits. The
build report is the real check.

## Top level

| Field | Required | What it is | Fits |
| --- | --- | --- | --- |
| `partner` | no | The company the page is for. Shown beside the logo as "Bluefyn × Acme Pay" and used in the file name. | 1 to 3 words. It shares the top line with `meta`, and the build reports it if the two collide. |
| `meta` | no | Short strings at the top right, such as `["Prepared for Acme Pay", "November 2026"]`. "Prepared for <partner>" is standard and may be added. | 0 to 2 items, about 45 characters in total |
| `mode` | no | `"light"`, `"dark"` or `"both"`. `--mode` on the command line overrides it. Default `light`. | |
| `title` | no | PDF document title. Default "Bluefyn for <partner>". | |
| `headline` | yes | The main claim, set at 27pt on the navy header. | 45 to 75 characters for two or three lines. Over about 75 it usually runs four, which the build reports as a problem. |
| `lede` | no | One paragraph under the headline. | up to about 300 characters, four lines |

## `told`: the proof points, left of the headline

```json
"told": {
  "label": "What your team told us",
  "rows": [ { "figure": "40+", "text": "vendor invoices a week, reviewed by hand" } ]
}
```

- Two to four rows. Three is the approved layout.
- `figure`: a number or two or three words, up to about 12 characters ("$120K", "Each launch").
- `text`: up to about 50 characters, two lines.
- Splitting an author's sentence: the figure is the number with its unit ("4 days", "$1.2M"), or the
  number alone when the noun reads better in the text ("9" and "processors, each with its own fee
  schedule"). The text is the rest, unchanged. Do not start the text with a capital; it continues the figure.
- With no `told`, the headline takes the full width.

## `with`: the answer

```json
"with": { "label": "With Bluefyn", "figure": "Every bill", "text": "checked against contract on both sides, continuously" }
```

- `figure`: up to about 12 characters. It sits under the proof points, as the last figure in that column.
- `text`: one line, up to about 55 characters. It starts under the headline and continues the figure, so
  it starts in lower case ("Every bill" then "checked against contract ...").

## `sides`: two columns

```json
"sides": {
  "label": "Both sides of Acme's economics",
  "note": "Read-only to start. Bluefyn never touches funds",
  "columns": [
    { "title": "What Acme pays", "mark": "Money out", "sub": "Processors, banks, ...", "items": ["...", "...", "..."] },
    { "title": "What Acme bills", "mark": "Money in", "sub": "Customers on custom, ...", "items": ["...", "...", "..."] }
  ]
}
```

- Exactly two columns.
- `label` sits over the first column and `note` over the second. Both are optional. A `note` with no
  `label` moves over the first column. If the author gave no label, you can propose one ("Both sides of
  <partner>'s economics") and say you added it.
- `note` must fit on one line: up to about 48 characters when there is a `layer` card, longer without one.
  The build reports it if it is too wide.
- `title`: up to about 16 characters when the column has a `mark`, about 26 without. The approved pattern
  is "What <partner> pays" and "What <partner> bills", which fits a partner name of up to about five
  letters. For a longer name, keep both columns the same shape and pick one: write to the reader ("What
  you pay", "What you bill"), drop "What" ("Northwind pays"), use a short form of the name the author
  agrees to, or drop the marks from both columns. The build reports a title that wraps.
- `mark`: optional, one or two words. Write it in normal case; it is set as a blue capitals mark.
- `sub`: optional, up to two lines (about 70 characters).
- `items`: three per column is the approved layout; two to five work. Each up to about 65 characters. Keep
  the two columns the same length so they end together.

## `layer`: the dark card beside the two columns

```json
"layer": { "label": "A layer above", "stack": ["Bluefyn", "Spend", "ERP", "CRM"], "text": "Works alongside your spend tool, ERP and CRM. Nothing ripped out or replaced." }
```

- `stack`: the first name is always "Bluefyn", the top plate. Then the two or three tools it sits above,
  each one word of up to about 10 characters ("Salesforce" fits). Shorten a two-word product to its
  first word on the plate ("Stripe Billing" becomes "Stripe") and use the full name in `text`.
- `text`: up to about 80 characters, three lines. It can name the same tools as the stack; the approved
  page does.
- With no `layer`, the two columns widen to fill the row.

## `flags`: a two-column table

```json
"flags": { "label": "What our agents flag, before your team has to look", "rows": [["A vendor charges above contract", "The amount, the clause and the evidence, ready to dispute"]] }
```

- Each row is `[trigger, response]`. Trigger up to about 38 characters, response up to about 75.
- Two to five rows. Each row costs about 19pt of height. With fewer than two real rows, leave the section out.

## `closing`: up to three short blocks

```json
"closing": [
  { "label": "Who we are", "text": "..." },
  { "label": "Why now", "text": "..." },
  { "label": "Also included", "items": ["Treasury forecasting", "Account visibility"] }
]
```

- One to three blocks. Each has a `label` and either `text` or `items`. Blocks sit on the three page
  columns, one column each. A single block spans two columns.
- `text`: up to about 150 characters per block (four or five lines), or about 300 for a single block.
- `items`: up to five short lines.

## `next`: the footer

```json
"next": { "label": "Next step", "text": "A discovery call this week to map your vendor and customer contracts. ...", "contact": { "name": "Alex Morgan", "role": "Partnerships, Bluefyn", "email": "alex@example.com" } }
```

- `text`: two lines, up to about 120 characters. This is the call to action, so make it one concrete step.
- `contact` is optional. `role` and `email` share one line, about 45 characters together. The build reports
  it if they do not fit.

## Output names

Files are named `one-pager-<partner>-<mode>` with the partner in lower case and hyphens. `--name <stem>`
sets the stem yourself, for example `--name acme-proposal` for a second version to compare.

## What the builder does to your text

- Escapes it for HTML. Write plain text, with no markup.
- Keeps hyphenated words such as "usage-based" on one line.
- Sets marks in capitals and figures with tabular numbers.
- Leaves quotes and apostrophes as you typed them.
- Warns about em and en dashes, middle dots, bullets, arrows, exclamation points and strings typed in
  capitals. It does not change them; you fix them with the author.

## Spacing presets

`--density auto` (the default) tries `roomy`, `regular`, then `tight` and keeps the first that leaves the
required room above the footer. If a lot of room is left, it adds some between the sections (shown as
`stretch` in the report). With `--mode both`, the dark page reuses the spacing chosen for the light page.
Pass `--density regular` to force a preset.

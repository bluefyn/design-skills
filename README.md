# Bluefyn design skills

Four skills for [Claude Code](https://claude.com/claude-code). Two of them make documents and pages in
the Bluefyn brand. The other two make writing plainer.

| Skill | What it does | How to start it |
| --- | --- | --- |
| `bluefyn-design` | Holds the brand book (colors, type, logo, graphics, layout rules, what to leave out) and a design method for layout and copy. Claude uses it for any Bluefyn-branded piece. | Ask for a branded page, slide, poster or PDF, or type `/bluefyn-design` |
| `bluefyn-one-pager` | Turns any text into a one-page PDF in the Bluefyn brand, light or dark. | Ask for a one pager, or type `/bluefyn-one-pager` |
| `bluefyn-unslop` | Removes AI tells from prose, such as em dashes, filler and hype words. | Type `/bluefyn-unslop`, or ask for a final pass on some writing |
| `bluefyn-bro` | Restates Claude's last answer in plain language. | Type `/bluefyn-bro` |

## Install

You need:

- Claude Code
- Python 3 (the system Python on macOS works)
- Chrome, Chromium, Edge or Brave, which the one pager skill uses to print the PDF

The skills need no Python packages and install nothing else.

1. Clone the repo.

   ```bash
   git clone https://github.com/bluefyn/design-skills.git
   ```

2. Run the installer from the repo folder. It copies the four skills into `~/.claude/skills`.

   ```bash
   cd design-skills && ./install.sh
   ```

3. Start a new Claude Code session and type `/bluefyn`. The four skills appear in the menu.

To install into one repo instead, so that everyone who works in it gets the skills:

```bash
./install.sh --project /path/to/repo
```

The installer skips a skill that is already installed. To update, pull the repo and run the installer
with `--force`:

```bash
git pull && ./install.sh --force
```

To uninstall, delete the four `bluefyn-*` folders from `~/.claude/skills`.

### Install as a plugin

The repo is also a Claude Code plugin marketplace. In Claude Code, run:

```
/plugin marketplace add bluefyn/design-skills
/plugin install bluefyn@bluefyn-design-skills
```

Claude Code puts the plugin name in front of plugin skills, so the commands become `/bluefyn:bluefyn-one-pager`,
`/bluefyn:bluefyn-bro` and so on. Use `install.sh` if you want the short names.

## Prompts to try

One pagers:

> Make a one pager for Acme Pay from these call notes: ...

> Here is our old sales PDF (path). Turn it into a one pager in our brand, light and dark.

> Turn this email thread into a one pager I can send to their CFO. Keep my numbers exactly.

> The one pager is 20 points too tall. Show me two ways to cut it.

> I want a bigger headline and the flags table above the two columns, just for this deal. Make me a local kit and change it there.

Other design work:

> Design a title slide for our board deck in the Bluefyn brand.

> Restyle this landing page section so it looks like us. Use the brand tokens.

> What does the brand say about using green and red?

> Draw the cube of records as an SVG, 300 points wide.

Writing:

> /bluefyn-unslop this PR description

> Write the release note, then run it through bluefyn-unslop.

> /bluefyn-bro

## Build a one pager by hand

The one pager skill is a script and a content file. You can run it without Claude:

```bash
python3 skills/bluefyn-one-pager/scripts/one_pager.py skills/bluefyn-one-pager/examples/acme.json --out ./out --mode both
```

It writes `one-pager-acme-pay-light.pdf` and `one-pager-acme-pay-dark.pdf`, a PNG preview of each, and a
report that says whether the content fits on the page. Copy `acme.json`, change the text and build again.
[content-schema.md](skills/bluefyn-one-pager/references/content-schema.md) lists every field.

Acme Pay is a made-up company. The figures in the example are made up too.

## Tune the template for yourself

The template in the skill is the shared design. To change the layout for your own page, make a local kit:

```bash
python3 skills/bluefyn-one-pager/scripts/one_pager.py init ./one-pager-kit
```

The kit is a folder with its own copy of the template, the brand code, the assets and the example
content. Edit `one_pager.py` in the kit (the `CSS` block holds every size, color and gap) and rebuild:

```bash
python3 ./one-pager-kit/one_pager.py ./one-pager-kit/content.json --out ./one-pager-kit/out --mode both
```

Your changes stay in the kit. The installed skills do not change.

## What is in the repo

```
skills/
  bluefyn-design/
    SKILL.md                      how Claude designs for Bluefyn
    references/brand.md           the brand rules
    references/brand-book.pdf     the illustrated brand book
    references/frontend-design.md the design method
    references/graphics.md        the brand drawings and how to draw them
    scripts/brand.py              colors, logo and drawings as SVG
    assets/                       logo, Geist font, tokens.css, grain and texture images
  bluefyn-one-pager/
    SKILL.md                      how Claude turns text into a one pager
    references/content-schema.md  every field of the content file and how much text fits
    scripts/one_pager.py          content file in, PDF and preview out
    examples/                     the Acme Pay sample, as JSON, PDF and image
  bluefyn-unslop/SKILL.md
  bluefyn-bro/SKILL.md
install.sh
```

`bluefyn-one-pager` reads its colors, logo and font from `bluefyn-design`, so install them together.

## Credits and licenses

- The Bluefyn name, logo and brand book belong to Bluefyn. They are here so that work made for Bluefyn
  looks right.
- `references/frontend-design.md` is Anthropic's `frontend-design` skill, under the Apache License 2.0.
  The license is in `skills/bluefyn-design/LICENSE-frontend-design.txt`.
- `bluefyn-unslop` and `bluefyn-bro` come from pstack by Lauren Tan, under the MIT license.
  `bluefyn-unslop` has our edits. See `THIRD-PARTY.md`.
- Geist is under the SIL Open Font License 1.1. The license is next to the font.

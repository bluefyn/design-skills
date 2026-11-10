# Bluefyn design workspace

This folder is for making Bluefyn-branded pieces on this computer: one pagers, PDFs, slides, social
images and pages. The installer from github.com/bluefyn/design-skills made it.

## What is here

| Path | What it is |
| --- | --- |
| `.claude/skills/bluefyn-design/` | The brand book, the design method, `scripts/brand.py` and the brand files |
| `.claude/skills/bluefyn-one-pager/` | The one pager template and its builder |
| `.claude/skills/bluefyn-unslop/`, `bluefyn-bro/` | The two writing skills |
| `brand/` | The brand files, in plain view: `logo/`, `avatars/`, `banners/`, `patterns/`, `fonts/`, `tokens.css`, `brand-book.pdf`. These are the same files the skills read, not a second copy |
| `content/` | Content files for one pagers. `acme.json` is a made-up example |
| `out/` | Everything that gets built |
| `build.sh` | Builds a one pager: `./build.sh content/<name>.json` |

## How to work here

- Use the bluefyn-design skill for any branded piece. Read its `SKILL.md` and `references/brand.md` once
  per session before you design.
- For a one pager, use the bluefyn-one-pager skill. Write the content file in `content/`, run
  `./build.sh content/<name>.json`, open the PNG in `out/` and fix what the report flags.
- Take logos, profile pictures, banners and patterns from `brand/`. The bluefyn-design skill's
  `references/assets.md` says which file is for what. Do not redraw, recolor or re-export them.
- For any other piece (a slide, a poster, a social image), lay it out in HTML with `brand/tokens.css`
  and `scripts/brand.py`, keep the source in `work/<piece>/`, and print the result into `out/`.
- Geist must be in every file you make. Load it from `brand/fonts/` or embed it with
  `brand.geist_face()`.
- Put every finished file in `out/`.
- Do not edit `.claude/skills/` or `brand/`. The installer replaces them on update. To change the one
  pager layout for one job, make a kit and edit that:
  `python3 .claude/skills/bluefyn-one-pager/scripts/one_pager.py init kits/<name>`
- Run copy you wrote through the bluefyn-unslop skill before you hand a piece over.
- Content in this folder can name real prospects and their figures. Keep it on this computer. Do not
  publish, upload or push it unless the person asks.

## What the builds need

Python 3 and Chrome, Chromium, Edge or Brave. No Python packages.

## Update

    curl -fsSL https://raw.githubusercontent.com/bluefyn/design-skills/main/install.sh | sh -s -- --workspace . --force

This replaces the skills, `brand/` and `build.sh`. It leaves this file, `content/`, `out/` and everything
else alone.

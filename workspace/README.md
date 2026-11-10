# Bluefyn design workspace

A folder where Claude makes Bluefyn-branded pieces on your computer. It holds the design skills, the
brand files and a builder for one pagers.

## Start

Open this folder in Claude Code, or run `claude` in it, and ask:

> Make a one pager for Acme Pay from these call notes: ...

> Give me the white logo as a PNG and the X header on the night ground.

> Design a title slide for our board deck with the tower pattern as the background.

> Dream up three different designs for the Acme Pay one pager.

> Here are my call notes with Northwind. Write the one pager copy.

Finished files land in `out/`.

## Build without Claude

    ./build.sh content/acme.json

This writes a light and a dark PDF, a PNG preview of each and the HTML into `out/`. Copy
`content/acme.json`, change the text and build again. It needs Python 3 and Chrome, Chromium, Edge or
Brave.

## What is in the folder

    brand/        logo, profile pictures, banners, patterns, the Geist font and the brand book
    content/      the text of each one pager, as JSON
    dreams/       three-design explorations, one folder each
    out/          what gets built
    build.sh      builds a one pager
    CLAUDE.md     tells Claude how to work here
    .claude/      the six skills (a hidden folder)

`brand/` and `.claude/skills/` come from the installer and are replaced on update, so keep your own
files out of them.

## Update

    curl -fsSL https://raw.githubusercontent.com/bluefyn/design-skills/main/install.sh | sh -s -- --workspace . --force

Your `content/`, `dreams/`, `out/`, `CLAUDE.md` and this file stay as they are.

#!/usr/bin/env python3
"""Checks Bluefyn copy: a one pager content file, or any plain text.

    python3 copy_check.py content.json          check a content file against the schema and the voice
    python3 copy_check.py --text draft.md       check any prose (an email, a doc, a post) against the voice
    python3 copy_check.py --text -              read the prose from stdin

It prints one line per finding, as `<where> problem: ...` or `<where> note: ...`, then a summary.
Exit code 0: nothing to fix. 2: problems found. 1: the file could not be read or is not valid JSON.
Notes never change the exit code.

Python standard library only. No browser and no network.
"""
import json
import re
import sys

# ------------------------------------------------------------------ voice
PUNCT = {
    "—": "an em dash (use a comma or a period)",
    "–": "an en dash (use a comma, a period or 'to')",
    "·": "a middle dot",
    "•": "a bullet character",
    "…": "an ellipsis character",
    "→": "an arrow", "←": "an arrow", "⇒": "an arrow", "➔": "an arrow", "->": "an arrow",
    "!": "an exclamation point",
    "‘": "a curly quote (use a straight one)", "’": "a curly quote (use a straight one)",
    "“": "a curly quote (use a straight one)", "”": "a curly quote (use a straight one)",
}
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️‍]")

# Words that read as generated or as hype. Each maps to what to do instead.
WORDS = {
    "additionally": "start with 'Also', or drop it", "crucial": "say why it matters", "delve": "use 'look at'",
    "enduring": "say how long", "enhance": "say what changes", "foster": "say what happens",
    "fostering": "say what happens", "garner": "use 'get'", "interplay": "name the two things",
    "intricate": "say what is involved", "landscape": "name the market or the tools", "pivotal": "say why",
    "showcase": "use 'show'", "showcasing": "use 'showing'", "tapestry": "cut it", "testament": "cut it",
    "underscore": "use 'show'", "underscores": "use 'shows'", "vibrant": "cut it", "leverage": "use 'use'",
    "leverages": "use 'uses'", "leveraging": "use 'using'", "utilize": "use 'use'", "utilizes": "use 'uses'",
    "facilitate": "use 'help'", "numerous": "use 'many' or the number", "seamless": "say what does not break",
    "seamlessly": "say what does not break", "robust": "say what it survives", "cutting-edge": "cut it",
    "game-changer": "say what changes", "game-changing": "say what changes", "revolutionize": "say what changes",
    "revolutionary": "cut it", "unlock": "say what they can now do", "unlocks": "say what they can now do",
    "empower": "say what they can do", "empowers": "say what they can do", "best-in-class": "cut it",
    "world-class": "cut it", "synergy": "cut it", "synergies": "cut it", "holistic": "say what it covers",
    "next-generation": "cut it", "state-of-the-art": "cut it", "supercharge": "say by how much",
    "effortless": "say what the work is", "effortlessly": "say what the work is", "unparalleled": "cut it",
    "paradigm": "cut it", "journey": "name the steps", "elevate": "say what improves", "streamlined": "say what is removed",
    "harness": "use 'use'", "harnessing": "use 'using'", "ecosystem": "name the tools", "solution": "name what it does",
    "solutions": "name what they do", "innovative": "cut it", "transformative": "say what changes",
    "dive": "use 'look at'", "realm": "cut it", "navigate": "say what they do", "robustly": "cut it",
}
PHRASES = {
    "in order to": "use 'to'", "due to the fact that": "use 'because'", "it is important to note": "cut it",
    "it's important to note": "cut it", "serves as": "use 'is'", "stands as": "use 'is'", "boasts": "use 'has'",
    "not just": "state the point directly", "not only": "state the point directly",
    "at the end of the day": "cut it", "take it to the next level": "say what improves",
    "we're excited": "cut it", "we are excited": "cut it", "i hope this helps": "cut it",
    "let me know if": "cut it", "feel free to": "cut it", "reach out": "use 'write' or 'call'",
    "a wide range of": "name them or use 'many'", "a variety of": "name them or use 'several'",
    "plays a key role": "say what it does", "plays a crucial role": "say what it does",
    "peace of mind": "say what risk goes away", "the future of": "cut it",
}
ALL_CAPS_RUN = re.compile(r"\b[A-Z]{2,}(?:\s+[A-Z]{2,})+\b")
MARK_WORDS = re.compile(r"\b(?:OFF CONTRACT|MONEY OUT|MONEY IN)\b")     # the brand's mark words, set in capitals
LEAD_IN = re.compile(r"^\*\*[^*]+[.?]\*\*\s*")                     # "**Name.** detail", allowed by the voice


def voice(where, text, out, kind="prose"):
    """Findings for one string. kind is "prose", "fragment" (list item, cell, figure) or "label"."""
    for ch, name in PUNCT.items():
        if ch in text:
            out.append((where, "problem", f"contains {name}"))
    if EMOJI.search(text):
        out.append((where, "problem", "contains an emoji"))
    low = text.lower()
    for word in re.findall(r"[a-z][a-z\-']+", low):
        if word in WORDS:
            out.append((where, "problem", f"'{word}': {WORDS[word]}"))
    for phrase, fix in PHRASES.items():
        if phrase in low:
            out.append((where, "problem", f"'{phrase}': {fix}"))
    if ALL_CAPS_RUN.search(MARK_WORDS.sub("", text)):
        out.append((where, "problem", "words typed in capitals; write them in normal case"))
    if "**" in text or "__" in text:
        out.append((where, "problem", "markdown bold; write plain text"))
    if "  " in text:
        out.append((where, "note", "two spaces in a row"))
    if text != text.strip():
        out.append((where, "note", "space at the start or the end"))
    words = text.split()
    if kind in ("fragment", "label") and text.rstrip().endswith("."):
        out.append((where, "problem", "ends with a period; labels, list items and cells do not"))
    if kind == "label" and len(words) >= 3 and all(w[:1].isupper() for w in words if w[:1].isalpha()):
        out.append((where, "problem", "Title Case; labels are sentence case"))
    if kind == "prose":
        for sentence in re.split(r"(?<=[.?])\s+", text):
            n = len(sentence.split())
            if n > 30:
                out.append((where, "note", f"a sentence of {n} words; split it"))


# ----------------------------------------------------------------- schema
def length(where, text, limit, out):
    """The schema's lengths are guides; the one pager build is the real fit check. Slightly over is a
    note, clearly over (more than 15 percent) is a problem."""
    if len(text) > limit * 1.15:
        out.append((where, "problem", f"{len(text)} characters, fits about {limit}"))
    elif len(text) > limit:
        out.append((where, "note", f"{len(text)} characters, about {limit} fits; the build will tell"))


def need(obj, key, where, out):
    if not isinstance(obj, dict) or not obj.get(key):
        out.append((where, "problem", f"'{key}' is required"))
        return None
    return obj[key]


def check_content(c):
    out = []
    if not isinstance(c, dict):
        return [("content", "problem", "the file must hold one JSON object")]
    known = {"partner", "meta", "mode", "title", "headline", "lede", "told", "with", "sides", "layer", "flags",
             "closing", "next"}
    for key in c:
        if key not in known:
            out.append((key, "problem", "not a field of the one pager schema"))

    if c.get("partner"):
        if len(c["partner"].split()) > 3:
            out.append(("partner", "problem", "more than three words"))
        voice("partner", c["partner"], out, "label")
    meta = c.get("meta") or []
    if len(meta) > 2:
        out.append(("meta", "problem", f"{len(meta)} items, fits two"))
    if sum(len(m) for m in meta) > 45:
        out.append(("meta", "problem", f"{sum(len(m) for m in meta)} characters in all, fits about 45"))
    for i, m in enumerate(meta):
        voice(f"meta[{i}]", m, out, "label")
    if c.get("mode") not in (None, "light", "dark", "both"):
        out.append(("mode", "problem", "use light, dark or both"))

    head = need(c, "headline", "content", out)
    if head:
        if len(head) > 75:
            out.append(("headline", "problem", f"{len(head)} characters; over about 75 it runs four lines"))
        elif len(head) < 45:
            out.append(("headline", "note", f"{len(head)} characters; under about 45 it may set on one line"))
        voice("headline", head, out)
    if c.get("lede"):
        length("lede", c["lede"], 300, out)
        voice("lede", c["lede"], out)

    told = c.get("told")
    if told:
        if told.get("label"):
            voice("told.label", told["label"], out, "label")
        rows = need(told, "rows", "told", out) or []
        if not 2 <= len(rows) <= 4:
            out.append(("told.rows", "problem", f"{len(rows)} rows; two to four fit, three is the approved layout"))
        for i, r in enumerate(rows):
            w = f"told.rows[{i}]"
            fig, text = need(r, "figure", w, out), need(r, "text", w, out)
            if fig:
                length(w + ".figure", fig, 12, out)
                voice(w + ".figure", fig, out, "fragment")
            if text:
                length(w + ".text", text, 50, out)
                voice(w + ".text", text, out, "fragment")
                if text[:1].isupper() and not re.match(r"[A-Z]{2,}|[A-Z][a-z]+ [A-Z]", text):
                    out.append((w + ".text", "note", "starts with a capital; it continues the figure, so start lower case"))

    w_ = c.get("with")
    if w_:
        for key, lim in (("label", 30), ("figure", 12), ("text", 55)):
            v = need(w_, key, "with", out)
            if v:
                length(f"with.{key}", v, lim, out)
                voice(f"with.{key}", v, out, "label" if key == "label" else "fragment")
        if w_.get("text", "")[:1].isupper():
            out.append(("with.text", "note", "starts with a capital; it continues the figure, so start lower case"))

    s = c.get("sides")
    layer = c.get("layer")
    if s:
        for key in ("label", "note"):
            if s.get(key):
                voice(f"sides.{key}", s[key], out, "label")
        if s.get("note"):
            length("sides.note", s["note"], 48 if layer else 90, out)
        cols = need(s, "columns", "sides", out) or []
        if len(cols) != 2:
            out.append(("sides.columns", "problem", f"{len(cols)} columns; it takes exactly two"))
        counts = []
        for i, col in enumerate(cols):
            w = f"sides.columns[{i}]"
            title = need(col, "title", w, out)
            if title:
                length(w + ".title", title, 16 if col.get("mark") else 26, out)
                voice(w + ".title", title, out, "label")
            if col.get("mark"):
                if len(col["mark"].split()) > 2:
                    out.append((w + ".mark", "problem", "one or two words"))
                voice(w + ".mark", col["mark"], out, "label")
            if col.get("sub"):
                length(w + ".sub", col["sub"], 70, out)
                voice(w + ".sub", col["sub"], out, "fragment")
            items = need(col, "items", w, out) or []
            counts.append(len(items))
            if not 2 <= len(items) <= 5:
                out.append((w + ".items", "problem", f"{len(items)} items; two to five fit, three is the approved layout"))
            for j, item in enumerate(items):
                length(f"{w}.items[{j}]", item, 65, out)
                voice(f"{w}.items[{j}]", item, out, "fragment")
        if len(set(counts)) > 1:
            out.append(("sides.columns", "note", f"the columns have {counts[0]} and {counts[1]} items; even them out"))

    if layer:
        if layer.get("label"):
            voice("layer.label", layer["label"], out, "label")
        stack = need(layer, "stack", "layer", out) or []
        if stack and stack[0] != "Bluefyn":
            out.append(("layer.stack", "problem", "the first plate is always 'Bluefyn'"))
        if not 3 <= len(stack) <= 4:
            out.append(("layer.stack", "problem", f"{len(stack)} plates; Bluefyn and two or three tools fit"))
        for i, name in enumerate(stack):
            if len(name.split()) > 1 or len(name) > 10:
                out.append((f"layer.stack[{i}]", "problem", "one word of up to 10 characters; use the full name in the text"))
        if layer.get("text"):
            length("layer.text", layer["text"], 80, out)
            voice("layer.text", layer["text"], out)

    f = c.get("flags")
    if f:
        if f.get("label"):
            voice("flags.label", f["label"], out, "label")
        rows = need(f, "rows", "flags", out) or []
        if not 2 <= len(rows) <= 5:
            out.append(("flags.rows", "problem", f"{len(rows)} rows; two to five fit"))
        for i, r in enumerate(rows):
            if not (isinstance(r, list) and len(r) == 2):
                out.append((f"flags.rows[{i}]", "problem", "each row is [trigger, response]"))
                continue
            length(f"flags.rows[{i}][0]", r[0], 38, out)
            length(f"flags.rows[{i}][1]", r[1], 75, out)
            voice(f"flags.rows[{i}][0]", r[0], out, "fragment")
            voice(f"flags.rows[{i}][1]", r[1], out, "fragment")

    blocks = c.get("closing") or []
    if len(blocks) > 3:
        out.append(("closing", "problem", f"{len(blocks)} blocks; it takes up to three"))
    for i, blk in enumerate(blocks):
        w = f"closing[{i}]"
        label = need(blk, "label", w, out)
        if label:
            voice(w + ".label", label, out, "label")
        if blk.get("text"):
            length(w + ".text", blk["text"], 300 if len(blocks) == 1 else 150, out)
            voice(w + ".text", blk["text"], out)
        elif blk.get("items"):
            if len(blk["items"]) > 5:
                out.append((w + ".items", "problem", f"{len(blk['items'])} items; up to five fit"))
            for j, item in enumerate(blk["items"]):
                voice(f"{w}.items[{j}]", item, out, "fragment")
        else:
            out.append((w, "problem", "needs 'text' or 'items'"))

    n = need(c, "next", "content", out)
    if n:
        if n.get("label"):
            voice("next.label", n["label"], out, "label")
        text = need(n, "text", "next", out)
        if text:
            length("next.text", text, 120, out)
            voice("next.text", text, out)
        contact = n.get("contact")
        if contact:
            need(contact, "name", "next.contact", out)
            line = len(contact.get("role", "")) + len(contact.get("email", ""))
            if line > 45:
                out.append(("next.contact", "problem", f"role and email are {line} characters together, fit about 45"))

    words = len(" ".join(strings(c, skip=("mode", "title"))).split())
    if words > 400:
        out.append(("content", "problem", f"{words} words with labels; the page holds about 380 at most"))
    elif words > 340:
        out.append(("content", "note", f"{words} words with labels, near the most a page holds; build and read the fit"))
    elif words < 120:
        out.append(("content", "note", f"{words} words; the page will look thin, so suggest the missing sections"))
    return out, words


def strings(node, skip=(), path=""):
    if isinstance(node, str):
        if path not in skip:
            yield node
    elif isinstance(node, list):
        for item in node:
            yield from strings(item, skip, path)
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from strings(value, skip, key if not path else f"{path}.{key}")


def check_text(text):
    out = []
    for i, para in enumerate(p for p in re.split(r"\n\s*\n", text) if p.strip()):
        lines = para.strip().splitlines()
        first = lines[0].strip()
        if re.match(r"#{1,6}\s", first):
            heading = re.sub(r"^#{1,6}\s+", "", first)
            voice(f"paragraph {i + 1} heading", heading, out, "label")
            lines = lines[1:]
        body = " ".join(LEAD_IN.sub("", re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", ln).strip()) for ln in lines)
        if body:
            voice(f"paragraph {i + 1}", body, out)
    return out


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    if argv[0] == "--text":
        if len(argv) < 2:
            print("--text needs a file, or - for stdin", file=sys.stderr)
            return 1
        try:
            text = sys.stdin.read() if argv[1] == "-" else open(argv[1], encoding="utf-8").read()
        except OSError as err:
            print(f"cannot read {argv[1]}: {err}", file=sys.stderr)
            return 1
        found, summary = check_text(text), f"{len(text.split())} words"
    else:
        try:
            with open(argv[0], encoding="utf-8") as fh:
                content = json.load(fh)
        except (OSError, ValueError) as err:
            print(f"cannot read {argv[0]}: {err}", file=sys.stderr)
            return 1
        result = check_content(content)
        if isinstance(result, list):
            found, summary = result, ""
        else:
            found, words = result
            summary = f"{words} words on the page"
    problems = [f for f in found if f[1] == "problem"]
    for where, level, msg in found:
        print(f"[{where}] {level}: {msg}")
    print(f"{summary}, {len(problems)} problem(s), {len(found) - len(problems)} note(s): "
          f"{'clean' if not problems else 'fix the problems above'}")
    return 2 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

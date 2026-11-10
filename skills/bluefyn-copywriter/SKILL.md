---
name: bluefyn-copywriter
description: Turn any text into Bluefyn copy. It rewrites notes, call summaries, emails, transcripts, old decks and long documents into the one pager content file (the JSON that bluefyn-one-pager and bluefyn-dream build from), and it rewrites any prose into plain, professional business text with no em dashes, emoji, hype or other AI patterns. Use it before building a one pager or a dream from raw material, when someone asks to "write the copy", "make this a one pager", "clean up this text", "make it sound professional", or when a draft needs the Bluefyn voice.
---

# Bluefyn copywriter

This skill writes the words. It has two jobs:

1. **Content for a page.** Any source in, one content file out, in the bluefyn-one-pager schema. The
   bluefyn-one-pager and bluefyn-dream skills build from that file.
2. **Plain business prose.** Any draft in (an email, a post, a doc, a PR description), the same message out
   in the Bluefyn voice.

Both end with the checker, which catches what the voice leaves out:

```bash
python3 <this skill's folder>/scripts/copy_check.py content.json
python3 <this skill's folder>/scripts/copy_check.py --text draft.md
```

## The voice

Read `references/voice.md` once per session. In short:

- Plain words and short sentences. One idea per sentence. Active voice, with the actor named.
- Say what happens, with the number when there is one. "Checks every invoice against its contract", not
  "streamlines invoice workflows".
- Professional and calm. The reader works in finance and payments and knows the terms. No hype, no
  exclamation points, no emoji, no excited openers.
- Commas and periods. No em dashes or en dashes, no arrows, no bullets typed as characters, no ellipsis
  character, straight quotes.
- Sentence case for every heading and label.
- Every fact comes from the source. Never invent a figure, a customer, a quote or a result.

The bluefyn-unslop skill has the full list of patterns. If it is installed, run the final text through
it as well.

## Job 1: content for a page

### Read the source and find the page in it

A one pager answers eight questions, and each has a field:

| The reader asks | Field |
| --- | --- |
| What is this and why should I care? | `headline`, `lede` |
| What do you know about us? | `told` |
| What do you do about it? | `with` |
| How, concretely? | `sides` |
| Does it fit what we have? | `layer` |
| What will it catch? | `flags` |
| Who are you, why now, what else? | `closing` |
| What happens next? | `next` |

Only `headline` and `next` are required. Leave out a section the source says nothing about rather than
filling it with something plausible. If the page cannot work without something the source lacks (who it
is for, the next step, the contact), ask once, with all your questions together.

The field lengths are in bluefyn-one-pager `references/content-schema.md`. Read it before you write.
`../bluefyn-one-pager/examples/acme.json` is a complete file to copy.

### Decide how much you may change

- **A finished draft or an old one pager.** The words are the author's. Keep wording and numbers. Fix only
  punctuation the brand leaves out, split rough separators into fields, and move sentences to the field
  they fit. List every change when you hand over.
- **Raw material.** Notes, a transcript or a long document. Write the copy in the voice, from the
  source's facts. Prefer the source's own phrases, cut down. Keep every figure's value; you may tidy how
  it is written ("$85k" becomes "$85K").

### Write each field

- `headline`: one claim about what changes for the reader, 45 to 75 characters. Not a slogan.
- `lede`: one paragraph about their situation, then what Bluefyn does about it. Up to 300 characters.
- `told.rows`: the figure is a number with its unit or two or three words ("40+", "$120K", "Each launch").
  The text continues it in lower case.
- `with`: a short figure and one line in lower case that continues it.
- `sides`: two parallel columns with the same number of items. Items are fragments without a final
  period.
- `layer.stack`: "Bluefyn" first, then the tools by one-word names.
- `flags.rows`: a trigger and what the reader gets, each a fragment.
- `closing`: up to three blocks, each a label and a short paragraph or a list.
- `next`: one concrete step with a time ("A 30-minute call this week to ...") and the contact.

Labels are structure. When the source gives none, use plain ones in the style of the example ("What your
team told us", "Who we are") and say that you added them.

### Check, then hand over

Run the checker on the file and fix every problem. Notes are judgment calls, so read them and decide. Then
build with bluefyn-one-pager (or bluefyn-dream for three designs). Its report is the final check for fit.

When you hand over, say that you wrote the copy from their material, list anything you were unsure of,
and list the labels you added.

## Job 2: plain business prose

1. Find the one thing the text must make the reader know or do. Put it first.
2. Cut what does not serve it: throat-clearing, restated points, generic closing lines.
3. Rewrite in the voice. Keep facts, names, numbers and commitments exactly.
4. Run `copy_check.py --text` and fix every problem.
5. Return the text, then a short list of what you changed in meaning, if anything, so the author can check.

Keep the author's structure when it works. A short message stays short.

## Files

- `scripts/copy_check.py`: the checker. Standard library only, no browser.
- `references/voice.md`: the voice, with before and after examples.

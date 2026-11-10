# Ready-made brand files in `assets/brand/`

These are the finished exports from the design team: the logo in every form, the profile pictures, the
social banners and the vector patterns. Use them as they are. Do not redraw, recolor, crop or re-export
them, and do not build a new banner or avatar when one of these fits.

All paths below are inside the bluefyn-design skill folder. In Python:

```python
import sys
sys.path.insert(0, "<bluefyn-design skill folder>/scripts")
import brand as b

b.brand_file("logo/svg/bluefyn-logo-ink.svg")            # absolute path, checked to exist
b.brand_files("banners")                                 # every file under a folder, as relative paths
b.brand_uri("patterns/bluefyn-pattern-tower-night.svg")  # data URI for an <img> or a CSS background
```

`python3 scripts/brand.py` prints the whole list with pixel sizes.

## Which file to pick

| You need | Take |
| --- | --- |
| The logo in a web page or an HTML document | `b.logo()`, `b.symbol()` or `b.wordmark()`, which draw the same artwork inline in any palette color |
| The logo as a file, for a slide, a README, an email or a design tool | `logo/svg/` |
| The logo where SVG is not accepted (Word, Google Docs, a form upload) | `logo/png/`, which has a transparent ground |
| The logo for a printer or a vendor | `logo/pdf/`, which is vector |
| A favicon, an app icon in a list, any mark drawn very small | `logo/svg/bluefyn-symbol-small-sizes-*.svg` |
| A profile picture for a social or chat account | `avatars/<platform>/` |
| A header image for LinkedIn or X | `banners/` |
| A background or hero image made of the brand's material | `patterns/` |

## Logo

`assets/brand/logo/{svg,png,pdf}/bluefyn-<part>-<color>.<ext>`

| Part | What it is | SVG size | PNG size |
| --- | --- | --- | --- |
| `logo` | Symbol and wordmark together | 503.6 x 113.2 | 4000 x 899 |
| `symbol` | The four fins alone | 329 x 320 | 2106 x 2048 |
| `symbol-small-sizes` | The symbol with wider gaps between the fins, so they stay open when it is drawn small | 329 x 320 | 2106 x 2048 |
| `wordmark` | The word alone | 330.6 x 93.8 | 4000 x 1135 |

Each part comes in three colors, which gives 12 files per format.

| Color | Hex | Goes on |
| --- | --- | --- |
| `ink` | `#1C1919` | Paper and white |
| `white` | `#FFFFFF` | Navy, night and blue |
| `blue` | `#0035A6` | Paper and white, when the logo is the one accent on the page |

The logo rules in `brand.md` apply to these files: one color, clear space, nothing below the smallest
size, never inside a line of text.

## Profile pictures

`assets/brand/avatars/<platform>/bluefyn-<platform>-avatar-<ground>-<size>.png`

The symbol centered on a square ground. Platforms crop these to a circle or a rounded square, and the
symbol is sized to survive that.

| Platform | Sizes | Grounds |
| --- | --- | --- |
| `linkedin` | 400, 1024 | `blue`, `night`, `paper` |
| `slack` | 512, 1024 | `blue`, `night`, `paper` |
| `x` | 400, 1024 | `blue`, `night`, `paper` |

`blue` is a white symbol on Bluefyn blue, `night` is a white symbol on night, `paper` is an ink symbol on
paper. Each platform also has `bluefyn-<platform>-avatar-blue.svg`, the vector of the blue one. For a
platform that is not listed, use the 1024 file of any of the three.

## Banners

Finished header images. Upload the file that matches the slot. The `@2x` and `@3x` files are the same
picture at higher density for platforms that accept them.

`night` means a night ground. `tower` means a paper ground. Both show the tower of records on the right,
except the `center` files. A file with `mark` in its name carries the symbol alone, and one without it
carries the full logo.

### `banners/linkedin-page-cover-1128x191/`, for a company page

| File | Size | Shows |
| --- | --- | --- |
| `bluefyn-linkedin-night.png`, `@2x` | 1128 x 191, 2256 x 382 | Full logo, night ground, tower on the right |
| `bluefyn-linkedin-tower.png`, `@2x` | 1128 x 191, 2256 x 382 | Full logo, paper ground, tower on the right |
| `bluefyn-mark-linkedin-night.png`, `@2x` | 1128 x 191, 2256 x 382 | Symbol alone, night ground, tower on the right |
| `bluefyn-mark-linkedin-tower.png`, `@2x` | 1128 x 191, 2256 x 382 | Symbol alone, paper ground, tower on the right |

### `banners/linkedin-profile-1584x396/`, for a person's profile

| File | Size | Shows |
| --- | --- | --- |
| `bluefyn-mark-linkedin-profile-night.png`, `@2x` | 1584 x 396, 3168 x 792 | Symbol alone, night ground, tower on the right |
| `bluefyn-mark-linkedin-profile-tower.png`, `@2x` | 1584 x 396, 3168 x 792 | Symbol alone, paper ground, tower on the right |
| `bluefyn-mark-linkedin-profile-center-night-1400x350.png`, `@3x` | 1400 x 350, 4752 x 1188 | Symbol alone in the middle of a plain night ground |
| `bluefyn-mark-linkedin-profile-center-paper-1400x350.png`, `@3x` | 1400 x 350, 4752 x 1188 | Symbol alone in the middle of a plain paper ground |

### `banners/x-header-1500x500/`, for an X profile

| File | Size | Shows |
| --- | --- | --- |
| `bluefyn-x-night.png`, `@2x.png` | 1500 x 500, 3000 x 1000 | Full logo, night ground, tower on the right |
| `bluefyn-x-tower.png`, `@2x.jpg` | 1500 x 500, 3000 x 1000 | Full logo, paper ground, tower on the right |
| `bluefyn-mark-x-night.png` | 1500 x 500 | Symbol alone, night ground, tower on the right |
| `bluefyn-mark-x-tower.png` | 1500 x 500 | Symbol alone, paper ground, tower on the right |

## Patterns

`assets/brand/patterns/`. Vector, 1600 x 800, with the ground color painted in. They scale to any size.

| File | Ground | Shows |
| --- | --- | --- |
| `bluefyn-pattern-stream-blue.svg` | Bluefyn blue | The check log as full-width lines of white monospace text |
| `bluefyn-pattern-stream-paper.svg` | Paper | The same log in ink, with MATCH in green and OFF CONTRACT in red |
| `bluefyn-pattern-tower-night.svg` | Night | The tower of records on the right half, with CHECKING records in blue |
| `bluefyn-pattern-tower-paper.svg` | Paper | The same tower in ink on paper |
| `bluefyn-pattern-tower-folded-blue.svg` | Bluefyn blue | A folded sheet of records, with MATCH and OFF CONTRACT records |

How to use them:

- Place one as an image or a CSS background (`background: url(...) center / cover`). The towers sit on
  the right, so type goes on the left.
- A pattern is the hero graphic of its piece. Do not add a second drawing from `brand.py` next to it.
- The text inside is live SVG text. The towers use Arial. The two stream files use SF Mono and fall back
  to Menlo or another monospace font on a machine without it, which changes the line breaks slightly.
  Check the render.
- In a PDF, live text can be found by search and copied. If that matters, render the pattern to a PNG
  first and place the PNG, as `texture.png` does for the record texture.
- For a different size, crop or seed, draw a new one with `brand.py` (see `graphics.md`) instead of
  editing these files.

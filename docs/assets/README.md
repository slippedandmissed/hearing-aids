# docs/assets: hand-authored diagrams

These files are **source, checked in, edited by hand** (unlike everything under `docs/build`, which `make` generates). Each one is a plain SVG (or another diagrams-as-code text file) so a change to the design is a text edit, not a regeneration. `make docs` converts every `*.svg` here to a vector PDF in `docs/build/assets/`; chapters refer to them as `![caption](assets/name.svg)`.

Pictures derived from data (simulations, renders, PCB images, charts) stay generated under `docs/figures/`.

## Conventions

- **Canvas** 640 px wide, text 12 px or larger (it prints at about 6.5 in wide, so 13 px is roughly 9 pt). Stack things vertically.
- **Fonts** `Helvetica Neue, Helvetica, Arial, sans-serif`. Dark text `#1f2933`, muted `#6b7785`; light text only on dark fills.
- **Step colours**, the same in every assembly diagram: 1 orange `#f08a24`, 2 blue `#2f8bd6`, 3 violet `#7a5fd0`, 4 teal `#17a2a2`, 5 pink `#e5489b`. Ribbon wires: A blue, B orange (carrier close-up, dangle map). Red `#d64545` = positive / marked / danger, black = ground. PCB fill `#dcefe3` with stroke `#2e7d5b`; parts fitted by JLCPCB are grey `#b8c0c8`.
- **Geometry** where a diagram shows a real board, draw it in millimetres inside a `<g transform="translate(x,y) scale(8)">` group, with the coordinates copied from `pcb/*/build_*.py`, and say so in the comment at the top. Note the board revision it was checked against.
- Put a comment at the top of every file saying what it shows and what it was checked against.
- Render with `rsvg-convert -w 1280 file.svg -o /tmp/x.png` and **look at it** before committing. Check for text over lines, labels over parts, clipped text.
- Keep SVG features to what `rsvg-convert` supports (no external CSS or fonts, no `foreignObject`).

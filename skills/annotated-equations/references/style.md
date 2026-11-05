# Style choices

Discuss the user's audience and destination before imposing a visual style. The defaults reproduce the course-book approach, but are not a mandatory house style.

## Defaults

- An equation row uses individually measured terms, coordinated brackets, and short plain-language labels.
- Prefer labels of five words or fewer per line and at most two lines. Let meaning determine the grouping.
- Operators are muted and usually unlabeled. Put labels above/below or at staggered levels when crowded.
- Wide layout places an optional inset on the right; narrow layout puts it below.
- Put a one-sentence takeaway outside the image; provide the equation and explanation as accessible text.
- Default math uses STIX; labels use Matplotlib's bundled DejaVu Sans for portability.

| Semantic role | Default light | Default dark | Typical meaning |
| --- | --- | --- | --- |
| estimate | #1F4E8C | #9CC0F0 | estimated result, signal, or pattern |
| error | #B4473A | #F2A091 | residual, bias, uncertainty, or a potential trap |
| data | #1A1A1A | #ECE8DF | observations |
| constant | #8A6D3B | #DCBF8A | fixed parameters or bookkeeping |
| operator | #4A505A | #B9C0C9 | equality and arithmetic operators |

These roles are starting points. A geometric quantity need not be forced into an estimation story; explain how colors are used in that figure. Role names describe meaning, not the chosen hue.

## Discussing alternatives

Useful questions, when needed: Should this match a publication or slide template? Will it appear on white, dark, or transparent backgrounds? Would a neutral or color-vision-friendly palette be preferable? Is the goal an introductory explanation or a compact expert reference?

Offer a small number of relevant choices rather than a long menu. A teal/orange palette, grayscale, user-provided hex colors, or a supplied brand guide are all acceptable. Match inset curves to corresponding terms. Keep labels and structure sufficient to interpret the figure without seeing color. Check actual contrast on the destination background; a palette name is not an accessibility guarantee.

`palette` supplies per-theme color overrides using semantic roles. `background` controls the opaque PNG background; SVG remains transparent. `style` controls label font, label/tick sizes, and minimum display width. See rendering.md. Honor layout and typography preferences, but flag choices that make the final figure illegible or mathematically misleading.

For slides, choose an appropriate final displayed size rather than inheriting web assumptions. For dense mathematics, split into steps or use the Python API for a custom composition. Do not squeeze a long expression into a narrow canvas by reducing type indefinitely.

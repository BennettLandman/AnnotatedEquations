# Rendering and editable inputs

## Setup and invocation

Requires Python 3.9+ and Matplotlib. Resolve paths relative to the installed skill, not the current course or repository. No external LaTeX installation is needed.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r /path/to/annotated-equations/requirements.txt
.venv/bin/python /path/to/annotated-equations/scripts/render_equation.py equation.json --output output
```

By default this exports four SVGs and four PNGs (wide/narrow × light/dark), a copy of the JSON, a checks report, and a caption/alt-text file. PNGs have opaque backgrounds at 200 dpi. SVGs have transparent backgrounds and outlined glyphs. Select variants with `--layouts wide` or `--themes light`. Keep JSON and caption text for editing and accessibility.

Exit 0 means geometry checks passed, 1 means outputs exist but have reported layout/readability problems, and 2 means invalid input or a rendering error. Do not deliver a flagged figure as final without resolving or explicitly describing the issue. Existing output files of the same names are replaced; use a new output folder when preserving revisions.

## Book examples: grouping and custom behavior

For six real teaching cases, see [teaching-examples.md](teaching-examples.md), `../examples/book/equations.json`, and its `build_examples.py`. Run that generator with `--output` to reproduce the cases, plain baselines, and light/dark phone/desktop variants. That richer book JSON is a separate format consumed by its own generator; do not pass it to `render_equation.py`. The simple CLI schema below remains useful for new figures and sampled curves.

## Specification

See `../examples/area.json` and `../examples/decay.json` for complete working inputs.

Required top-level fields:

- `name`: safe filename stem (letters, numbers, underscores, hyphens).
- `alt_text`: full equation in words, meanings, and any inset explanation.
- `takeaway`: one sentence about the consequence, saved separately from the image.
- `rows`: nonempty list of objects with `y` (relative baseline in inches, default 0) and `terms`.

Each term has `tex` (Matplotlib mathtext, normally `$...$`), `role` (default `data`), optional `label`, optional integer `level` (default 0), and `side` (`below` or `above`). Newlines split labels. Higher levels move annotations farther from the equation; collisions can increase levels automatically. Multirow baselines are explicit: give rows enough separation and inspect cross-row collisions.

Roles: `estimate`, `error`, `data`, `constant`, `operator`, plus `gray` and `faint` for secondary graphics.

Optional `palette` contains `light` and/or `dark` objects with role-to-color overrides and `background` for PNGs. An omitted role retains its default. For monochrome, set all five primary roles to the same foreground and provide an appropriate background in each requested theme.

Optional `style` contains `wide` and/or `narrow` objects. Supported keys:

- `equation_fs`: equation font size in points (default 30).
- `label_fs`: label size (default 13 wide / 14 narrow).
- `tick_fs`: inset ticks/title/axis labels (default 12.5 wide / 14 narrow).
- `font_family`: annotation font family (default `DejaVu Sans`; custom inset fonts require the Python API).
- `min_px`: smallest intended display width in CSS pixels (default 644 wide / 286 narrow).

For example:

```json
{
  "palette": {
    "light": {"estimate": "#006D77", "error": "#A94C13", "background": "white"},
    "dark": {"estimate": "#83D6D0", "error": "#FFBE85", "background": "#14252B"}
  },
  "style": {
    "wide": {"label_fs": 14, "equation_fs": 32, "font_family": "DejaVu Sans", "min_px": 700}
  }
}
```

This fragment belongs in a full specification. Transparent SVGs must be placed on the matching background. The two fixed canvas widths are 8 and 4 inches; for other compositions use the Python API and adapt the renderer deliberately.

## Insets

JSON supports sampled line plots: `inset` has `title`, `xlabel`, `ylabel`, and `series`. Each series has equal-length finite numeric `x` and `y` arrays (at least two points), a `role`, and optional `label`. Compute the samples in code from the actual model. No expression strings are executed.

For richer insets, import from the bundled `scripts/ann_eq.py`:

```python
from ann_eq import ann_eq, titled

def behavior(ax, palette, tick_fs):
    ax.plot([0, 1, 2], [0, 1, 4], color=palette['estimate'])
    ax.set_xlabel('input')
    ax.set_ylabel('squared input')

checks = ann_eq(
    'square.svg',
    [(0, [(r'$y$', 'estimate', 'squared output'),
          (r'$=$', 'operator'), (r'$x^2$', 'data', 'input squared')])],
    layout='wide', theme='light', inset=titled(behavior, 'Quadratic growth'),
    preview_dir='.', palette={'estimate': '#006D77'},
)
```

Run a custom script with this skill's `scripts` directory on `PYTHONPATH`, or add that absolute directory to `sys.path`. Do not depend on a course checkout. `ann_eq()` also accepts `fs`, `inset_size=(width,height)` in inches, `style`, and `circled` (exact term strings to outline). Python code is trusted executable code; JSON does not load callbacks or evaluate expressions.

## Math and verification limits

This uses Matplotlib mathtext, not full LaTeX. Use `\frac`, `\mathrm`, `\leq`, and `\geq`. Avoid `\tfrac`, `\dfrac`, `\big`, custom macros, and arbitrary LaTeX packages. Keep a fraction/root/exponential structurally intact unless the renderer can preserve its notation when split. Do not place independent top-level chunks inside a fraction and imply that their typography is equivalent.

The renderer measures term and label bounds, staggers labels, crops height, and checks label collisions, horizontal equation bounds, and inset collisions. It does not guarantee mathematical correctness, font availability, contrast, nonintersecting leader lines, or every custom inset text size. Glyphs are paths in SVG, so external alt text and captions remain necessary. Inspect the actual exported variants at their final display dimensions, including nested scripts. Split crowded expressions or change the composition rather than accepting tiny text.

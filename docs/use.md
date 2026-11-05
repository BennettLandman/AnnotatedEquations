# Use the skill

## Start with the teaching question

Compare these requests:

> Make this equation look better: fₙ = Vₙ(r)/(2r)ⁿ.

> Use $annotated-equations to explain why the goat reaches a shrinking fraction of its field as dimension grows. The field has side 2r and the goat is tied at its center with rope length r. This is for first-year engineering students. Distinguish reachable volume from total field volume, and show the trend.

The second request gives the agent a reason to group the numerator and denominator, and a reason to choose a dimension-versus-share inset. It can infer defaults when context is missing, but notation alone may not establish the meaning of every symbol.

Useful context includes the equation, symbol definitions, audience, teaching point, assumptions, destination, and any existing style guide. A source is especially helpful for specialized notation. You do not need to fill out a form before every figure.

## Change the question, then change the annotations

For the same goat problem:

> Now explain why changing scale does not change the fraction. Keep the field side at twice the rope length. Show the cancellation and replace the falling-bars inset with a plot against rope length.

The new figure should label the complete ball and field volumes and show the common rⁿ factor canceling. The inset should be flat at fixed dimension. Reusing the previous declining plot would answer a different question.

See the [two book treatments](book-examples.md#2-why-does-rope-length-cancel).

## Discuss or supply style

> Before rendering, show me two palette options: the book colors and a monochrome version. Keep the same grouping and wording so I can compare the style.

> Match this journal's figure guide. Use a white background, restrained color, and labels above the equation where possible.

> Use the defaults and generate the figure now.

All are valid. Color, typography, density, backgrounds, bracket placement, and inset choices can be discussed. The skill should preserve prior preferences and proceed without an unnecessary questionnaire. A color change must also update corresponding inset curves; labels still have to work without color.

## Review the explanation

Ask whether the output answers the question you supplied:

- Does the bracket group one coherent idea? In the coin example, 45 + 10 + 1 is one tail count.
- Does the label explain a meaning? “All m independent tests stay quiet” explains a probability term better than “one minus alpha to the m.”
- Does the inset show behavior under the same assumptions as the equation?
- Does the caption state the consequence? The limit example must preserve that every finite share is positive.

Then check the actual image at its intended size. Open light and dark variants on their matching backgrounds and inspect narrow versions at phone width. Automated checks cannot establish that every leader line, nested script, or custom plot label is readable.

## Keep editable outputs

Request SVG/PNG figures plus the JSON specification, caption/alt text, and any custom Python generator. Keep them together. SVG glyphs are outlined, so the equation and explanation also need accessible text outside the image.

## Reproduce the bundled examples

From the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r skills/annotated-equations/requirements.txt
```

For the small JSON examples:

```sh
.venv/bin/python skills/annotated-equations/scripts/render_equation.py \
  skills/annotated-equations/examples/area.json --output output/area
.venv/bin/python skills/annotated-equations/scripts/render_equation.py \
  skills/annotated-equations/examples/decay.json --output output/decay
```

For all six book cases, including the plain-equation baselines:

```sh
.venv/bin/python skills/annotated-equations/examples/book/build_examples.py \
  --output output/book
```

Expect 30 SVG/PNG pairs: six plain light-background versions and 24 annotated variants (six cases × wide/narrow × light/dark), plus captions and checks. The generator uses only this repository. It never imports the course checkout. The exact source figure IDs and source commit are in `examples/book/provenance.json`.

Edit a copy of `examples/book/equations.json` together with its generator for a custom composition, or create a task-specific JSON input for `render_equation.py`. The book specification stores separate `wide`/`narrow` term rows and font sizes; it is consumed by `build_examples.py`, **not** by the simpler `render_equation.py` schema. Insets are explicit Python callbacks selected from a fixed map. No input expressions are evaluated.

For book color experiments, write `palette.json` with per-theme semantic colors and run:

```sh
.venv/bin/python skills/annotated-equations/examples/book/build_examples.py \
  --palette palette.json --output output/book-custom
```

For example, this makes a light-theme monochrome version while leaving the dark theme at its defaults:

```json
{
  "light": {
    "estimate": "#222222", "error": "#222222", "constant": "#222222",
    "data": "#222222", "operator": "#222222", "background": "#FFFFFF"
  }
}
```

Inspect the result: series previously distinguished by color may now need line styles or direct labels. A palette substitution alone is not a complete monochrome redesign.

## Check repository changes

```sh
.venv/bin/python -m unittest discover -s tests -v
```

The tests exercise rendering, invalid inputs, palette changes, book-case invariants, and geometry. Visual inspection and checking the explanation remain separate tasks. See the [rendering reference](../skills/annotated-equations/references/rendering.md) for format details and limitations.

# Choose the explanation before the layout

These examples are bundled in `../examples/book/equations.json`, with a generator that works without the course repository. The source IDs are stable. Use them when a task needs an example of grouping, inset selection, or a potentially misleading interpretation; do not copy a case's labels into an unrelated equation.

| Case | Prompt and context | Choice to transfer |
| --- | --- | --- |
| GOAT-EQ03, `fraction` | Explain reachable fraction in a centered ball/cube model | Bracket numerator and denominator as complete physical quantities; show reachable/unreachable shares in the inset. |
| GOAT-EQ04, `cancel` | Explain scaling both the rope and field together | Label the complete volumes, expose the common rⁿ cancellation, and plot against radius with fixed dimension. A falling dimension plot answers a different question. |
| GOAT-EQ20, `step-two` | Explain why adding two dimensions more than halves the share for n ≥ 2 | Label π/[2(n+2)] as one multiplier with a useful bound; do not label each symbol separately. |
| GOAT-EQ23, `limit` | Explain a zero limit without claiming a zero finite share | Attach the warning to the potentially misread zero. No inset is needed when it adds no new explanation. |
| GOAT-EQ24, `pvalue` | Explain the one-sided tail for eight heads in ten planned fair flips | Group 45 + 10 + 1 as the complete tail count and highlight 8, 9, and 10 heads. The denominator counts ordered sequences, not the eleven possible head counts. |
| GOAT-EQ25, `family-wise` | Explain per-test versus family-wide error under independence | Label (1 − α)ᵐ by its event: all tests stay quiet. Match the complement and correction to the plotted curves. State independence for the exact curve; do not imply Bonferroni's general bound requires it. |

The first two cases are algebraically connected but teach different ideas. Use the teaching question to decide which view to build. The limit case shows why annotating a familiar symbol can matter more than defining an unfamiliar one. The probability cases show why events and assumptions should drive grouping.

## Source structure

The book JSON stores separate wide/narrow rows and font sizes. It belongs to `examples/book/build_examples.py`, not the simplified `scripts/render_equation.py` schema. Each entry includes a source figure ID, alt text, takeaway, and a named inset callback. The inset callbacks recompute the model curves. Numeric labels and captions in the JSON preserve the values computed by the source generator; the repository tests independently check the probability values and geometric recurrence. Its explicit callback map does not evaluate source strings.

Run:

```sh
/path/to/python /path/to/annotated-equations/examples/book/build_examples.py --output /path/to/output
```

Read the selected entry and corresponding callback when adapting a case. Inspect actual exported variants and their report. A copied label can remain geometrically valid while becoming scientifically misleading if the model or teaching goal changes.

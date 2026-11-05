# Copyright 2026 Bennett Landman
# SPDX-License-Identifier: Apache-2.0

"""Rebuild the ES 1400 teaching examples without an ES 1400 checkout.

Equations and inset models adapted from Chapter 01, GOAT-EQ03/04/20/23/24/25.
See provenance.json. JSON selects only the explicit callbacks below; no eval.
"""
import argparse
import json
import math
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "scripts"))
from ann_eq import ann_eq, titled

FACTS = {"fwer20": 1 - .95 ** 20}

def f(n):
    """Fraction of a cube of side 2r inside the inscribed ball of radius r, in n dimensions."""
    return math.pi ** (n / 2) / (2 ** n * math.gamma(n / 2 + 1))


def inset_corners(ax, P, fs):
    n = np.arange(1, 9)
    share = np.array([f(k) for k in n])
    ax.bar(n, share, color=P["blue"], width=0.7)
    ax.bar(n, 1 - share, bottom=share, color=P["salmon"], width=0.7)
    ax.set_xticks([1, 4, 8]); ax.set_yticks([0, 0.5, 1]); ax.set_yticklabels(["0", "½", "1"])
    ax.set_xlabel("dimension n")


def inset_rope_cancels(ax, P, fs):
    r = np.linspace(0.2, 2, 50)
    for n, c in ((2, P["blue"]), (3, P["brown"]), (5, P["salmon"])):
        ax.plot(r, np.full_like(r, f(n)), color=c, lw=2)
        ax.text(2.06, f(n), f"n = {n}", color=c, fontsize=fs, va="center")
    ax.set_xlim(0.2, 2.75); ax.set_ylim(0, 1); ax.set_xticks([0.5, 1, 2]); ax.set_yticks([0, 0.5, 1])
    ax.set_yticklabels(["0", "½", "1"]); ax.set_xlabel("rope length r")


def inset_step_cap(ax, P, fs):
    n = np.arange(2, 13)
    ax.bar(n, np.pi / (2 * (n + 2)), color=P["salmon"], width=0.62)
    ax.axhline(np.pi / 8, color=P["brown"], lw=1.2, ls="--")
    ax.text(12.4, np.pi / 8 + 0.02, "π/8", color=P["brown"], fontsize=fs, ha="right", va="bottom")
    ax.set_ylim(0, 0.6); ax.set_xticks([2, 7, 12]); ax.set_yticks([0, 0.5]); ax.set_yticklabels(["0", "½"])
    ax.set_xlabel("dimension n")


def inset_binomial(ax, P, fs):
    k = np.arange(0, 11)
    p = np.array([math.comb(10, i) for i in k]) / 1024
    ax.bar(k, p, color=[P["salmon"] if i >= 8 else P["faint"] for i in k], width=0.75)
    ax.set_xticks([0, 5, 8, 10]); ax.set_yticks([0, 0.2]); ax.set_xlabel("heads in 10 flips")


def inset_fwer(ax, P, fs):
    m = np.arange(1, 61)
    ax.plot(m, 1 - 0.95 ** m, color=P["salmon"], lw=2)
    ax.plot(m, 1 - (1 - 0.05 / m) ** m, color=P["blue"], lw=2)
    ax.scatter([20], [FACTS["fwer20"]], color=P["salmon"], s=22, zorder=3)
    ax.text(58, 0.75, "uncorrected", color=P["salmon"], fontsize=fs, ha="right", va="top")
    ax.text(58, 0.1, "Bonferroni", color=P["blue"], fontsize=fs, ha="right", va="bottom")
    ax.set_ylim(0, 1); ax.set_xticks([1, 20, 60]); ax.set_yticks([0, 0.5, 1]); ax.set_yticklabels(["0", "½", "1"])
    ax.set_xlabel("tests m")


INSETS = {
    fn.__name__: fn for fn in (inset_corners, inset_rope_cancels,
                               inset_step_cap, inset_binomial, inset_fwer)
}
ROLE_TO_LEGACY = {"estimate": "blue", "error": "salmon", "constant": "brown",
                  "data": "ink", "operator": "muted"}


def build(output, palette=None):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    equations = json.loads((HERE / "equations.json").read_text())
    reports = []
    for e in equations:
        for layout in ("wide", "narrow"):
            rows = e.get("narrow", e["wide"]) if layout == "narrow" else e["wide"]
            for theme in ("light", "dark"):
                colors = dict((palette or {}).get(theme, {}))
                colors.setdefault("faint", "#819391" if theme == "dark" else "#9C978C")
                # Keep source inset colors in step with semantic term colors.
                for role, legacy in ROLE_TO_LEGACY.items():
                    if role in colors:
                        colors[legacy] = colors[role]
                callback = INSETS[e["inset"]] if e["inset"] else None
                path = output / f'{e["slug"]}-{layout}-{theme}.svg'
                r = ann_eq(path, rows, layout=layout, theme=theme,
                           fs=e["fs"][0 if layout == "wide" else 1], name=e["source_id"],
                           inset=titled(callback, e["title"]) if callback else None,
                           palette=colors, preview_dir=str(output))
                r["file"] = path.name
                reports.append(r)
        # Same mathematics, no annotation or behavior inset: an honest baseline.
        bare_rows = [(y, [(t[0], "data") for t in terms]) for y, terms in e["wide"]]
        path = output / f'{e["slug"]}-bare.svg'
        r = ann_eq(path, bare_rows, fs=e["fs"][0], name=e["source_id"] + "-bare",
                   preview_dir=str(output))
        r["file"] = path.name
        reports.append(r)
        (output / f'{e["slug"]}-caption.txt').write_text(e["takeaway"] + "\n\nAlt text: " + e["alt_text"] + "\n")
    (output / "checks.json").write_text(json.dumps(reports, indent=2) + "\n")
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "figures")
    parser.add_argument("--palette", type=Path, help="Optional light/dark palette overrides as JSON")
    args = parser.parse_args()
    palette = json.loads(args.palette.read_text()) if args.palette else None
    reports = build(args.output, palette)
    bad = [r for r in reports if r["problems"]]
    print(json.dumps({"variants": len(reports), "problems": bad}, indent=2))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

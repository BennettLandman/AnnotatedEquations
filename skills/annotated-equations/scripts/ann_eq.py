# Copyright 2026 Bennett Landman
# SPDX-License-Identifier: Apache-2.0

"""Annotated equation renderer, adapted from the ES 1400 course-book generator.

Measures terms and bracket labels, supports light/dark palettes and wide/narrow
compositions, crops height, and reports selected overlap/readability checks.
"""
import os

import matplotlib
import matplotlib.patches

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "mathtext.fontset": "stix",
    "svg.fonttype": "path",
    "svg.hashsalt": "annotated-equations",
    "font.family": "DejaVu Sans",
})

PALETTES = {
    "light": {"ink": "#1A1A1A", "blue": "#1F4E8C", "salmon": "#B4473A", "brown": "#8A6D3B",
              "muted": "#4A505A", "gray": "#6B7280", "faint": "#D9D6CC"},
    "dark": {"ink": "#ECE8DF", "blue": "#9CC0F0", "salmon": "#F2A091", "brown": "#DCBF8A",
             "muted": "#B9C0C9", "gray": "#AAB3BD", "faint": "#3E5452"},
}

# Layouts. min_px is the default minimum display width for the label/tick size estimate.
LAYOUTS = {
    "wide": {"w": 8.0, "label_fs": 13, "tick_fs": 12.5, "min_px": 644},
    "narrow": {"w": 4.0, "label_fs": 14, "tick_fs": 14, "min_px": 286},
}
GAP = 0.07
PAD = 0.12


def quiet(ax, P, fs, title=None):
    """Quiet inset axes: no top or right spines, muted ticks, a one-line gray title."""
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(P["muted"])
        ax.spines[side].set_linewidth(0.9)
    ax.tick_params(colors=P["muted"], labelsize=fs, length=3, width=0.8)
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_color(P["muted"])
    ax.xaxis.label.set_color(P["muted"]); ax.xaxis.label.set_size(fs)
    ax.yaxis.label.set_color(P["muted"]); ax.yaxis.label.set_size(fs)
    ax.patch.set_alpha(0)
    if title:
        ax.set_title(title, fontsize=fs, color=P["gray"], loc="left", pad=8)


def _place_rows(ax, r, dpi, rows, P, fs, label_fs, region, family="DejaVu Sans"):
    """Draw the rows centered in [0, region]; return the artists, for the checks."""
    labels, glyphs = [], []
    step = max(0.5, 2 * label_fs * 1.15 / 72 + 0.12)  # a bumped label clears a two-line label
    for y, terms in rows:
        objs = []
        for t in terms:
            o = ax.text(0, y, t[0], fontsize=fs, color=P.get(t[1], t[1]), ha="left", va="baseline", family=family)
            bb = o.get_window_extent(r)
            objs.append((o, bb.width / dpi, bb.y0 / dpi, bb.y1 / dpi))
        # Label widths, then the row's full extent: shift it so edge labels stay on the canvas.
        lws = []
        for t in terms:
            if len(t) > 2 and t[2]:
                probe = ax.text(0, 0, t[2], ha="center", fontsize=label_fs, linespacing=1.15, family=family)
                lws.append(probe.get_window_extent(r).width / dpi); probe.remove()
            else:
                lws.append(0)
        total = sum(o[1] for o in objs) + GAP * (len(objs) - 1)
        x = (region - total) / 2
        left = right = 0.0
        cx = x
        for (o, ww, y0, y1), lw_ in zip(objs, lws):
            left = min(left, cx + ww / 2 - lw_ / 2 - x)
            right = max(right, cx + ww / 2 + lw_ / 2 - (x + total))
            cx += ww + GAP
        x += max(0, 0.06 - (x + left)) - max(0, (x + total + right) - (region - 0.06))
        used = {}
        for (o, ww, y0, y1), t, lw_ in zip(objs, terms, lws):
            o.set_x(x)
            glyphs.append(o)
            if len(t) > 2 and t[2]:
                level = t[3] if len(t) > 3 else 0
                side = t[4] if len(t) > 4 else "below"
                c = P.get(t[1], t[1]); cx = x + ww / 2
                lo, hi = cx - lw_ / 2 - 0.08, cx + lw_ / 2 + 0.08
                while any(not (hi < a or lo > b) for a, b in used.get((side, level), [])):
                    level += 1
                used.setdefault((side, level), []).append((lo, hi))
                sgn = -1 if side == "below" else 1
                yb = (y0 - 0.14) if side == "below" else (y1 + 0.14)
                ax.plot([x + 0.03, x + 0.03, x + ww - 0.03, x + ww - 0.03],
                        [yb - sgn * 0.07, yb, yb, yb - sgn * 0.07], color=c, lw=1.4, solid_capstyle="butt")
                ys = yb + sgn * (0.16 + step * level)
                ax.plot([cx, cx], [yb, ys], color=c, lw=1.0)
                labels.append(ax.text(cx, ys + sgn * 0.04, t[2], ha="center",
                                      va="top" if side == "below" else "bottom",
                                      fontsize=label_fs, color=c, linespacing=1.15, family=family))
            x += ww + GAP
    return labels, glyphs


def _overlaps(a, b, slack=0.02):
    return not (a.x1 < b.x0 - slack or b.x1 < a.x0 - slack or a.y1 < b.y0 - slack or b.y1 < a.y0 - slack)


def ann_eq(path, rows, *, layout="wide", theme="light", fs=30, inset=None, inset_size=None, name="", circled=(), palette=None, style=None, preview_dir=None):
    """Render one annotated equation to an SVG and return a dict of checks.

    rows: [(y, [(tex, color[, label[, level[, side]]]), ...]), ...]; y is relative (inches).
    inset: draw_fn(ax, P, tick_fs) or None.  inset_size: (w, h) in inches for the inset axes.
    circled: tex strings of terms to ring with an ellipse in the term's color (the unknowns of a system).
    """
    L = dict(LAYOUTS[layout])
    style = style or {}
    for key in ("label_fs", "tick_fs", "min_px"):
        if key in style:
            L[key] = style[key]
    P = {**PALETTES[theme], **(palette or {})}
    # Semantic names decouple the teaching role from the user's chosen hue.
    for role, legacy in {"estimate": "blue", "error": "salmon", "data": "ink",
                         "constant": "brown", "operator": "muted"}.items():
        P.setdefault(role, P[legacy])
    w = L["w"]
    if inset_size is None:
        inset_size = (2.25, 1.85) if layout == "wide" else (3.05, 1.85)
    iw, ih = inset_size
    # Space around the inset axes for its title, tick labels, and axis labels.
    margin_l, margin_b, margin_t = (0.62, 0.55, 0.42) if layout == "wide" else (0.72, 0.62, 0.48)
    region = w - (iw + margin_l + 0.1) if (inset and layout == "wide") else w

    # Pass 1: lay the rows out on a tall scratch canvas and measure their extent.
    fig = plt.figure(figsize=(w, 8))
    # Set the family on equation axes only; avoid changing global font preferences.

    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, w); ax.set_ylim(0, 8); ax.axis("off")
    fig.canvas.draw(); r = fig.canvas.get_renderer(); dpi = fig.dpi
    labels, glyphs = _place_rows(ax, r, dpi, [(y + 4.5, t) for y, t in rows], P, fs, L["label_fs"], region, style.get("font_family", "DejaVu Sans"))
    fig.canvas.draw()
    to_in = lambda bb: matplotlib.transforms.Bbox.from_extents(bb.x0 / dpi, bb.y0 / dpi, bb.x1 / dpi, bb.y1 / dpi)
    for g in glyphs:
        if g.get_text() in circled:
            b = to_in(g.get_window_extent(r))
            ax.add_patch(matplotlib.patches.Ellipse(((b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2), b.width + 0.1,
                                                    b.height + 0.06, fill=False, lw=1.3, color=g.get_color()))
    boxes = [to_in(a.get_window_extent(r)) for a in labels + glyphs]
    lo = min(b.y0 for b in boxes) - PAD; hi = max(b.y1 for b in boxes) + PAD
    eq_h = hi - lo

    # Pass 2: crop the canvas to the equation and add the inset.
    if inset and layout == "narrow":
        inset_zone = ih + margin_b + margin_t
        H = eq_h + inset_zone
        fig.set_size_inches(w, H)
        ax.set_position([0, inset_zone / H, 1, eq_h / H]); ax.set_ylim(lo, hi)
        inset_box = (margin_l, margin_b, iw, ih)
    elif inset:
        H = max(eq_h, ih + margin_b + margin_t)
        fig.set_size_inches(w, H)
        off = (H - eq_h) / 2
        ax.set_position([0, off / H, 1, eq_h / H]); ax.set_ylim(lo, hi)
        inset_box = (w - iw - 0.12, margin_b + (H - ih - margin_b - margin_t) / 2, iw, ih)
    else:
        H = eq_h
        fig.set_size_inches(w, H)
        ax.set_position([0, 0, 1, 1]); ax.set_ylim(lo, hi)
    iax = None
    if inset:
        bx, by, bw, bh = inset_box
        iax = fig.add_axes([bx / w, by / H, bw / w, bh / H])
        inset(iax, P, L["tick_fs"])
        quiet(iax, P, L["tick_fs"], getattr(iax, "_ann_title", None))

    # Checks: everything inside the canvas, no label overlaps, nothing in the inset.
    fig.canvas.draw(); r = fig.canvas.get_renderer()
    problems = []
    fig_bb = matplotlib.transforms.Bbox.from_extents(0, 0, w * dpi, H * dpi)
    lab_bbs = [(l.get_text(), l.get_window_extent(r)) for l in labels]
    gly_bbs = [g.get_window_extent(r) for g in glyphs]
    for g in gly_bbs:
        if g.x0 < 2 or g.x1 > fig_bb.x1 - 2:
            problems.append("equation off canvas")
    for text, bb in lab_bbs:
        if bb.x0 < 2 or bb.y0 < 2 or bb.x1 > fig_bb.x1 - 2 or bb.y1 > fig_bb.y1 - 2:
            problems.append(f"label off canvas: {text!r}")
        for g in gly_bbs:
            if _overlaps(bb, g, 0):
                problems.append(f"label touches equation: {text!r}")
    for i in range(len(lab_bbs)):
        for j in range(i + 1, len(lab_bbs)):
            if _overlaps(lab_bbs[i][1], lab_bbs[j][1]):
                problems.append(f"labels overlap: {lab_bbs[i][0]!r} / {lab_bbs[j][0]!r}")
    if iax is not None:
        ibb = iax.get_tightbbox(r)
        for text, bb in lab_bbs:
            if _overlaps(bb, ibb, 0):
                problems.append(f"label runs into inset: {text!r}")
        for g in gly_bbs:
            if _overlaps(g, ibb, 0):
                problems.append("equation runs into inset")
        if ibb.x0 < 0 or ibb.y0 < 0 or ibb.x1 > fig_bb.x1 + 1 or ibb.y1 > fig_bb.y1 + 1:
            problems.append("inset off canvas")
    smallest_pt = min([L["label_fs"]] + ([L["tick_fs"]] if inset else []))
    min_px = smallest_pt / 72 * L["min_px"] / w

    background = P.get("background", "#f7f5ef" if theme == "light" else "#142c2e")
    fig.savefig(path, transparent=True, metadata={"Date": None})
    preview = preview_dir or os.environ.get("ANN_EQ_PREVIEW")
    if preview:  # PNG on the page background, for looking at the result
        bg = background
        fig.savefig(os.path.join(preview, os.path.basename(path)[:-4] + ".png"), facecolor=bg, dpi=200)
    plt.close(fig)
    return {"name": name, "layout": layout, "theme": theme, "w": w, "h": round(H, 3),
            "min_px": round(min_px, 2), "problems": problems}


def titled(fn, title):
    """Attach a one-line gray title to an inset draw function."""
    def draw(ax, P, fs):
        fn(ax, P, fs)
        ax._ann_title = title
    return draw

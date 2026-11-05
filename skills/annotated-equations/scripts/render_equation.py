# Copyright 2026 Bennett Landman
# SPDX-License-Identifier: Apache-2.0

"""Render a trusted, declarative equation specification; never eval math input."""
import argparse
import json
import math
from pathlib import Path
import re
import sys

from ann_eq import ann_eq, titled
from matplotlib.colors import is_color_like

ROLES = {'estimate', 'error', 'data', 'constant', 'operator', 'gray', 'faint'}


def positive(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f'{label} must be a positive finite number')
    return value


def validate(spec):
    if not isinstance(spec, dict):
        raise ValueError('specification must be an object')
    name = spec.get('name', '')
    if not isinstance(name, str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]*', name):
        raise ValueError('name must contain only letters, numbers, underscores, and hyphens')
    for key in ('alt_text', 'takeaway'):
        if not isinstance(spec.get(key), str) or not spec[key].strip():
            raise ValueError(f'{key} must be nonempty text')
    if not isinstance(spec.get('rows'), list) or not spec['rows']:
        raise ValueError('rows must be a nonempty list')
    for row in spec['rows']:
        if not isinstance(row, dict):
            raise ValueError('each row must be an object')
        y = row.get('y', 0)
        if isinstance(y, bool) or not isinstance(y, (int, float)) or not math.isfinite(y):
            raise ValueError('row y must be finite')
        if not isinstance(row.get('terms'), list) or not row['terms']:
            raise ValueError('each row needs a nonempty terms list')
        for term in row['terms']:
            if not isinstance(term, dict) or not isinstance(term.get('tex'), str) or not term['tex'].strip():
                raise ValueError('each term needs nonempty tex')
            if term.get('role', 'data') not in ROLES:
                raise ValueError('unknown semantic role')
            if not isinstance(term.get('label', ''), str):
                raise ValueError('label must be text')
            level = term.get('level', 0)
            if type(level) is not int or level < 0:
                raise ValueError('level must be a nonnegative integer')
            if term.get('side', 'below') not in ('above', 'below'):
                raise ValueError('side must be above or below')
    if not isinstance(spec.get('palette', {}), dict):
        raise ValueError('palette must be an object keyed by theme')
    for theme, colors in spec.get('palette', {}).items():
        if theme not in ('light', 'dark') or not isinstance(colors, dict):
            raise ValueError('palette must use light/dark theme objects')
        for role, color in colors.items():
            if role not in ROLES | {'background'} or not is_color_like(color):
                raise ValueError(f'invalid palette entry: {role}')
    if not isinstance(spec.get('style', {}), dict):
        raise ValueError('style must be an object keyed by layout')
    for layout, style in spec.get('style', {}).items():
        if layout not in ('wide', 'narrow') or not isinstance(style, dict):
            raise ValueError('style must use wide/narrow layout objects')
        for key, value in style.items():
            if key in ('label_fs', 'tick_fs', 'min_px', 'equation_fs'):
                positive(value, key)
            elif key == 'font_family':
                if not isinstance(value, str) or not value:
                    raise ValueError('font_family must be text')
            else:
                raise ValueError(f'unknown style key: {key}')
    inset = spec.get('inset')
    if inset is not None:
        if not isinstance(inset, dict) or not isinstance(inset.get('series'), list) or not inset['series']:
            raise ValueError('inset needs a nonempty series list')
        for key in ('title', 'xlabel', 'ylabel'):
            if not isinstance(inset.get(key, ''), str):
                raise ValueError(f'inset {key} must be text')
        for series in inset['series']:
            if not isinstance(series, dict) or series.get('role', 'estimate') not in ROLES:
                raise ValueError('invalid inset series role')
            if not isinstance(series.get('label', ''), str):
                raise ValueError('series label must be text')
            xs, ys = series.get('x'), series.get('y')
            if not isinstance(xs, list) or not isinstance(ys, list) or len(xs) != len(ys) or len(xs) < 2:
                raise ValueError('inset x/y must be equal-length lists with at least two points')
            if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in xs + ys):
                raise ValueError('inset samples must be finite numbers')
    return spec


def make_inset(config):
    if not config:
        return None
    def draw(ax, palette, fs):
        for series in config['series']:
            ax.plot(series['x'], series['y'], color=palette[series.get('role', 'estimate')],
                    label=series.get('label', ''), linewidth=2)
        ax.set_xlabel(config.get('xlabel', ''))
        ax.set_ylabel(config.get('ylabel', ''))
        if len(config['series']) > 1 and any(s.get('label') for s in config['series']):
            ax.legend(frameon=False, fontsize=fs, labelcolor=palette['data'])
    return titled(draw, config.get('title', ''))


def render(spec, output, layouts=('wide', 'narrow'), themes=('light', 'dark')):
    validate(spec)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    rows = [(row.get('y', 0), [(t['tex'], t.get('role', 'data'), t.get('label', ''),
             t.get('level', 0), t.get('side', 'below')) for t in row['terms']]) for row in spec['rows']]
    reports = []
    for layout in layouts:
        for theme in themes:
            style = spec.get('style', {}).get(layout, {})
            path = output / f'{spec["name"]}-{layout}-{theme}.svg'
            report = ann_eq(path, rows, layout=layout, theme=theme,
                            fs=style.get('equation_fs', 30), name=spec['name'],
                            inset=make_inset(spec.get('inset')),
                            palette=spec.get('palette', {}).get(theme), style=style,
                            preview_dir=str(output))
            if report['min_px'] < 13.33:
                report['problems'].append('label/tick estimate below 13.33 px at minimum display width')
            reports.append(report)
    (output / f'{spec["name"]}.json').write_text(json.dumps(spec, indent=2, allow_nan=False) + '\n')
    (output / f'{spec["name"]}-checks.json').write_text(json.dumps(reports, indent=2) + '\n')
    (output / f'{spec["name"]}-caption.txt').write_text(spec['takeaway'] + '\n\nAlt text: ' + spec['alt_text'] + '\n')
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('spec', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--layouts', nargs='+', choices=('wide', 'narrow'), default=['wide', 'narrow'])
    parser.add_argument('--themes', nargs='+', choices=('light', 'dark'), default=['light', 'dark'])
    args = parser.parse_args()
    try:
        reports = render(json.loads(args.spec.read_text()), args.output, args.layouts, args.themes)
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.exit(2, f'error: {exc}\n')
    print(json.dumps(reports, indent=2))
    return 1 if any(r['problems'] for r in reports) else 0


if __name__ == '__main__':
    sys.exit(main())

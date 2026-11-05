import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/annotated-equations'
sys.path.insert(0, str(SKILL / 'scripts'))
from render_equation import render, validate


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads((SKILL/'examples/area.json').read_text())

    def test_examples_render_all_variants_and_pass_geometry(self):
        for example in ('area', 'decay'):
            spec = json.loads((SKILL/f'examples/{example}.json').read_text())
            with self.subTest(example=example), tempfile.TemporaryDirectory() as folder:
                reports = render(spec, folder)
                self.assertEqual(len(reports), 4)
                self.assertTrue(all(not r['problems'] for r in reports), reports)
                self.assertEqual(len(list(Path(folder).glob('*.svg'))), 4)
                self.assertEqual(len(list(Path(folder).glob('*.png'))), 4)
                self.assertEqual(json.loads((Path(folder)/f'{spec["name"]}.json').read_text()), spec)

    def test_palette_changes_rendered_color(self):
        self.spec['palette'] = {'light': {'estimate': '#123abc'}}
        with tempfile.TemporaryDirectory() as folder:
            render(self.spec, folder, layouts=('wide',), themes=('light',))
            svg = next(Path(folder).glob('*.svg')).read_text()
            self.assertIn('#123abc', svg)

    def test_invalid_input_rejected(self):
        cases = [dict(name='../escape'), dict(rows=[]), dict(alt_text=''),
                 dict(palette={'light': {'estimate': 'nonsense'}}),
                 dict(style={'wide': {'label_fs': -1}}),
                 dict(inset={'series': [{'x': [0, 1], 'y': [1, float('nan')]}]})]
        for change in cases:
            spec = copy.deepcopy(self.spec)
            spec.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate(spec)

    def test_small_display_width_is_flagged(self):
        self.spec['style'] = {'wide': {'min_px': 100}}
        with tempfile.TemporaryDirectory() as folder:
            reports = render(self.spec, folder, layouts=('wide',), themes=('light',))
            self.assertTrue(any('13.33' in p for p in reports[0]['problems']))


if __name__ == '__main__':
    unittest.main()

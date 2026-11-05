# Copyright 2026 Bennett Landman
# SPDX-License-Identifier: Apache-2.0

"""Verify the published gallery is reproducible and its numerical claims agree."""
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'skills/annotated-equations/examples/book'
sys.path.insert(0, str(ROOT / 'skills/annotated-equations/scripts'))
module_spec = importlib.util.spec_from_file_location('book_examples', BOOK / 'build_examples.py')
book = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(book)


class BookExamplesTests(unittest.TestCase):
    def test_standalone_cli_reproduces_all_published_cases(self):
        with tempfile.TemporaryDirectory() as folder:
            # A different working directory prevents relative course dependencies.
            result = subprocess.run([sys.executable, str(BOOK/'build_examples.py'), '--output', folder],
                                    cwd=folder, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            reports = json.loads((Path(folder)/'checks.json').read_text())
            self.assertEqual(len(reports), 30)
            self.assertTrue(all(not r['problems'] for r in reports))
            self.assertEqual(len(list(Path(folder).glob('*.svg'))), 30)
            self.assertEqual(len(list(Path(folder).glob('*.png'))), 30)
            self.assertEqual(len(list(Path(folder).glob('*-caption.txt'))), 6)
            for report in reports:
                self.assertGreaterEqual(report['min_px'], 13.33)

    def test_geometry_claims(self):
        for n in range(1, 31):
            self.assertGreater(book.f(n), 0)
            self.assertLessEqual(book.f(n), 1 + 1e-12)
            self.assertAlmostEqual(book.f(n + 2), math.pi / (2 * (n + 2)) * book.f(n))
        for n in range(2, 31):
            self.assertLess(book.f(n + 2), .5 * book.f(n))
        self.assertAlmostEqual(book.f(2), math.pi / 4)
        self.assertAlmostEqual(book.f(4), math.pi ** 2 / 32)

    def test_probability_caption_numbers(self):
        tail = sum(math.comb(10, k) for k in range(8, 11))
        self.assertEqual(tail, 56)
        self.assertEqual(tail / 2**10, .0546875)
        self.assertAlmostEqual(book.FACTS['fwer20'], 1 - .95**20)
        self.assertEqual(round(100 * book.FACTS['fwer20']), 64)
        self.assertEqual(round(100 * (1 - (1 - .05 / 20)**20), 1), 4.9)


if __name__ == '__main__':
    unittest.main()

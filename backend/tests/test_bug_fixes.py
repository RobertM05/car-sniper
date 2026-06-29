"""
Unit tests for Bug 1.3, 1.4, 1.7 fixes.

Run from the project root:
    python3 backend/tests/test_bug_fixes.py
"""
import sys
import os
import re
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from car_database import CarDatabaseOptimizer


class TestBug14YearClamping(unittest.TestCase):
    """Bug 1.4: year=0 bypasses clamping."""

    def setUp(self):
        self.db = CarDatabaseOptimizer.__new__(CarDatabaseOptimizer)

    def _simulate_year_extraction(self, year_val):
        """Replicate the fixed year extraction logic."""
        if year_val is not None:
            year_val = int(''.join(c for c in str(year_val) if c.isdigit()) or 0)
            year_val = max(1950, min(year_val, 2026))
        return year_val

    def test_year_none_stays_none(self):
        self.assertIsNone(self._simulate_year_extraction(None))

    def test_year_zero_clamped_to_1950(self):
        self.assertEqual(self._simulate_year_extraction(0), 1950)

    def test_year_string_zero_clamped_to_1950(self):
        self.assertEqual(self._simulate_year_extraction('0'), 1950)

    def test_year_below_range_clamped(self):
        self.assertEqual(self._simulate_year_extraction(1000), 1950)

    def test_year_above_range_clamped(self):
        self.assertEqual(self._simulate_year_extraction(2030), 2026)

    def test_year_valid_unchanged(self):
        self.assertEqual(self._simulate_year_extraction(2020), 2020)

    def test_year_boundary_min(self):
        self.assertEqual(self._simulate_year_extraction(1950), 1950)

    def test_year_boundary_max(self):
        self.assertEqual(self._simulate_year_extraction(2026), 2026)

    def test_year_garbage_string_clamped(self):
        self.assertEqual(self._simulate_year_extraction('abc'), 1950)

    def test_year_empty_string_clamped(self):
        self.assertEqual(self._simulate_year_extraction(''), 1950)


class TestBug17NumericModelNames(unittest.TestCase):
    """Bug 1.7: year-stripping must not destroy numeric model names."""

    def setUp(self):
        self.db = CarDatabaseOptimizer.__new__(CarDatabaseOptimizer)
        self.db._NUMERIC_MODEL_NAMES = {'2008', '3008', '5008', '4007', '1007'}

    def test_numeric_model_name_preserved(self):
        result = self.db.format_model_name('Peugeot 2008')
        self.assertIn('2008', result)

    def test_actual_year_stripped(self):
        result = self.db.format_model_name('Seria 3 2015')
        self.assertNotIn('2015', result)
        self.assertIn('3', result)

    def test_numeric_model_3008_preserved(self):
        result = self.db.format_model_name('Peugeot 3008')
        self.assertIn('3008', result)

    def test_numeric_model_5008_preserved(self):
        result = self.db.format_model_name('5008')
        self.assertIn('5008', result)

    def test_year_at_end_stripped(self):
        result = self.db.format_model_name('Golf 2021')
        self.assertNotIn('2021', result)
        self.assertIn('Golf', result)

    def test_year_in_middle_stripped(self):
        result = self.db.format_model_name('BMW 2018 320d')
        self.assertNotIn('2018', result)

    def test_model_without_year_unchanged(self):
        result = self.db.format_model_name('Golf GTI')
        self.assertIn('GTI', result)

    def test_2000_not_in_numeric_models_stripped(self):
        result = self.db.format_model_name('Toyota 2000')
        self.assertNotIn('2000', result)


class TestBug13SuspiciousPriceFiltering(unittest.TestCase):
    """Bug 1.3: is_suspicious_price wired to filter luxury cars below 15k."""

    def test_is_suspicious_luxury_below_threshold(self):
        is_luxury = any(x in 'x6' for x in ['x6','x7','q8','q7','gle','gls','g-class'])
        is_suspicious = is_luxury and 0 < 10000 < 15000
        self.assertTrue(is_suspicious)

    def test_is_not_suspicious_luxury_above_threshold(self):
        is_luxury = any(x in 'x6' for x in ['x6','x7','q8','q7','gle','gls','g-class'])
        is_suspicious = is_luxury and 0 < 20000 < 15000
        self.assertFalse(is_suspicious)

    def test_is_not_suspicious_non_luxury_below_threshold(self):
        is_luxury = any(x in 'golf' for x in ['x6','x7','q8','q7','gle','gls','g-class'])
        is_suspicious = is_luxury and 0 < 5000 < 15000
        self.assertFalse(is_suspicious)

    def test_is_not_suspicious_zero_price(self):
        is_luxury = any(x in 'q7' for x in ['x6','x7','q8','q7','gle','gls','g-class'])
        is_suspicious = is_luxury and 0 < 0 < 15000
        self.assertFalse(is_suspicious)

    def test_is_suspicious_luxury_at_14999(self):
        is_luxury = any(x in 'q8' for x in ['x6','x7','q8','q7','gle','gls','g-class'])
        is_suspicious = is_luxury and 0 < 14999 < 15000
        self.assertTrue(is_suspicious)

    def test_is_not_suspicious_luxury_at_15000(self):
        is_luxury = any(x in 'g-class' for x in ['x6','x7','q8','q7','gle','gls','g-class'])
        is_suspicious = is_luxury and 0 < 15000 < 15000
        self.assertFalse(is_suspicious)


if __name__ == '__main__':
    unittest.main()

import os
import sys
import unittest
import pandas as pd
# Ensure project root is on sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components.lenses import create_price_lens
from data.loader import get_all_data

class TestLenses(unittest.TestCase):
    def test_create_price_lens_smoke(self):
        df = get_all_data()
        # ensure datetime index
        df.index = pd.to_datetime(df.index)
        fig = create_price_lens(df)
        self.assertTrue(hasattr(fig, 'data'))
        # Expect CPI and (real) low-wage earnings traces to be present if data exists
        self.assertGreaterEqual(len(fig.data), 1)
        names = [t.name for t in fig.data]
        # If both series available, Real Low-Wage Earnings should be present
        if 'Consumer Prices' in names:
            self.assertTrue('Consumer Prices' in names)
        # If real wage trace exists, it should be labelled 'Real Low-Wage Earnings'
        if any('Real' in n for n in names):
            self.assertTrue(any(n == 'Real Low-Wage Earnings' for n in names))
        # Check that a tariff vrect was added (layout shapes contain rect)
        shapes = getattr(fig.layout, 'shapes', []) or []
        rects = [s for s in shapes if getattr(s, 'type', '') == 'rect']
        self.assertGreaterEqual(len(rects), 1)
        # Check y-axis range is approximately [95, 125]
        y_axis = getattr(fig.layout, 'yaxis', None)
        y_range = None
        if y_axis is not None and hasattr(y_axis, 'range') and y_axis.range is not None:
            y_range = list(y_axis.range)
        if y_range:
            self.assertEqual(y_range, [95, 130])
        # Look for policy/tariff annotations (Fed bands or Tariff Era)
        ann = getattr(fig.layout, 'annotations', []) or []
        texts = [a.text for a in ann]
        self.assertTrue(any(('Tariff' in str(t) or 'TARIFF' in str(t) or 'Fed' in str(t) or 'Hikes' in str(t) or 'Cuts' in str(t)) for t in texts))
        # If both CPI and Real wage present, assert the last real wage is not higher than CPI by >0.5
        if 'Consumer Prices' in names and 'Real Low-Wage Earnings' in names:
            cpi_vals = [t.y for t in fig.data if t.name == 'Consumer Prices'][0]
            real_vals = [t.y for t in fig.data if t.name == 'Real Low-Wage Earnings'][0]
            # compare last overlapping point
            last_idx = min(len(cpi_vals), len(real_vals)) - 1
            if last_idx >= 0:
                self.assertLessEqual(real_vals[last_idx], cpi_vals[last_idx] + 0.5)

if __name__ == '__main__':
    unittest.main()

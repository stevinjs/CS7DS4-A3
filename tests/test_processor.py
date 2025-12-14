import pandas as pd
import numpy as np
from data.processor import rebase_series, calculate_k_indices, align_to_monthly


def make_df():
    # daily index over Jan-Feb 2020
    idx = pd.date_range('2020-01-01', '2020-02-28', freq='D')
    df = pd.DataFrame(index=idx)
    # SP500 daily values ramp
    df['SP500'] = np.linspace(3000, 3200, len(idx))
    # Quarterly wealth: only quarterly dates (simulated)
    q_idx = pd.to_datetime(['2020-01-01', '2020-04-01'])
    wealth = pd.Series([35.0, 36.0], index=q_idx)
    # Merge, making wealth NaN for other days
    df = df.join(wealth.rename('WEALTH_TOP1'))
    # Monthly employment, wages: set on first of month
    df.loc['2020-01-01', 'EMP_LOW_WAGE'] = 100
    df.loc['2020-02-01', 'EMP_LOW_WAGE'] = 102
    df.loc['2020-01-01', 'WAGE_LOW_WAGE'] = 12.0
    df.loc['2020-02-01', 'WAGE_LOW_WAGE'] = 12.5
    # Fill other days with NaN to emulate reporting frequency
    return df


def test_align_to_monthly():
    df = make_df()
    monthly = align_to_monthly(df)
    # index freq should be end-of-month (monthly)
    assert monthly.index.freq is not None
    assert monthly.index.freqstr in ('M', 'ME') or monthly.index[-1].day >= 28
    # SP500 should not be NaN
    assert not monthly['SP500'].isna().any()
    # WEALTH_TOP1 should be forward filled into monthly rows
    assert not monthly['WEALTH_TOP1'].isna().any()


def test_rebase_series():
    df = make_df()
    monthly = align_to_monthly(df)
    rebased = rebase_series(monthly, '2020-01-01')
    # At base date, all series should equal 100
    base_idx = rebased.index.get_indexer([pd.to_datetime('2020-01-31')], method='nearest')[0]
    base_vals = rebased.iloc[base_idx]
    # Non-numeric columns shouldn't exist; check SP500
    assert pytest_approx_equal(base_vals['SP500'], 100)


def pytest_approx_equal(a, b, tol=1e-6):
    return abs(a - b) <= tol


def test_calculate_k_indices():
    # Synthetic normalized dataframe where values are normalized
    idx = pd.date_range('2020-01-31', periods=3, freq='ME')
    df = pd.DataFrame(index=idx)
    df['SP500'] = [100, 110, 120]
    df['WEALTH_TOP1'] = [100, 105, 110]
    df['EMP_LOW_WAGE'] = [100, 95, 90]
    df['WAGE_LOW_WAGE'] = [100, 102, 104]
    out = calculate_k_indices(df)
    # K_UPPER is mean of SP500 and WEALTH_TOP1
    assert list(out['K_UPPER']) == [100.0, 107.5, 115.0]
    # K_LOWER is mean of employment and wage
    assert list(out['K_LOWER']) == [100.0, 98.5, 97.0]


def test_calculate_k_indices_with_delinquency_series():
    # Construct a small raw-data DataFrame including delinquency series
    idx = pd.to_datetime(["2019-12-01", "2020-01-01", "2020-02-01"])
    df = pd.DataFrame(index=idx)
    df['SP500'] = [100.0, 110.0, 120.0]
    df['WEALTH_TOP1'] = [50.0, 60.0, 70.0]
    df['EMP_LOW_WAGE_RAW'] = [100.0, 100.0, 100.0]
    df['WAGE_LOW_WAGE_RAW'] = [100.0, 100.0, 100.0]
    df['DRCCLACBS_RAW'] = [1.0, 1.0, 1.0]

    out = calculate_k_indices(df)
    # With these symmetric inputs, inverted delinquency index should be 100
    # and EMP/WAGE indices are 100, so K_LOWER should be 100
    assert out['K_LOWER'].dropna().mean() == 100.0

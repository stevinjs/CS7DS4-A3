import pandas as pd
from data import config as data_config
import numpy as np

def rebase_series(df, base_date_str):
    """
    Rebases the DataFrame to 100 at the specified base_date.
    Finds the closest date in the index to base_date_str.
    Returns a new DataFrame.
    """
    try:
        base_date = pd.to_datetime(base_date_str)
        # Find integer location of nearest date
        idx_loc = df.index.get_indexer([base_date], method='nearest')[0]
        
        # Get baseline values
        base_vals = df.iloc[idx_loc]
        
        # Divide and scale
        # Replace 0 in base_vals with NaN to avoid Inf, although unlikely for these series
        base_vals = base_vals.replace(0, np.nan)
        
        rebased_df = df.div(base_vals) * 100
        return rebased_df
    except Exception as e:
        print(f"Error rebasing data: {e}")
        return df.copy()


def align_to_monthly(df):
    """
    Aligns input DataFrame to a monthly frequency.
    - For higher-frequency series (daily), takes the last observation of the month.
    - For lower-frequency series (quarterly), forward-fills the latest known value for each month.
    Returns a monthly-indexed DataFrame (period end).
    """
    try:
        # Ensure DateTimeIndex
        df = df.copy()
        df.index = pd.to_datetime(df.index)
        # Take last observation for each month, then forward-fill to cover months with no new obs
        monthly = df.resample('ME').last()
        monthly = monthly.ffill()
        return monthly
    except Exception as e:
        print(f"Error aligning to monthly: {e}")
        return df.copy()

def calculate_k_indices(df_normalized):
    """
    Calculates the Upper and Lower arm composite indices from data.

    New methodology (2020 baseline):
    - Lower Arm = average of:
        1) L&H Employment Index (2020=100)
        2) Nominal L&H Wage Index (2020=100)
        3) Inverted Average Delinquency Index (credit card + consumer loan) (higher delinquency -> lower index)

    - Upper Arm = average of:
        1) S&P 500 index (2020=100)
        2) Top 10% Wealth index (2020=100)
    """
    out_df = df_normalized.copy()
    
    # Ensure columns exist before calculation
    cols = out_df.columns
    
    # Baseline for indexing: 2020-01-01 (as requested)
    baseline = pd.to_datetime('2020-01-01')
    # Helper to compute index (2020=100) using raw series when available, else use normalized series
    def index_series(raw_name, norm_name=None):
        if raw_name and raw_name in out_df.columns:
            s = out_df[raw_name].astype(float)
            # find nearest baseline value
            try:
                idx = out_df.index.get_indexer([baseline], method='nearest')[0]
                base = float(s.iloc[idx])
                if base == 0 or np.isnan(base):
                    raise ValueError('bad base')
                return (s / base) * 100
            except Exception:
                # fallback to normalized series
                pass
        if norm_name and norm_name in out_df.columns:
            return out_df[norm_name]
        return pd.Series(np.nan, index=out_df.index)

    # Upper arm: SP500 and WEALTH_TOP1
    sp500_idx = index_series('SP500', 'SP500')
    wealth_idx = index_series('WEALTH_TOP50_RAW', 'WEALTH_TOP_50_RAW')  
    out_df['K_UPPER'] = (sp500_idx + wealth_idx) / 2

    # Lower arm components
    emp_idx = index_series('EMP_LOW_WAGE_RAW', 'EMP_LOW_WAGE')

    bottom_wealth_idx = index_series('WEALTH_BOTTOM50_RAW', 'WEALTH_BOTTOM50_RAW')
    # Prefer REAL wage when available (pre-computed real series), else fall back to nominal wage
    wage_idx = index_series('REAL_WAGE_LOW_WAGE_RAW', 'REAL_WAGE_LOW_WAGE')
    if wage_idx.isna().all():
        wage_idx = index_series('WAGE_LOW_WAGE_RAW', 'WAGE_LOW_WAGE')

    # Delinquencies: average of available series (credit card, consumer loan, mortgage)
    delinq_series = []
    for key in ['DRCCLACBS_RAW', 'DRCLACBS_RAW']:
        if key in out_df.columns:
            delinq_series.append(out_df[key].astype(float))
    if delinq_series:
        avg_delinq = pd.concat(delinq_series, axis=1).mean(axis=1)
        # index delinquency relative to baseline, then invert so higher delinquency -> lower index
        try:
            idx = out_df.index.get_indexer([baseline], method='nearest')[0]
            base_delinq = float(avg_delinq.iloc[idx])
            inverted_delinq_indexed = 100 - ((avg_delinq - base_delinq) / base_delinq * 100)
        except Exception:
            inverted_delinq_indexed = pd.Series(100.0, index=out_df.index)
    else:
        inverted_delinq_indexed = pd.Series(100.0, index=out_df.index)

    out_df['K_LOWER'] = (emp_idx + wage_idx + inverted_delinq_indexed + bottom_wealth_idx) / 4
        
    return out_df


def compute_real_wages_and_cpi(df):
    """
    Adds CPI-normalized real wage series to the DataFrame.
    REAL_WAGE_LOW_WAGE = (WAGE_LOW_WAGE / CPIAUCSL) * 100
    Returns a DataFrame with additional columns when possible.
    """
    out = df.copy()
    if 'WAGE_LOW_WAGE' in out.columns and 'CPIAUCSL' in out.columns:
        # Compute from raw units (this function will be used on raw df)
        out['REAL_WAGE_LOW_WAGE_RAW'] = (out['WAGE_LOW_WAGE'] / out['CPIAUCSL']) * 100
    return out


def compute_normalized_real_wage(rebased_df, raw_df):
    """
    Computes normalized REAL_WAGE_LOW_WAGE by re-normalizing from pre-computed RAW real wages.
    rebased_df: DataFrame with rebased/indexed series
    raw_df: Monthly raw series DataFrame
    Adds 'REAL_WAGE_LOW_WAGE' to rebased_df if possible (rebase of raw real wages).
    """
    out = rebased_df.copy()
    try:
        if 'REAL_WAGE_LOW_WAGE_RAW' in raw_df.columns:
            # Rebase the raw real wage to index 100 at START_DATE
            # Reuse rebase_series logic by creating intermediate DF
            tmp = raw_df[['REAL_WAGE_LOW_WAGE_RAW']].copy()
            tmp.columns = ['REAL_WAGE_LOW_WAGE']
            tmp_rebased = rebase_series(tmp, data_config.START_DATE)
            out['REAL_WAGE_LOW_WAGE'] = tmp_rebased['REAL_WAGE_LOW_WAGE']
    except Exception:
        pass
    return out

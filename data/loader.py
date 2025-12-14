import pandas as pd
import functools
from . import config

# Simple in-memory cache
@functools.lru_cache(maxsize=32)
def load_fred_series(series_id, series_name):
    """
    Fetches a single series from FRED via direct CSV URL.
    Returns a DataFrame with index 'DATE' and column [series_id].
    """
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    try:
        # Read CSV directly from URL
        # Use index_col=0 to handle 'DATE' or 'observation_date' dynamically
        df = pd.read_csv(url, parse_dates=[0], index_col=0)
        
        # Rename the generic value column (often matches series_id or is 'value')
        # FRED CSV usually has columns: DATE, <SERIES_ID>
        # We ensure standard naming
        if series_id in df.columns:
            df = df.rename(columns={series_id: series_name})
        else:
            # Fallback if column name differs
            df.columns = [series_name]
            
        # Filter by start date if config specified
        if config.START_DATE:
            df = df[df.index >= pd.to_datetime(config.START_DATE)]
            
        # Ensure numeric
        df[series_name] = pd.to_numeric(df[series_name], errors='coerce')
        
        return df
    except Exception as e:
        # Use print to ensure visibility in server logs/CLI
        print(f"FAILED to load {series_name} ({series_id}): {e}")
        return pd.DataFrame()

@functools.lru_cache(maxsize=1)
def get_all_data():
    """
    Loads all configured series and merges them into a single DataFrame.
    Resamples/Forward-fills to daily frequency to align different reporting periods.
    """
    merged_df = pd.DataFrame()
    
    # Load all series
    for internal_id, fred_id in config.SERIES_IDS.items():
        # Use internal ID as column name for cleaner code reference
        df = load_fred_series(fred_id, internal_id)
        
        if merged_df.empty:
            merged_df = df
        else:
            merged_df = merged_df.join(df, how='outer')
    
    # Sort by date
    merged_df = merged_df.sort_index()
    
    # Handle missing values:
    # 1. Forward fill (propagate last known value for monthly/quarterly series)
    # 2. Drop rows before the start date (handled in load, but double check)
    merged_df = merged_df.ffill()

    # Synthesize tariff time series based on config.TARIFF_SCHEDULE
    try:
        tariff_schedule = config.TARIFF_SCHEDULE
        # Create a series at the merged_df index frequency (daily)
        tariff_series = pd.Series(index=merged_df.index, dtype=float)
        last_val = 0
        for date_str, val in tariff_schedule:
            dt = pd.to_datetime(date_str)
            tariff_series.loc[tariff_series.index >= dt] = val
            last_val = val
        # Fill any earlier dates with 0 or first known
        tariff_series = tariff_series.ffill().fillna(0)
        merged_df['TARIFF_RATE'] = tariff_series
    except Exception as e:
        print(f"Failed to synthesize tariff series: {e}")
    
    return merged_df

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data.loader import get_all_data
from data.processor import align_to_monthly, compute_real_wages_and_cpi, rebase_series, compute_normalized_real_wage, calculate_k_indices
from components.lenses import create_market_lens
from data import config as data_config

# load
if __name__ == '__main__':
    df = get_all_data()
    df = align_to_monthly(df)
    df = compute_real_wages_and_cpi(df)
    df_rebased = rebase_series(df, data_config.START_DATE)
    for col in df.columns:
        df_rebased[f"{col}_RAW"] = df[col]
    df_rebased = compute_normalized_real_wage(df_rebased, df)
    df_rebased = calculate_k_indices(df_rebased)
    fig = create_market_lens(df_rebased)
    print('Traces:')
    for t in fig.data:
        y = list(t.y)
        if len(y) > 0:
            print('-', t.name, ', min:', min(y), 'max:', max(y))
        else:
            print('-', t.name, '(no data)')
    # Layout checks
    try:
        ya = fig.layout.yaxis.range
        y2 = fig.layout.yaxis2.range
        print('Layout yaxis range:', ya)
        print('Layout yaxis2 range:', y2)
    except Exception:
        print('Could not read layout ranges')

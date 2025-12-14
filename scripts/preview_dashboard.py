import os, sys

# Ensure project root is on sys.path so package imports resolve when running as a script
sys.path.insert(0, os.path.abspath(os.getcwd()))

from data.loader import get_all_data
from data.processor import rebase_series, calculate_k_indices
from data import config as data_config
from components.hero import create_k_timeline
from components.lenses import create_labor_lens, create_price_lens, create_market_lens


if __name__ == '__main__':
    df = get_all_data()
    df_rebased = rebase_series(df, data_config.START_DATE)
    df_with_k = calculate_k_indices(df_rebased)

    hero_fig = create_k_timeline(df_with_k)
    labor_fig = create_labor_lens(df_with_k)
    price_fig = create_price_lens(df_with_k)
    market_fig = create_market_lens(df_with_k)

    # Save to assets as simple HTML
    hero_fig.write_html('assets/preview_hero.html')
    labor_fig.write_html('assets/preview_labor.html')
    price_fig.write_html('assets/preview_price.html')
    market_fig.write_html('assets/preview_market.html')

    print('Preview files created in assets/ (preview_*.html)')
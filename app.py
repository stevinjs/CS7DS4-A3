import dash
from dash import dcc, html, Input, Output
import dash
import dash_bootstrap_components as dbc
import pandas as pd

from data.loader import get_all_data
from data.processor import rebase_series, calculate_k_indices, align_to_monthly, compute_real_wages_and_cpi, compute_normalized_real_wage
from data import config as data_config
from components.hero import create_k_timeline
from components.lenses import create_labor_lens, create_price_lens, create_market_lens, create_wealth_lens
from data.events import EVENTS

# Initialize app with local CSS enabled
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
app.title = "K-Shaped Economy"

def load_and_process_data():
    df = get_all_data()
    df['WEALTH_TOP50'] = df['WEALTH_TOP0_1'] + df['WEALTH_99_999'] + df['WEALTH_NEXT9'] + df['WEALTH_NEXT40']  # Example composite series
    # We'll rebase to the configured START_DATE
    # Align frequencies to monthly before rebasing to avoid SP500 daily noise
    df_monthly = align_to_monthly(df)
    df_raw = df_monthly.copy()
    # Compute raw derived series
    df_raw = compute_real_wages_and_cpi(df_raw)

    # Now rebased (normalized) copy
    df_rebased = rebase_series(df_raw, data_config.BASELINE)

    # Mix in *raw* columns with _RAW suffix to preserve original units for plotting
    for col in df_raw.columns:
        raw_col = f"{col}_RAW"
        df_rebased[raw_col] = df_raw[col]

    # Compute normalized real wage column from raw real wage
    # df_rebased = compute_normalized_real_wage(df_rebased, df_raw)
    df_with_k = calculate_k_indices(df_rebased)
    return df_with_k


# Basic Layout
df_global = load_and_process_data()
MONTHS = list(df_global.index)


def set_chart_height(fig, height=350):
    try:
        fig.update_layout(height=height)
    except Exception:
        pass
    return fig
# Pre-generate hero and initial lens figures for layout placement
hero_fig = set_chart_height(create_k_timeline(df_global), 450)
labor_fig = set_chart_height(create_labor_lens(df_global), 320)
price_fig = set_chart_height(create_price_lens(df_global), 320)
market_fig = set_chart_height(create_market_lens(df_global), 320)
wealth_fig = set_chart_height(create_wealth_lens(df_global), 320)
# Ensure initial figures have unified hover + consistent x-range and extra bottom padding for descriptions
for _fig in (hero_fig, labor_fig, price_fig, market_fig, wealth_fig):
    try:
        _fig.update_layout(hovermode='x unified')
        _fig.update_xaxes(range=['2017-01-01', '2025-12-31'])
        # Enforce larger bottom margin and push legend down to avoid overlap with description boxes
        _fig.update_layout(margin=dict(l=60, r=60, t=30, b=100))
        _fig.update_layout(legend=dict(y=-0.40))
    except Exception:
        pass


def create_lens_container(lens_id, title, subtitle, figure, description_content, chart_id=None):
    """Standard container for all lenses with flexible header, chart and description heights."""
    graph_id = chart_id or f'lens-{lens_id}-chart'
    header = html.Div([
        html.H3(
            f'LENS {lens_id}: {title}' if str(lens_id).upper() != 'HERO' else title,
            style={
                'color': '#e8eaed',
                'marginBottom': '0.25rem',
                'fontSize': '18px',
                'fontWeight': '600'
            }
        ),
        html.Div(
            html.P(subtitle, style={'color': '#9aa0b1', 'fontSize': '13px', 'marginBottom': '0', 'fontStyle': 'italic', 'lineHeight': '1.4'}),
            style={'height': '42px', 'overflow': 'hidden'}
        )
    ], style={'marginBottom': '0.75rem'})

    chart = dcc.Graph(id=graph_id, figure=figure, style={'height': '320px', 'marginBottom': '1rem'}, config={'displayModeBar': False})

    # Use flexible height to allow the description to size to its content and avoid internal scrolling
    desc = html.Div(description_content, style={'backgroundColor': 'rgba(30, 36, 51, 0.5)', 'padding': '12px', 'borderRadius': '6px', 'marginTop': '8px', 'borderLeft': '3px solid #4b5563', 'minHeight': '72px', 'height': 'auto', 'overflowY': 'hidden', 'fontSize': '12px', 'lineHeight': '1.35'})

    return html.Div([header, chart, desc], style={'padding': '0.5rem'})


app.layout = dbc.Container([
    # Header Row
    dbc.Row([
        dbc.Col([
            html.Header([
                html.H1("The K-Shaped Economy", className="text-2xl font-bold text-[var(--text-primary)]"),
                html.H4(
                    'When Policy Helps Wall Street But Hurts Main Street: The 2017-2025 Divergence',
                    style={'color': '#9aa0b1', 'fontSize': '16px', 'fontWeight': '400', 'marginBottom': '1rem'}
                )
            ], className="k-header")
        ])
    ], className='mb-3'),



    # Main Content row: full-width 2x2 grid
    dbc.Row([
        dbc.Col([
            # HERO full-width row
            dbc.Row([
                dbc.Col(create_lens_container('HERO', 'Branched K-Timeline', 'Composite divergence: upper arm climbs while lower arm stagnates', hero_fig, html.Div([
                    html.Div('Composite K-Shaped Indices:', style={'color': '#e8eaed', 'fontWeight': '600', 'fontSize': '11px', 'marginBottom': '4px'}),
                    html.Div([html.Span('━ ', style={'color': '#10b981', 'fontSize': '14px', 'fontWeight': 'bold'}), html.Span('Upper Arm (Economic Narrative): ', style={'color': '#10b981', 'fontWeight': '600', 'fontSize': '11px'}), html.Span('Average of (1) S&P 500 index, indexed to Jan 2020 = 100, and (2) Top 50% wealth', style={'color': '#9aa0b1', 'fontSize': '11px'})], style={'marginBottom': '5px', 'marginLeft': '8px'}),
                    html.Div([html.Span('━ ', style={'color': '#ef4444', 'fontSize': '14px', 'fontWeight': 'bold'}), html.Span('Lower Arm (Reality of Silent Majority): ', style={'color': '#ef4444', 'fontWeight': '600', 'fontSize': '11px'}), html.Span('Average of (1) L&H employment, (2) real low-wage earnings, (3) inverted avg delinquency (credit card + consumer loan), all indexed to Jan 2020 = 100, and (4) bottom 50% wealth', style={'color': '#9aa0b1', 'fontSize': '11px'})], style={'marginBottom': '5px', 'marginLeft': '8px'}),
                    html.Div('The K-Divergence: Upper arm (assets + top wealth) climbs while lower arm (jobs + wages + debt stress + bottom wealth) stagnates', style={'color': '#9aa0b1', 'fontSize': '10px', 'fontStyle': 'italic', 'marginTop': '4px'})
                ], style={'height': '110px', 'overflowY': 'auto'}), chart_id='hero-chart'), width=10, style={'margin': '0 auto'})
            ], style={'marginBottom': '2rem'}),

            # Top row: Lens 1 & Lens 2
            dbc.Row([
                dbc.Col(create_lens_container('1', 'Labor Reality', 'Unemployment headlines vs low-wage employment dynamics', labor_fig, html.Div([
                    html.Div([html.Span('◆ ', style={'color': '#6366f1', 'fontSize': '14px', 'fontWeight': 'bold'}), html.Span('Unemployment Rate: ', style={'color': '#e8eaed', 'fontWeight': '600', 'fontSize': '11px'}), html.Span('Official headline metric - shows economy "recovered" by 2022', style={'color': '#9aa0b1', 'fontSize': '11px'})], style={'marginBottom': '6px'}),
                    html.Div([html.Span('◆ ', style={'color': '#10b981', 'fontSize': '14px', 'fontWeight': 'bold'}), html.Span('Total Employment: ', style={'color': '#e8eaed', 'fontWeight': '600', 'fontSize': '11px'}), html.Span('Aggregate job recovery across all sectors - rebounds quickly post-COVID', style={'color': '#9aa0b1', 'fontSize': '11px'})], style={'marginBottom': '6px'}),
                    html.Div([html.Span('◆ ', style={'color': '#ef4444', 'fontSize': '14px', 'fontWeight': 'bold'}), html.Span('L&H Employment (Low-Wage): ', style={'color': '#e8eaed', 'fontWeight': '600', 'fontSize': '11px'}), html.Span('Restaurants, hotels, entertainment - lags behind total, still catching up in 2024', style={'color': '#9aa0b1', 'fontSize': '11px'})], style={'marginBottom': '8px'}),
                    html.Div([html.Span('⚠ ', style={'color': '#f97316', 'fontSize': '12px'}), html.Span('Oct-Nov 2025: Data blackout due to government shutdown - official numbers unreliable', style={'color': '#f97316', 'fontSize': '11px', 'fontStyle': 'italic'})], style={'marginTop': '6px'}),
                    html.Div([html.Span('⚠ ', style={'color': '#dc2626', 'fontSize': '12px'}), html.Span('2025 Tariffs: 480K jobs lost due to tariffs + retaliation - low-wage sectors hit hardest', style={'color': '#dc2626', 'fontSize': '11px', 'fontStyle': 'italic'})], style={'marginTop': '3px'})
                ]), chart_id='labor-chart'), width=6),
                dbc.Col(create_lens_container('2', 'Policy vs Affordability', 'Tariffs and policy drove prices higher while low-wage purchasing power lagged', price_fig, html.Div([
                    html.Div([html.Span('━ ', style={'color': '#f59e0b', 'fontSize': '14px', 'fontWeight': 'bold'}), html.Span('Consumer Prices (CPI): ', style={'color': '#e8eaed', 'fontWeight': '600', 'fontSize': '11px'}), html.Span('Cost of living - up 20%+ since Jan 2020', style={'color': '#9aa0b1', 'fontSize': '11px'})], style={'marginBottom': '4px'}),
                    html.Div([html.Span('━ ', style={'color': '#6366f1', 'fontSize': '14px', 'fontWeight': 'bold'}), html.Span('Real Low-Wage Earnings: ', style={'color': '#e8eaed', 'fontWeight': '600', 'fontSize': '11px'}), html.Span('Wages adjusted for inflation - purchasing power flat, workers can afford less despite increase in wages', style={'color': '#9aa0b1', 'fontSize': '11px'})], style={'marginBottom': '7px'}),
                    html.Div('Policy Periods (Shaded Regions):', style={'color': '#e8eaed', 'fontWeight': '600', 'fontSize': '11px', 'marginBottom': '3px'}),
                    html.Div([html.Span('▮ ', style={'color': '#3b82f6', 'fontSize': '14px'}), html.Span('Fed Hikes (Mar 2022 - Jul 2023): ', style={'color': '#3b82f6', 'fontWeight': '600', 'fontSize': '11px'}), html.Span('Powell raises rates from 0% to 5.5% to fight inflation - succeeded in slowing price growth', style={'color': '#9aa0b1', 'fontSize': '11px'})], style={'marginBottom': '3px', 'marginLeft': '8px'}),
                    html.Div([html.Span('▮ ', style={'color': '#10b981', 'fontSize': '14px'}), html.Span('Fed Cuts (Sept 2024 - Dec 2025): ', style={'color': '#10b981', 'fontWeight': '600', 'fontSize': '11px'}), html.Span('Rates cut to 3.75% to boost labor market', style={'color': '#9aa0b1', 'fontSize': '11px'})], style={'marginBottom': '3px', 'marginLeft': '8px'}),
                    html.Div([html.Span('▮ ', style={'color': '#dc2626', 'fontSize': '14px'}), html.Span('Tariff Era (Apr 2025+): ', style={'color': '#dc2626', 'fontWeight': '600', 'fontSize': '11px'}), html.Span('Liberation Day 34% tariff drives prices up, adds 0.7pp to inflation - further hurting affordability', style={'color': '#9aa0b1', 'fontSize': '11px'})], style={'marginLeft': '8px'})
                ]), chart_id='price-chart'), width=6)
            ], className='mb-3'),

            # Bottom row: Lens 3 & Hero
            dbc.Row([
                dbc.Col(create_lens_container('3', 'Financial Stress', 'Roaring Markets vs. Consumer Distress', market_fig, html.Div([
                    html.Div([html.Span('━ ', style={'color': '#10b981', 'fontSize': '14px', 'fontWeight': 'bold'}), html.Span('S&P 500: ', style={'color': '#e8eaed', 'fontWeight': '600', 'fontSize': '11px'}), html.Span('Stock market up 100%+ since Jan 2020, record highs in 2024-25', style={'color': '#9aa0b1', 'fontSize': '11px'})], style={'marginBottom': '6px'}),
                    html.Div('Consumer Debt Stress:', style={'color': '#e8eaed', 'fontWeight': '600', 'fontSize': '11px', 'marginBottom': '3px'}),
                    html.Div([html.Span('━ ', style={'color': '#ef4444', 'fontSize': '14px'}), html.Span('Credit Card Delinquency: ', style={'color': '#ef4444', 'fontWeight': '600', 'fontSize': '11px'}), html.Span('90+ days late - rises from 2% to 3%+ as inflation squeezes people\'s budgets', style={'color': '#9aa0b1', 'fontSize': '11px'})], style={'marginBottom': '3px', 'marginLeft': '8px'}),
                    html.Div([html.Span('- - ', style={'color': '#ef4444', 'fontSize': '14px', 'fontWeight': 'bold', 'letterSpacing': '3px'}), html.Span('Consumer Loan Delinquency: ', style={'color': '#ef4444', 'fontWeight': '600', 'fontSize': '11px'}), html.Span('Broader consumer debt stress ticks up alongside credit cards', style={'color': '#9aa0b1', 'fontSize': '11px'})], style={'marginBottom': '6px', 'marginLeft': '8px'}),

                    html.Div('Financial K-Divergence: Markets soar (green) while consumer debt stress rises across categories (red)', style={'color': '#9aa0b1', 'fontSize': '10px', 'fontStyle': 'italic'})
                ]), chart_id='market-chart'), width=6),
                dbc.Col(create_lens_container('4', 'Wealth Distribution', 'Extreme concentration: top 10% own 70% of wealth while bottom 50% owns almost nothing', wealth_fig, html.Div([
                    html.Div('Wealth Distribution by Percentile:', style={'color': '#e8eaed', 'fontWeight': '600', 'fontSize': '11px', 'marginBottom': '4px'}),
                    html.Div([html.Span('━ ', style={'color': '#10b981', 'fontSize': '14px', 'fontWeight': 'bold'}), html.Span('Top 0.1%: ', style={'color': '#10b981', 'fontWeight': '600', 'fontSize': '11px'}), html.Span('Own ~14% of all wealth', style={'color': '#9aa0b1', 'fontSize': '11px'})], style={'marginBottom': '3px', 'marginLeft': '8px'}),
                    html.Div([html.Span('━ ', style={'color': '#8B5CF6', 'fontSize': '14px', 'fontWeight': 'bold'}), html.Span('Next 0.9%: ', style={'color': '#8B5CF6', 'fontWeight': '600', 'fontSize': '11px'}), html.Span('Own ~17% of all wealth', style={'color': '#9aa0b1', 'fontSize': '11px'})], style={'marginBottom': '3px', 'marginLeft': '8px'}),
                    html.Div([html.Span('━ ', style={'color': '#3b82f6', 'fontSize': '14px', 'fontWeight': 'bold'}), html.Span('Next 9%: ', style={'color': '#3b82f6', 'fontWeight': '600', 'fontSize': '11px'}), html.Span('90-99th percentile own ~36% of wealth', style={'color': '#9aa0b1', 'fontSize': '11px'})], style={'marginBottom': '3px', 'marginLeft': '8px'}),
                    html.Div([html.Span('━ ', style={'color': '#f59e0b', 'fontSize': '14px', 'fontWeight': 'bold'}), html.Span('Next 40%: ', style={'color': '#f59e0b', 'fontWeight': '600', 'fontSize': '11px'}), html.Span('50-90th percentile own ~30% of wealth', style={'color': '#9aa0b1', 'fontSize': '11px'})], style={'marginBottom': '3px', 'marginLeft': '8px'}),
                    html.Div([html.Span('━ ', style={'color': '#ef4444', 'fontSize': '14px', 'fontWeight': 'bold'}), html.Span('Bottom 50%: ', style={'color': '#ef4444', 'fontWeight': '600', 'fontSize': '11px'}), html.Span('Own only ~3% of total wealth', style={'color': '#9aa0b1', 'fontSize': '11px'})], style={'marginBottom': '6px', 'marginLeft': '8px'}),
                    html.Div('Extreme concentration: Top 10% own ~70% of all US wealth while bottom half owns almost nothing', style={'color': '#9aa0b1', 'fontSize': '10px', 'fontStyle': 'italic'})
                ]), chart_id='wealth-chart'), width=6)
            ])
        ], width=12)
    ], className='mb-5'),


], fluid=True, style={'backgroundColor': data_config.COLORS['bg_primary'], 'minHeight': '100vh'})



# Date-range based hero update removed. Figures are now static and pre-generated; hovermode and x-range are applied at startup.




# Date-range based lens update removed. Figures are static; they are generated at startup and will reflect the full dataset.


if __name__ == '__main__':
    app.run(debug=True, port=8050)

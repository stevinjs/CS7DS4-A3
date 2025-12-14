import plotly.graph_objects as go
import pandas as pd
from data import config as data_config
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Shared Dark Theme Layout Template
COLORS = data_config.COLORS

DARK_TEMPLATE = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color=COLORS['text_secondary'], family='Inter, sans-serif'),
    xaxis=dict(
        showgrid=False, 
        zeroline=False, 
        showline=True, 
        linewidth=1, 
        linecolor=COLORS['border_subtle']
    ),
    yaxis=dict(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(255,255,255,0.05)', 
        zeroline=False
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    margin=dict(l=40, r=20, t=30, b=40)
)

def create_labor_lens(df):
    """
    Lens 1: Labor Reality.
    Compare Headline Unemployment (UNRATE) vs Low-Wage Employment (EMP_LOW_WAGE).
    """
    fig = go.Figure()
    
    # Unemployment (Left Y) — headline series
    unrate_key = 'UNRATE_RAW' if 'UNRATE_RAW' in df.columns else 'UNRATE'
    if unrate_key in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[unrate_key],
            name='Unemployment Rate',
            line=dict(color='#6366f1', width=3),
            hovertemplate='%{y:.1f}%'
        ))

    # Total Employment (PAYEMS) indexed to 2020-01-01 on right axis
    PAYEMS_KEY = 'PAYEMS_RAW' if 'PAYEMS_RAW' in df.columns else 'PAYEMS'
    if PAYEMS_KEY in df.columns:
        try:
            series = df[PAYEMS_KEY].dropna()
            base_date = pd.to_datetime('2020-01-01')
            base_val = series.asof(base_date) if base_date in series.index or series.asof(base_date) is not None else series.iloc[0]
            base_val = float(base_val)
            payems_idx = (series / base_val) * 100.0
            fig.add_trace(go.Scatter(
                x=payems_idx.index,
                y=payems_idx.values,
                name='Total Employment',
                line=dict(color='#10b981', width=2, dash='dot'),
                yaxis='y2',
                hovertemplate='%{y:.1f}'
            ))
        except Exception:
            pass

    # L&H Employment (Low-Wage) indexed to 2020-01-01 on right axis (seasonally adjusted / smoothed)
    LH_KEY = 'EMP_LOW_WAGE_RAW' if 'EMP_LOW_WAGE_RAW' in df.columns else 'EMP_LOW_WAGE'
    if LH_KEY in df.columns:
        try:
            raw = df[LH_KEY].astype(float)
            # Apply 3-month centered moving average to smooth seasonal waves
            smoothed = raw
            # Fill edge NaNs conservatively
            smoothed = smoothed.ffill().bfill()
            base_date = pd.to_datetime('2020-01-01')
            base_val = smoothed.asof(base_date) if base_date in smoothed.index or smoothed.asof(base_date) is not None else smoothed.iloc[0]
            base_val = float(base_val)
            lh_idx = (smoothed / base_val) * 100.0
            fig.add_trace(go.Scatter(
                x=lh_idx.index,
                y=lh_idx.values,
                name='L&H Employment (Low-Wage)',
                line=dict(color='#ef4444', width=3),
                yaxis='y2',
                hovertemplate='%{y:.1f}'
            ))
        except Exception:
            pass
    
    final_layout = DARK_TEMPLATE.copy()
    final_layout.update({
        'paper_bgcolor': COLORS['bg_secondary'],
        'plot_bgcolor': COLORS['bg_secondary'],
        'font': dict(color=COLORS['text_primary'], family='Inter, sans-serif'),
        'xaxis': dict(type='date', gridcolor='rgba(255,255,255,0.05)', color=COLORS['text_secondary']),
        'yaxis': dict(
            gridcolor='rgba(255,255,255,0.05)',
            color='#6366f1',
            title=dict(text='<b>Unemployment Rate (%)</b>', font=dict(color='#6366f1', size=12)),
            tickfont=dict(color='#6366f1'),
            range=[3, 15],
            showgrid=True
        ),
        'yaxis2': dict(
            overlaying='y',
            side='right',
            showgrid=False,
            title=dict(text='<b>Employment Level (Jan 2020 = 100)</b>', font=dict(color='#10b981', size=12)),
            tickfont=dict(color=COLORS['text_secondary']),
            range=[60, 110]
        ),
        'title': None,
        'hovermode': "x unified",
        'legend': dict(
            orientation='h',
            yanchor='bottom',
            y=-0.40,
            xanchor='center',
            x=0.5,
            bgcolor='rgba(30, 36, 51, 0.85)',
            bordercolor='#4b5563',
            borderwidth=1,
            font=dict(size=10, color=COLORS['text_primary'])
        ),
        'margin': dict(l=65, r=65, t=35, b=100),
        'height': 350
    })
    fig.update_layout(**final_layout)

    # Data blackout shaded region and small upper-right annotation
    # Data blackout shading restored for visibility (government shutdown Oct-Nov 2025)
    try:
        fig.add_vrect(x0='2025-10-01', x1='2025-11-30', fillcolor='rgba(249, 115, 22, 0.12)', layer='below', line_width=0)
    except Exception:
        pass
    # Move blackout annotation to lower-left so it does not block lines
    try:
        fig.add_annotation(
            x='2025-10-01',
            y=5.5,
            text='<b>DATA BLACKOUT</b><br><span style="font-size:8px">Oct jobs report cancelled</span>',
            showarrow=True,
            arrowhead=2,
            arrowcolor='#f97316',
            arrowwidth=1.5,
            ax=-80,
            ay=-60,
            font=dict(size=9, color=COLORS['text_primary']),
            bgcolor='rgba(30, 36, 51, 0.85)',
            bordercolor='#f97316',
            borderwidth=1.5,
            borderpad=3
        )
    except Exception:
        pass

    # Reposition Gig workers annotation near unemployment line (2023-06-01)
    try:
        unrate_series = None
        unrate_key = 'UNRATE_RAW' if 'UNRATE_RAW' in df.columns else 'UNRATE'
        if unrate_key in df.columns:
            unrate_series = df[unrate_key]
        # prefer the actual 2023-06-01 observation if available
        try:
            y_target = float(unrate_series.asof(pd.to_datetime('2023-06-01'))) if unrate_series is not None else 4.2
            if y_target is None or pd.isna(y_target):
                y_target = 4.2
        except Exception:
            y_target = 4.2
        fig.add_annotation(
            x='2023-06-01',
            y=y_target + 0.8,
            text='<span style="font-size:8px">Gig workers undercounted -<br>official unemployment<br>understates precarity</span>',
            showarrow=True,
            arrowhead=2,
            arrowcolor='#6b7280',
            arrowwidth=1.2,
            ax=50,
            ay=-30,
            font=dict(size=8, color='#9aa0b1'),
            bgcolor='rgba(30, 36, 51, 0.75)',
            bordercolor='#6b7280',
            borderwidth=1,
            borderpad=3,
            align='left'
        )
    except Exception:
        pass

    # Lag explanation pointing to gap between green and red lines
    fig.add_annotation(x='2022-06-01', y=95, text='Low-wage sector<br>lags recovery', showarrow=True, arrowhead=2, arrowcolor='#ef4444', arrowwidth=1.5, ax=-40, ay=20, font=dict(size=9, color=COLORS['text_primary']), bgcolor='rgba(30, 36, 51, 0.85)', bordercolor='#ef4444', borderwidth=1.5, borderpad=3)

    # Baseline marker at 2020-01-01
    fig.add_vline(x=pd.to_datetime('2020-01-01'), line_dash='dash', line_color='rgba(255, 255, 255, 0.15)', line_width=1.5)
    fig.add_annotation(x=pd.to_datetime('2020-01-01'), y=14.5, text='Baseline', showarrow=False, font=dict(size=9, color=COLORS['text_secondary']), bgcolor='rgba(30, 36, 51, 0.6)')
    return fig


def create_wealth_lens(df):
    """
    Lens 4: Wealth Distribution stacked area (Top 0.1%, Next 0.9%, Next 9%, Next 40%, Bottom 50%)
    """
    fig = go.Figure()

    added = False
    if not added:
        # Prefer internal keys (loaded into df via data.config.SERIES_IDS)
        series_map = [
            ('WEALTH_BOTTOM50_RAW', 'Bottom 50%', '#ef4444', 'rgba(239, 68, 68, 0.5)'),
            ('WEALTH_NEXT40_RAW', 'Next 40%', '#f59e0b', 'rgba(245, 158, 11, 0.5)'),
            ('WEALTH_NEXT9_RAW', 'Next 9%', '#3b82f6', 'rgba(59, 130, 246, 0.5)'),
            ('WEALTH_99_999_RAW', 'Next 0.9%', "#8B5CF6", 'rgba(139, 92, 246, 0.5)'),
            ('WEALTH_TOP0_1_RAW', 'Top 0.1%', '#10b981', 'rgba(16, 185, 129, 0.5)')
        ]
    

        present = []
        missing = []
        # Temporarily store resolved series so we can inspect them before plotting
        series_storage = {}  # label -> pd.Series (with datetime index)
        resolved_cols = {}
        for code, label, color, fill in series_map:
            col = code
            if not col:
                missing.append(label)
                continue
            try:
                s = df[col].astype(float).dropna()
                # Convert index to datetimes
                try:
                    xvals = s.index.to_timestamp() if hasattr(s.index, 'to_timestamp') else pd.to_datetime(s.index.astype(str))
                except Exception:
                    xvals = pd.to_datetime(s.index.astype(str), errors='coerce')
                s.index = xvals
                # Ensure the series name is the human-friendly label so concatenation preserves column order
                s = s.rename(label)
                series_storage[label] = s
                resolved_cols[label] = col
                present.append(label)
            except Exception:
                missing.append(label)
                continue

        # If we found series, inspect them for being "index-like" (i.e., normalized to 100),
        # which is often a baseline-indexed series (Jan 2020 = 100) rather than a percent share.
        if series_storage:
            # Log resolved mapping so we can see which columns are used at runtime
            try:
                logger.info('Wealth lens resolved columns: %s', resolved_cols)
            except Exception:
                pass

            

            # Normal path: plot the available series as shares
            # Align series into a single DataFrame in the canonical order
            ordered_labels = ['Bottom 50%', 'Next 40%', 'Next 9%', 'Next 0.9%', 'Top 0.1%']
            ordered_cols = [series_storage[l] for l in ordered_labels if l in series_storage]
            if not ordered_cols:
                # nothing to plot
                pass
            else:
                shares_df = pd.concat(ordered_cols, axis=1)
                # Ensure columns are in ordered_labels sequence
                shares_df = shares_df[[c for c in ordered_labels if c in shares_df.columns]]


                # Plot bottom-up (bottom first)
                color_map = {l: f for (_c, l, _col, f) in series_map}
                outline = dict(color='rgba(255,255,255,0.06)', width=0.6)
                for label in shares_df.columns:
                    try:
                        fig.add_trace(go.Scatter(
                            x=shares_df.index,
                            y=shares_df[label].values,
                            name=label,
                            line=outline,
                            mode='lines',
                            stackgroup='one',
                            fillcolor=color_map.get(label),
                            hovertemplate='%{y:.2f}%' 
                        ))
                        added = True
                    except Exception:
                        missing.append(label)

        # If some series are missing, annotate which ones are absent so the user knows what's loaded
        if missing:
            try:
                msg = 'Missing: ' + ', '.join(missing)
                fig.add_annotation(x=0.99, y=0.02, xref='paper', yref='paper', text=msg, showarrow=False, xanchor='right', yanchor='bottom', font=dict(size=9, color='#f3f4f6'), bgcolor='rgba(255,255,255,0.03)')
            except Exception:
                pass

    # Clean layout and styling
    final_layout = DARK_TEMPLATE.copy()
    yaxis_config = dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    yaxis_config.update({'title': dict(text='<b>Share of Total Wealth (%)</b>', font=dict(color=COLORS['text_primary'], size=12)), 'tickfont': dict(color=COLORS['text_secondary'], size=11), 'range': [0, 100]})

    final_layout.update({
        'paper_bgcolor': COLORS['bg_secondary'],
        'plot_bgcolor': COLORS['bg_secondary'],
        'font': dict(color=COLORS['text_primary'], family='Inter, sans-serif'),
        'xaxis': dict(type='date', gridcolor='rgba(255,255,255,0.05)', color=COLORS['text_secondary']),
        'yaxis': yaxis_config,
        'title': None,
        'hovermode': 'x unified',
        'legend': dict(
            orientation='h',
            yanchor='bottom',
            y=-0.40,
            xanchor='center',
            x=0.5,
            bgcolor='rgba(30, 36, 51, 0.85)',
            bordercolor='#4b5563',
            borderwidth=1,
            font=dict(size=10, color='#e8eaed')
        ),
        'margin': dict(l=60, r=40, t=30, b=100),
        'height': 320
    })
    fig.update_layout(**final_layout)


    # If nothing was added, show a helpful message to the user
    if not added:
        fig.add_annotation(x=0.5, y=0.5, xref='paper', yref='paper', text='Wealth series not available in dataset', showarrow=False, font=dict(size=11, color=COLORS['text_secondary']), bgcolor='rgba(30,36,51,0.6)')

    return fig

def create_price_lens(df):
    """
    Lens 2: Policy vs Affordability (Simplified)
    Show only: CPI (amber), Low-Wage Earnings (indigo), one Tariff Band (Liberation Day 2025), and minimal annotations.
    """
    fig = go.Figure()

    baseline = pd.to_datetime('2020-01-01')

    # CPI (indexed)
    cpi_key = 'CPIAUCSL_RAW' if 'CPIAUCSL_RAW' in df.columns else ('CPIAUCSL' if 'CPIAUCSL' in df.columns else None)
    if cpi_key:
        try:
            s = df[cpi_key].astype(float)
            base = s.asof(baseline) if baseline in s.index or s.asof(baseline) is not None else s.iloc[0]
            cpi_idx = (s / float(base)) * 100.0
            fig.add_trace(go.Scatter(x=cpi_idx.index, y=cpi_idx.values, name='Consumer Prices', line=dict(color='#f59e0b', width=4), mode='lines', hovertemplate='%{y:.1f}'))
        except Exception:
            pass

    # Low-Wage REAL Earnings (prefer precomputed real series, else compute from nominal and CPI)
    real_key_raw = 'REAL_WAGE_LOW_WAGE_RAW' if 'REAL_WAGE_LOW_WAGE_RAW' in df.columns else None
    real_key = 'REAL_WAGE_LOW_WAGE' if 'REAL_WAGE_LOW_WAGE' in df.columns else None
    wage_series_for_plot = None
    if real_key_raw and real_key_raw in df.columns:
        wage_series_for_plot = df[real_key_raw].astype(float)
    elif real_key and real_key in df.columns:
        wage_series_for_plot = df[real_key].astype(float)
    else:
        # Try to compute real wage on the fly if nominal and CPI are available
        if ('WAGE_LOW_WAGE_RAW' in df.columns or 'WAGE_LOW_WAGE' in df.columns) and ('CPIAUCSL_RAW' in df.columns or 'CPIAUCSL' in df.columns):
            try:
                nom_key = 'WAGE_LOW_WAGE_RAW' if 'WAGE_LOW_WAGE_RAW' in df.columns else 'WAGE_LOW_WAGE'
                cpi_key_raw = 'CPIAUCSL_RAW' if 'CPIAUCSL_RAW' in df.columns else 'CPIAUCSL'
                nom = df[nom_key].astype(float)
                cpi = df[cpi_key_raw].astype(float)
                # real wage in CPI-normalized units, scaled so baseline approx 100
                # Compute REAL = nominal / (CPI / CPI_base) -> (nominal * CPI_base / CPI)
                try:
                    cpi_base = float(cpi.asof(baseline) if baseline in cpi.index or cpi.asof(baseline) is not None else cpi.iloc[0])
                except Exception:
                    cpi_base = float(cpi.iloc[0])
                real = (nom * cpi_base) / cpi
                wage_series_for_plot = real.astype(float)
            except Exception:
                wage_series_for_plot = None

    if wage_series_for_plot is not None:
        try:
            s = wage_series_for_plot.dropna()
            base = s.asof(baseline) if baseline in s.index or s.asof(baseline) is not None else s.iloc[0]
            wage_idx = (s / float(base)) * 100.0
            fig.add_trace(go.Scatter(x=wage_idx.index, y=wage_idx.values, name='Real Low-Wage Earnings', line=dict(color='#6366f1', width=4), mode='lines', hovertemplate='%{y:.1f}'))
        except Exception:
            pass
    

        try:
            # Tariff era shading
            fig.add_vrect(x0='2025-04-02', x1='2025-12-31', fillcolor='rgba(220, 38, 38, 0.25)', layer='below', line_width=0)
            fig.add_annotation(x='2025-08-15', y=120, text='<b>TARIFF ERA</b><br><span style="font-size:9px">Liberation Day: 34%</span>', showarrow=False, font=dict(size=10, color='#dc2626'), bgcolor='rgba(10, 14, 26, 0.75)', bordercolor='#dc2626', borderwidth=1.5, borderpad=4, align='center')
        except Exception:
            pass

    # Fed policy context as small text annotations (not lines)
        # Hiking era: Mar 2022 - Jul 2023 (keep at top)
        try:
            # Fed hikes shading and label
            fig.add_vrect(x0='2022-03-01', x1='2023-07-31', fillcolor='rgba(59, 130, 246, 0.15)', layer='below', line_width=0)
            fig.add_annotation(x='2022-11-01', y=123, text='<b>FED HIKES</b><br><span style="font-size:9px">0% → 5.5%<br>Fighting inflation</span>', showarrow=False, font=dict(size=10, color='#3b82f6'), bgcolor='rgba(10, 14, 26, 0.75)', bordercolor='#3b82f6', borderwidth=1.5, borderpad=4, align='center')
        except Exception:
            pass

        # Cutting era: Sep 2024 - Dec 2025 (moved down slightly and increased opacity so it remains visible under tariffs)
        try:
            # Fed cuts shading and label
            fig.add_vrect(x0='2024-09-01', x1='2025-12-31', fillcolor='rgba(16, 185, 129, 0.12)', layer='below', line_width=0)
            fig.add_annotation(x='2025-01-15', y=98, text='<b>FED CUTS</b><br><span style="font-size:9px">5.5% → 3.75%<br>Support labor</span>', showarrow=False, font=dict(size=10, color='#10b981'), bgcolor='rgba(10, 14, 26, 0.75)', bordercolor='#10b981', borderwidth=1.5, borderpad=4, align='center')
        except Exception:
            pass

    # Main annotation: affordability gap
        # Main annotation: affordability gap
        # This line is removed as per the patch intent

    # Clean layout - single y-axis
    final_layout = DARK_TEMPLATE.copy()
    final_layout.update({
        'paper_bgcolor': COLORS['bg_secondary'],
        'plot_bgcolor': COLORS['bg_secondary'],
        'font': dict(color=COLORS['text_primary'], family='Inter, sans-serif'),
        'xaxis': dict(gridcolor='rgba(255,255,255,0.05)', color=COLORS['text_secondary']),
        'yaxis': dict(
            gridcolor='rgba(255,255,255,0.08)',
            color=COLORS['text_secondary'],
            title=dict(text='<b>Purchasing Power & Prices<br>(Jan 2020 = 100)</b>', font=dict(color='#e8eaed', size=13)),
            tickfont=dict(color='#9aa0b1', size=11),
            range=[95, 130],
            dtick=5,
            showgrid=True
        ),
        'title': None,
        'hovermode': 'x unified',
        'legend': dict(orientation='h', yanchor='bottom', y=-0.40, xanchor='center', x=0.5, bgcolor='rgba(30, 36, 51, 0.85)', bordercolor='#4b5563', borderwidth=1, font=dict(size=11, color=COLORS['text_primary'])),
        'margin': dict(l=70, r=40, t=30, b=100),
        'height': 350
    })
    fig.update_layout(**final_layout)

    # Baseline marker at 2020-01-01 for consistency with other lenses
    try:
        fig.add_vline(x=pd.to_datetime('2020-01-01'), line_dash='dash', line_color='rgba(255, 255, 255, 0.15)', line_width=1.5)
        fig.add_annotation(x=pd.to_datetime('2020-01-01'), y=124.5, text='Baseline', showarrow=False, font=dict(size=9, color=COLORS['text_secondary']), bgcolor='rgba(30, 36, 51, 0.6)')
    except Exception:
        pass

    return fig

def create_market_lens(df):
    """
    Lens 3: Financial Divergence.
    S&P 500 vs Consumer Distress Signals.
    """
    fig = go.Figure()
    
    # Prefer normalized (indexed) series so they show on the 80-200 axis
    baseline = pd.to_datetime('2020-01-01')

    # S&P 500: prefer already-normalized series, otherwise index raw series to baseline
    sp_y = None
    if 'SP500' in df.columns:
        sp_y = df['SP500'].astype(float)
    elif 'SP500_RAW' in df.columns:
        try:
            s = df['SP500_RAW'].astype(float)
            base = float(s.asof(baseline) if baseline in s.index or s.asof(baseline) is not None else s.iloc[0])
            sp_y = (s / base) * 100.0
        except Exception:
            sp_y = df['SP500_RAW']
    if sp_y is not None:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=sp_y,
            name="S&P 500",
            line=dict(color='#10b981', width=3),
            yaxis='y',
            mode='lines',
            hovertemplate='%{y:.1f}'
        ))

    # Add delinquency if present (attach to right-hand delinquency axis)
    # Credit card is a leading signal (solid red)
    if 'DRCCLACBS_RAW' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['DRCCLACBS_RAW'],
            name='Credit Card Delinquency',
            line=dict(color='#ef4444', width=3, dash='solid'),
            yaxis='y2',
            mode='lines',
            hovertemplate='%{y:.2f}%'
        ))

    # Consumer loan delinquency (dashed red)
    if 'DRCLACBS_RAW' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['DRCLACBS_RAW'],
            name='Consumer Loan Delinquency',
            line=dict(color='#ef4444', width=2, dash='dash'),
            yaxis='y2',
            mode='lines',
            hovertemplate='%{y:.2f}%'
        ))

    # Determine dynamic top of left axis so S&P peaks are not clipped
    try:
        y_max = 200
        if sp_y is not None:
            y_max = max(y_max, float(sp_y.max() * 1.05))
    except Exception:
        y_max = 200

    layout_updates = {
        'yaxis': dict(
            title=dict(text='<b>Index: Markets & Wealth<br>(Jan 2020 = 100)</b>', font=dict(color=COLORS['upper_arm'], size=12)),
            tickfont=dict(color=COLORS['text_secondary'], size=11),
            range=[70, y_max],
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)'
        ),
        'yaxis2': dict(
            overlaying='y',
            side='right',
            title=dict(text='<b>Delinquency Rate (%)</b>', font=dict(color='#ef4444', size=12)),
            tickfont=dict(color='#ef4444', size=11),
            range=[1, 4],
            showgrid=False
        )
    }
    final_layout = DARK_TEMPLATE.copy()
    final_layout.update({
        'paper_bgcolor': COLORS['bg_secondary'],
        'plot_bgcolor': COLORS['bg_secondary'],
        'font': dict(color=COLORS['text_primary'], family='Inter, sans-serif'),
        'xaxis': dict(gridcolor='rgba(255,255,255,0.05)', color=COLORS['text_secondary']),
        'yaxis': dict(gridcolor='rgba(255,255,255,0.05)', color=COLORS['text_secondary']),
        'yaxis2': dict(
            overlaying='y',
            side='right',
            showgrid=False
        ),
        'title': None,
        'hovermode': "x unified",
        'legend': dict(
            orientation='h',
            yanchor='bottom',
            y=-0.40,
            xanchor='center',
            x=0.5,
            bgcolor='rgba(30, 36, 51, 0.85)',
            bordercolor='#4b5563',
            borderwidth=1,
            font=dict(size=10, color='#e8eaed')
        ),
        'margin': dict(l=70, r=60, t=35, b=100),
        'height': 350
    })
    final_layout.update(layout_updates)
    fig.update_layout(**final_layout)
    # Note: Annotations removed here for clarity; moved job-loss notice to Lens 1 description

    # Baseline marker at 2020-01-01
    try:
        fig.add_vline(x=pd.to_datetime('2020-01-01'), line_dash='dash', line_color='rgba(255, 255, 255, 0.15)', line_width=1.5)
        fig.add_annotation(x=pd.to_datetime('2020-01-01'), y=y_max, text='Baseline', showarrow=False, font=dict(size=8, color='#6b7280'), bgcolor='rgba(30, 36, 51, 0.6)')
    except Exception:
        pass
    return fig

import plotly.graph_objects as go
import pandas as pd
from data import config as data_config
from data.processor import calculate_k_indices
from .lenses import DARK_TEMPLATE

COLORS = data_config.COLORS
BRANCH_DATE = pd.to_datetime(data_config.BRANCH_DATE)

def create_k_timeline(df_normalized):
    """
    Hero: K-Shaped Timeline.
    Plots the divergence of the two composite indices.
    """
    fig = go.Figure()

    upper_arm = df_normalized['K_UPPER'] if 'K_UPPER' in df_normalized.columns else None
    lower_arm = df_normalized['K_LOWER'] if 'K_LOWER' in df_normalized.columns else None
    # Create branched series and add to figure 
    if upper_arm is not None and lower_arm is not None:
        try:
            upper_br = upper_arm.copy()
            lower_br = lower_arm.copy()

            fig.add_trace(go.Scatter(
                x=upper_br.index,
                y=upper_br,
                name="Upper Arm (Economic Narrative)",
                line=dict(color=COLORS.get('upper_arm', COLORS['accent_upper']), width=4),
                fill='tonexty',
                fillcolor='rgba(16, 185, 129, 0.08)',
                hovertemplate='Index: %{y:.1f}'
            ))

            fig.add_trace(go.Scatter(
                x=lower_br.index,
                y=lower_br,
                name="Lower Arm (Reality of Silent Majority)",
                line=dict(color=COLORS.get('lower_arm', COLORS['accent_lower']), width=4),
                fill='tozeroy',
                fillcolor='rgba(239, 68, 68, 0.05)',
                hovertemplate='Index: %{y:.1f}'
            ))
        except Exception:
            pass

    # Baseline Line (100)
    fig.add_hline(y=100, line_dash="dash", line_color="rgba(255,255,255,0.15)")

    # Add visual divergence annotations and labels
    try:
        # Add vertical baseline marker (Jan 1, 2020) and remove other vertical regions to reduce clutter
        fig.add_vline(x=pd.to_datetime('2020-01-01'), line_dash='dash', line_color='rgba(255,255,255,0.15)', line_width=1.5)
        fig.add_annotation(x=pd.to_datetime('2020-01-01'), y=upper_br.max() if 'upper_br' in locals() else 140, text='Baseline', showarrow=False, font=dict(size=9, color='#6b7280'), bgcolor='rgba(30, 36, 51, 0.6)')

    except Exception:
        pass

    # Layout Customizations for Hero
    hero_layout = DARK_TEMPLATE.copy()
    hero_layout.update(
        height=560,
        margin=dict(l=40, r=40, t=20, b=100),
        xaxis=dict(showgrid=False, showline=True, linecolor=data_config.COLORS['border_subtle']),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
        legend=dict(orientation="h", y=-0.40, x=0.5, xanchor="center")
    )
    
    final_layout = dict(**hero_layout)
    final_layout.update({
        'paper_bgcolor': COLORS['bg_secondary'],
        'plot_bgcolor': COLORS['bg_secondary'],
        'font': dict(color=COLORS['text_primary'], family='Inter, sans-serif'),
        'xaxis': dict(gridcolor='rgba(255,255,255,0.05)', color=COLORS['text_secondary']),
        'yaxis': dict(
            gridcolor='rgba(255,255,255,0.05)',
            color=COLORS['text_secondary'],
            title=dict(text='<b>Composite Index<br>(Jan 2020 = 100)</b>', font=dict(color='#e8eaed', size=12)),
            tickfont=dict(color='#9aa0b1', size=11)
        ),
        'title': None,
        'hovermode': 'x unified'
    })
    fig.update_layout(**final_layout)
    
    # Add annotations for key divergence points if needed
    # (Optional: Add markers for events)

    return fig

START_DATE = "2017-01-01"
BASELINE = "2020-01-01"

# Series IDs for FRED
# Key: Internal ID, Value: FRED Series ID
SERIES_IDS = {
    # Macro
    "FEDFUNDS": "FEDFUNDS",       # Federal Funds Rate (Monthly)
    "UNRATE": "UNRATE",           # Unemployment Rate (Monthly)
    "PAYEMS": "PAYEMS",           # Total Nonfarm Employees (Monthly)
    
    # Upper Arm / Markets
    "SP500": "SP500",             # S&P 500 (Daily)
    "WEALTH_TOP1": "WFRBST01134", # Top 1% Wealth Share (Quarterly) 

    # Lower Arm / Fragile
    "EMP_LOW_WAGE": "USLAH", # Leisure & Hospitality Emp (Monthly)
    "WAGE_LOW_WAGE": "CES7000000008" # Leisure & Hospitality Hourly Earnings (Monthly)
}

# User Friendly Names
SERIES_NAMES = {
    "FEDFUNDS": "Fed Funds Rate (%)",
    "UNRATE": "Unemployment Rate (%)",
    "PAYEMS": "Nonfarm Employment (Thousands)",
    "SP500": "S&P 500 Index",
    "WEALTH_TOP1": "Top 1% Wealth Share (%)",
    "EMP_LOW_WAGE": "Leisure & Hospitality Employment (Thousands)",
    "WAGE_LOW_WAGE": "L&H Avg Hourly Wages ($)"
}

# Source references
DATA_SOURCES = {
    "Macro": "FRED (Federal Reserve Economic Data)"
}

# Additional series used for later lens analyses
SERIES_IDS.update({
    "CPIAUCSL": "CPIAUCSL",  # CPI Urban Consumers (All Items)
    "DRCCLACBS": "DRCCLACBS", # Credit Card Delinquency Rate
    "DRCLACBS": "DRCLACBS"  # Consumer Loan Delinquency Rate (alternate)
})

# Wealth distribution shares (Distributional Financial Accounts - FRED)
SERIES_IDS.update({
    "WEALTH_TOP1": "WFRBST01134",   # Top 1% share (Quarterly)
    "WEALTH_TOP0_1": "WFRBSTP1300", # Top 0.1% share (Quarterly)
    "WEALTH_99_999": "WFRBS99T999273", # 99-99.9% share (Quarterly)
    "WEALTH_NEXT9": "WFRBSN09161",  # 90th-99th percentile share (Quarterly)
    "WEALTH_NEXT40": "WFRBSN40188", # 50th-90th percentile share (Quarterly)
    "WEALTH_BOTTOM50": "WFRBSB50215" # Bottom 50% share (Quarterly)
})


SERIES_NAMES.update({
    'DRCLACBS': 'Consumer Loan Delinquency (%)'
})

# Friendly names for wealth distribution
SERIES_NAMES.update({
    'WEALTH_TOP1': 'Top 1% Wealth Share (%)',
    'WEALTH_TOP0_1': 'Top 0.1% Wealth Share (%)',
    'WEALTH_99_999': '99-99.9% Wealth Share (%)',
    'WEALTH_NEXT9': '90-99th Wealth Share (%)',
    'WEALTH_NEXT40': '50-90th Wealth Share (%)',
    'WEALTH_BOTTOM50': 'Bottom 50% Wealth Share (%)'
})


# Tariff schedule (handcrafted simplified series used for visualization)
TARIFF_SCHEDULE = [
    ("2017-01-01", 0),
    ("2018-07-06", 25),  # Tariff step increase
    ("2024-04-01", 34),
    ("2025-12-01", 10),
]

# Color palette for dark theme
COLORS = {
    'bg_primary': '#0a0e1a',
    'bg_secondary': '#141824',
    'bg_tertiary': '#1e2433',
    'text_primary': '#e8eaed',
    'text_secondary': '#9aa0b1',
    'border_subtle': '#2d3748',
    'accent_upper': '#10b981',
    'accent_lower': '#ef4444',
    'accent_neutral': '#6366f1',
    'event_fed': '#3b82f6',
    'event_tariff': '#dc2626',
    'event_shutdown': '#f97316'
}

# Additional named colors for traces
COLORS.update({
    'upper_arm': '#10b981',
    'lower_arm': '#ef4444',
    'neutral': '#6366f1',
    'inflation': '#f59e0b',
    'tariff': '#dc2626',
    'fed': '#3b82f6',
    'market': '#8b5cf6'
})

# Event type specific keys to map event types to colors
COLORS.update({
    'event_policy': '#10b981',
    'event_macro': '#6366f1',
    'event_shock': '#f97316',
    'event_tariff': '#dc2626',
    'event_fed': '#3b82f6',
    'event_shutdown': '#f97316',
    'event_market': '#8b5cf6'
})

# Baseline date to mark branch/diff in Hero chart
BRANCH_DATE = '2020-03-01'

# Debug settings
# Set to True to enable detailed wealth-series debug dumps when building Lens 4
DEBUG_WEALTH = True  # set True temporarily for debugging; change back to False when done
DEBUG_WEALTH_OUTPUT = 'data/wealth_debug.csv'

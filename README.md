***

# The K‑Shaped Economy

Interactive Dash web app that visualizes the “K‑shaped” post‑2017 US economy using multiple lenses: labor markets, prices and policy, financial stress, and wealth distribution.

## 1. Project Overview

The app loads macro, labor, price, market, and wealth series, aligns them to a monthly index, computes composite K‑indices, and renders coordinated dashboards (“lenses”) to show divergence between the “upper arm” (assets, top wealth) and “lower arm” (jobs, real wages, debt stress, bottom wealth).

Main pieces:

- `app.py`: Dash entrypoint, app layout, and figure wiring.  
- `data/`: Data loading, configuration, and feature engineering utilities (rebasing, real wages, K‑indices).  
- `components/`: Plotly figure factories for the hero timeline and the four lenses.  
- `assets/`: CSS and static assets for styling the dashboard.[1]
- `tests/` and `scripts/`: Optional helpers and tests for the data pipeline and app logic.[1]

## 2. Environment Setup

### 2.1. Prerequisites

- Python 3.9+ (recommended)  
- Git  
- A modern web browser (Chrome, Edge, Firefox, Safari)

### 2.2. Clone the Repository

```bash
git clone https://github.com/stevinjs/CS7DS4-A3.git
cd CS7DS4-A3
```

### 2.3. Create and Activate a Virtual Environment

Using `venv`:

```bash
python3 -m venv .venv
source .venv/bin/activate     # on macOS/Linux
# .venv\Scripts\activate      # on Windows (PowerShell/CMD)
```

### 2.4. Install Dependencies

All runtime dependencies are listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

This installs:

- `dash`, `dash-bootstrap-components` for the web UI.  
- `pandas`, `numpy` for data loading and transformation.  
- `plotly` for charting.  
- `pytest` for running tests.  

## 3. Running the Application

From the repository root (with the virtual environment activated):

```bash
python app.py
```

By default, Dash starts on port `8050` with debug mode enabled, as configured in `app.py`.  

Open the app in your browser at:

```text
http://127.0.0.1:8050
```

If the port is already in use, either stop the other process or edit the `port` argument in the `app.run(...)` call at the bottom of `app.py`.

## 4. Data Pipeline (What Happens Under the Hood)

The high‑level data flow is orchestrated in `load_and_process_data()` inside `app.py`:

1. **Load raw data**  
   - `get_all_data()` in `data/loader.py` reads all configured time series into a single `pandas.DataFrame` indexed by date.

2. **Construct composite series**  
   - A combined series `WEALTH_TOP50` is built from several top‑wealth percentiles (`WEALTH_TOP0_1`, `WEALTH_99_999`, `WEALTH_NEXT9`, `WEALTH_NEXT40`).

3. **Align to monthly frequency**  
   - `align_to_monthly()` converts mixed‑frequency series (e.g., daily S&P 500) to monthly to reduce noise and ensure comparability.

4. **Compute derived series**  
   - `compute_real_wages_and_cpi()` derives real wages and related CPI‑adjusted metrics.  

5. **Rebase and normalize**  
   - `rebase_series(..., data_config.BASELINE)` indexes all series to a common baseline (e.g., Jan 2020 = 100), and the rebased frame is saved to `debug_rebased.csv` for inspection.

6. **Attach raw columns**  
   - For each column in the raw frame, a `_RAW` version is added back into the rebased frame for plotting original units alongside normalized series.

7. **Compute K‑indices**  
   - `calculate_k_indices()` adds composite K‑shaped divergence indices used in the hero chart and lenses.

The resulting `df_global` is used to precompute the hero and lens figures before the Dash layout is declared.

## 5. UI Structure and Lenses

The UI is built using `dash` and `dash-bootstrap-components`:

- **Hero timeline** (`components.hero.create_k_timeline`)  
  - Shows upper vs lower arm composite K‑indices across time, with unified hover and fixed x‑axis range (2017–2025).

- **Lens 1 – Labor Reality** (`components.lenses.create_labor_lens`)  
  - Compares unemployment rate, total employment, and low‑wage (Leisure & Hospitality) employment.

- **Lens 2 – Policy vs Affordability** (`create_price_lens`)  
  - Contrasts CPI with real low‑wage earnings and overlays shaded policy regimes (rate hikes, cuts, tariffs) to show their impact on affordability.

- **Lens 3 – Financial Stress** (`create_market_lens`)  
  - Plots S&P 500 performance against credit card and consumer loan delinquencies to reveal market vs household stress divergence.

- **Lens 4 – Wealth Distribution** (`create_wealth_lens`)  
  - Visualizes wealth shares for top 0.1%, next 0.9%, next 9%, next 40%, and bottom 50%, highlighting extreme concentration.

All lenses are wrapped by a shared `create_lens_container(...)` helper that standardizes headers, chart height, and narrative descriptions.

## 6. Running Tests

If the `tests/` directory defines `pytest` test files, you can run them with:

```bash
pytest
```

This uses the `pytest` dependency listed in `requirements.txt`.

## 7. Development Notes

- **Styling**  
  - Colors and layout constants are configured in `data/config.py`, including `COLORS['bg_primary']` used for the page background.

- **Performance**  
  - Data is loaded and processed once at startup (`df_global = load_and_process_data()`), and figures are pre‑generated to avoid heavy work on callbacks.

- **Extending the app**  
  - Add new data series in `data/loader.py`, extend transformations in `data/processor.py`, and define new lenses in `components/lenses.py` following the existing pattern.

***



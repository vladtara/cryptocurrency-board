# src — Core Library

Python package powering the cryptocurrency-board data pipeline.
Fetches prices, manages CSV history, computes analytics, generates SVG charts,
and renders the dashboard README.

## Modules

| Module       | Purpose                                     |
| ------------ | ------------------------------------------- |
| `models.py`  | Pydantic data models and custom exceptions  |
| `api.py`     | Async CoinGecko API client with retry logic |
| `storage.py` | CSV persistence, history loading, analytics |
| `charts.py`  | Pygal SVG chart generation (dark theme)     |
| `rdoc.py`    | Jinja2 README template rendering            |

## Data Flow

```
api.py          models.py        storage.py          charts.py        rdoc.py
───────         ─────────        ──────────          ─────────        ───────
fetch_prices()─→ CoinPrice ──→ append_price()
                                load_named_windows()─→ DataFrame
                                compute_window_metrics()─→ metrics
                                                     │                  │
                                              generate_chart()─→ SVG    │
                                                                  render_readme()─→ README.md
```

---

## models.py

### `FetchError(Exception)`

Raised when the API fetch fails after all retry attempts.

### `CoinPrice(BaseModel)`

| Field        | Type    | Description                 |
| ------------ | ------- | --------------------------- |
| `coin`       | `str`   | Coin identifier ("bitcoin") |
| `symbol`     | `str`   | Trading symbol ("BTC")      |
| `price`      | `float` | USD price (validated > 0)   |
| `change_24h` | `float` | 24-hour percentage change   |
| `date`       | `date`  | Price record date           |

**Validator:** `price` must be strictly greater than zero.

---

## api.py

### `fetch_prices(api_key: str, max_retries: int = 3) -> dict[str, CoinPrice]`

Async function. Fetches BTC and ETH prices from the CoinGecko `/v3/simple/price` endpoint.

- **Auth:** `x-cg-demo-api-key` header
- **Retry:** Exponential backoff (`2^attempt` seconds), up to `max_retries`
- **Returns:** `{"bitcoin": CoinPrice(...), "ethereum": CoinPrice(...)}`
- **Raises:** `FetchError` after all retries are exhausted

**Usage:**

```python
from src.api import fetch_prices

prices = await fetch_prices(api_key="your-key")
print(prices["bitcoin"].price)
```

---

## storage.py

**CSV schema:** `date,price,change_24h`

### `append_price(coin_price: CoinPrice, filepath: Path) -> None`

Prepends a new price row to the top of the CSV. Creates the file if missing.

### `load_history(filepath: Path, days: int = 7) -> pd.DataFrame`

Returns the last *N* days from CSV. Empty `DataFrame` if file is missing.

### `load_full_history(filepath: Path) -> pd.DataFrame`

Loads all rows from CSV. Empty `DataFrame` if file is missing.

### `load_named_windows(filepath: Path, windows: dict[str, int]) -> dict[str, pd.DataFrame]`

Loads multiple time windows at once.
`windows` maps a label to a number of days, e.g. `{"7D": 7, "30D": 30}`.
Returns a dict of label → `DataFrame` sliced from the full history (sorted newest-first).

### `compute_window_metrics(df: pd.DataFrame) -> dict[str, float | str]`

Computes 10 statistical metrics from a price `DataFrame`:

| Key              | Type    | Description                           |
| ---------------- | ------- | ------------------------------------- |
| `min`            | `float` | Minimum price in window               |
| `max`            | `float` | Maximum price in window               |
| `avg`            | `float` | Mean price                            |
| `median`         | `float` | Median price                          |
| `return_pct`     | `float` | Period return percentage              |
| `volatility`     | `float` | Daily return std dev × 100            |
| `range_pct`      | `float` | (max − min) / min × 100              |
| `drawdown_pct`   | `float` | Maximum peak-to-trough percentage     |
| `up_day_ratio`   | `float` | Fraction of days with positive change |
| `current_streak` | `str`   | Direction and length, e.g. `"up:3"`   |

Returns all-zero values for empty input.

### `cleanup_zeros(filepath: Path) -> None`

Removes rows where `price == 0.0` from the CSV in-place.

---

## charts.py

### `generate_chart(df: DataFrame, coin: str, output_path: Path, horizon_label: str = "7D") -> None`

Generates a pygal SVG line chart with a GitHub-dark theme (`#0d1117` background, `#c9d1d9` text).

- **Coin colors:** BTC → `#ff8c00` (orange), ETH → `#4a90d9` (blue)
- **Input:** `DataFrame` with `date` and `price` columns
- **Output:** SVG file written to `output_path`

Creates parent directories automatically.

---

## rdoc.py

### `render_readme(prices, windows, charts, template_dir="./templates") -> str`

| Parameter      | Type                                              | Description                      |
| -------------- | ------------------------------------------------- | -------------------------------- |
| `prices`       | `dict[str, CoinPrice]`                            | Coin ID → current price          |
| `windows`      | `dict[str, dict[str, dict[str, float \| str]]]`   | Window → symbol → metrics dict   |
| `charts`       | `dict[str, list[dict[str, str]]]`                 | Symbol → list of `{label, path}` |
| `template_dir` | `str`                                             | Path to Jinja2 templates         |

Renders `templates/readme.md` with market data, analytics tables, and chart references.
Metrics dicts are converted to `SimpleNamespace` objects for dot-access in templates.
Adds an `updated_at` UTC timestamp (`YYYY-MM-DD HH:MM`).

---

## Dependencies

`httpx` · `pandas` · `pydantic` · `pygal` · `jinja2`

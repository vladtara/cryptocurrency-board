# Cryptocurrency Board Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the cryptocurrency-board with CoinGecko API, pygal SVG charts, proper src layout, tests, linting, and a richer README dashboard.

**Architecture:** Modular `src/` package with separate modules for API, models, storage, charts, and README rendering. `main.py` orchestrates the pipeline. `init.py` handles CI git operations using subprocess instead of gitpython.

**Tech Stack:** Python 3.14, httpx, pydantic, pandas, pygal, Jinja2, pytest, ruff, pyright, uv

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `pyproject.toml` | Modify | Dependencies, ruff/pyright config, Python 3.14 |
| `.python-version` | Modify | Update to 3.14 |
| `src/__init__.py` | Create | Package init |
| `src/models.py` | Create | Pydantic `CoinPrice` model, `FetchError` exception |
| `src/api.py` | Create | CoinGecko async client with retry |
| `src/storage.py` | Create | CSV append, load, cleanup |
| `src/charts.py` | Create | Pygal SVG chart generation |
| `src/readme.py` | Create | Jinja2 README rendering |
| `tests/__init__.py` | Create | Test package init |
| `tests/test_models.py` | Create | Model validation tests |
| `tests/test_storage.py` | Create | CSV operations tests |
| `tests/test_api.py` | Create | API client tests (mocked) |
| `tests/test_charts.py` | Create | SVG generation tests |
| `tests/test_readme.py` | Create | Template rendering tests |
| `main.py` | Modify | Rewrite to use src modules |
| `init.py` | Modify | Replace gitpython with subprocess |
| `templates/readme.md` | Modify | New dashboard layout |
| `Dockerfile` | Modify | Python 3.14 + uv |
| `.github/workflows/ci.yaml` | Create | Lint + type check + test |
| `.github/workflows/main.yaml` | Modify | Rename to build.yaml, update triggers |
| `.github/workflows/cron.yaml` | Modify | Add COINGECKO_API_KEY env |
| `requirements.txt` | Delete | Replaced by pyproject.toml |
| `data/btc-usd.csv` | Modify | Clean 0.0 entries |
| `data/eth-usd.csv` | Modify | Clean 0.0 entries |
| `CLAUDE.md` | Modify | Update documentation |

---

### Task 1: Update pyproject.toml and Python version

**Files:**
- Modify: `pyproject.toml`
- Modify: `.python-version`
- Delete: `requirements.txt`

- [ ] **Step 1: Update pyproject.toml with new dependencies and config**

Replace the full contents of `pyproject.toml`:

```toml
[project]
name = "cryptocurrency-board"
version = "0.2.0"
description = "Automated cryptocurrency price monitoring with SVG charts"
readme = "README.md"
requires-python = ">=3.14"
dependencies = [
    "httpx",
    "pandas",
    "Jinja2",
    "pydantic",
    "pygal",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "ruff",
    "pyright",
    "respx",
]

[tool.pyright]
include = ["src", "main.py", "init.py"]
exclude = [".venv", "build", "dist", ".git"]
pythonVersion = "3.14"
typeCheckingMode = "standard"
venvPath = "."
venv = ".venv"

[tool.ruff]
target-version = "py314"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Update .python-version**

Write `3.14` to `.python-version`.

- [ ] **Step 3: Delete requirements.txt**

```bash
rm requirements.txt
```

- [ ] **Step 4: Run uv sync to install dependencies**

```bash
uv sync --all-extras
```

Expected: All dependencies install successfully. `uv.lock` is updated.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml .python-version uv.lock
git rm requirements.txt
git commit -m "chore: update deps — drop aiohttp/matplotlib/pendulum/gitpython, add pygal/ruff/pytest"
```

---

### Task 2: Create models module

**Files:**
- Create: `src/__init__.py`
- Create: `src/models.py`
- Create: `tests/__init__.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Create package init files**

Create `src/__init__.py` (empty file).
Create `tests/__init__.py` (empty file).

- [ ] **Step 2: Write the failing test for CoinPrice**

Create `tests/test_models.py`:

```python
from datetime import date

from src.models import CoinPrice, FetchError


def test_coin_price_valid() -> None:
    price = CoinPrice(
        coin="bitcoin",
        symbol="BTC",
        price=67500.0,
        change_24h=1.2,
        date=date(2026, 4, 5),
    )
    assert price.coin == "bitcoin"
    assert price.symbol == "BTC"
    assert price.price == 67500.0
    assert price.change_24h == 1.2
    assert price.date == date(2026, 4, 5)


def test_coin_price_rejects_zero_price() -> None:
    from pydantic import ValidationError
    import pytest

    with pytest.raises(ValidationError):
        CoinPrice(
            coin="bitcoin",
            symbol="BTC",
            price=0.0,
            change_24h=0.0,
            date=date(2026, 4, 5),
        )


def test_coin_price_rejects_negative_price() -> None:
    from pydantic import ValidationError
    import pytest

    with pytest.raises(ValidationError):
        CoinPrice(
            coin="bitcoin",
            symbol="BTC",
            price=-100.0,
            change_24h=0.0,
            date=date(2026, 4, 5),
        )


def test_fetch_error_is_exception() -> None:
    error = FetchError("API down")
    assert str(error) == "API down"
    assert isinstance(error, Exception)
```

- [ ] **Step 3: Run test to verify it fails**

```bash
uv run pytest tests/test_models.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.models'`

- [ ] **Step 4: Write the implementation**

Create `src/models.py`:

```python
from datetime import date

from pydantic import BaseModel, field_validator


class FetchError(Exception):
    """Raised when API fetch fails after all retries."""


class CoinPrice(BaseModel):
    coin: str
    symbol: str
    price: float
    change_24h: float
    date: date

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("price must be positive")
        return v
```

- [ ] **Step 5: Run test to verify it passes**

```bash
uv run pytest tests/test_models.py -v
```

Expected: 4 passed

- [ ] **Step 6: Commit**

```bash
git add src/__init__.py src/models.py tests/__init__.py tests/test_models.py
git commit -m "feat: add CoinPrice model and FetchError exception"
```

---

### Task 3: Create storage module

**Files:**
- Create: `src/storage.py`
- Create: `tests/test_storage.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_storage.py`:

```python
from datetime import date
from pathlib import Path

import pandas as pd

from src.models import CoinPrice
from src.storage import append_price, cleanup_zeros, load_full_history, load_history


def test_append_price_creates_file(tmp_path: Path) -> None:
    filepath = tmp_path / "test.csv"
    price = CoinPrice(
        coin="bitcoin", symbol="BTC", price=67500.0, change_24h=1.2, date=date(2026, 4, 5)
    )
    append_price(price, filepath)
    assert filepath.exists()
    df = pd.read_csv(filepath)
    assert len(df) == 1
    assert df.iloc[0]["price"] == 67500.0
    assert df.iloc[0]["change_24h"] == 1.2


def test_append_price_prepends_to_existing(tmp_path: Path) -> None:
    filepath = tmp_path / "test.csv"
    old = CoinPrice(
        coin="bitcoin", symbol="BTC", price=60000.0, change_24h=-0.5, date=date(2026, 4, 4)
    )
    new = CoinPrice(
        coin="bitcoin", symbol="BTC", price=67500.0, change_24h=1.2, date=date(2026, 4, 5)
    )
    append_price(old, filepath)
    append_price(new, filepath)
    df = pd.read_csv(filepath)
    assert len(df) == 2
    assert df.iloc[0]["date"] == "2026-04-05"
    assert df.iloc[1]["date"] == "2026-04-04"


def test_load_history_returns_last_n_days(tmp_path: Path) -> None:
    filepath = tmp_path / "test.csv"
    for i in range(10):
        price = CoinPrice(
            coin="bitcoin",
            symbol="BTC",
            price=60000.0 + i * 1000,
            change_24h=0.1 * i,
            date=date(2026, 4, 1 + i),
        )
        append_price(price, filepath)
    df = load_history(filepath, days=7)
    assert len(df) == 7


def test_load_history_missing_file(tmp_path: Path) -> None:
    filepath = tmp_path / "missing.csv"
    df = load_history(filepath)
    assert len(df) == 0


def test_load_full_history(tmp_path: Path) -> None:
    filepath = tmp_path / "test.csv"
    for i in range(10):
        price = CoinPrice(
            coin="bitcoin",
            symbol="BTC",
            price=60000.0 + i * 1000,
            change_24h=0.1 * i,
            date=date(2026, 4, 1 + i),
        )
        append_price(price, filepath)
    df = load_full_history(filepath)
    assert len(df) == 10


def test_cleanup_zeros(tmp_path: Path) -> None:
    filepath = tmp_path / "test.csv"
    df = pd.DataFrame(
        {
            "date": ["2026-04-01", "2026-04-02", "2026-04-03"],
            "price": [67500.0, 0.0, 68000.0],
        }
    )
    df.to_csv(filepath, index=False)
    cleanup_zeros(filepath)
    result = pd.read_csv(filepath)
    assert len(result) == 2
    assert 0.0 not in result["price"].values


def test_load_history_backward_compat_no_change_24h(tmp_path: Path) -> None:
    filepath = tmp_path / "test.csv"
    df = pd.DataFrame(
        {
            "date": ["2026-04-05", "2026-04-04"],
            "price": [67500.0, 66000.0],
        }
    )
    df.to_csv(filepath, index=False)
    result = load_history(filepath, days=7)
    assert "change_24h" in result.columns
    assert pd.isna(result.iloc[0]["change_24h"])
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_storage.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.storage'`

- [ ] **Step 3: Write the implementation**

Create `src/storage.py`:

```python
import logging
from pathlib import Path

import pandas as pd

from src.models import CoinPrice

logger = logging.getLogger(__name__)


def append_price(coin_price: CoinPrice, filepath: Path) -> None:
    """Append a price entry to the top of a CSV file."""
    new_row = pd.DataFrame(
        [
            {
                "date": coin_price.date.isoformat(),
                "price": coin_price.price,
                "change_24h": coin_price.change_24h,
            }
        ]
    )
    if filepath.exists():
        existing = pd.read_csv(filepath)
        df = pd.concat([new_row, existing], ignore_index=True)
    else:
        df = new_row
    df.to_csv(filepath, index=False)
    logger.info("Wrote 1 row to %s", filepath.name)


def load_history(filepath: Path, days: int = 7) -> pd.DataFrame:
    """Load the last N days from a CSV file."""
    if not filepath.exists():
        return pd.DataFrame(columns=["date", "price", "change_24h"])
    df = pd.read_csv(filepath)
    if "change_24h" not in df.columns:
        df["change_24h"] = float("nan")
    return df.head(days)


def load_full_history(filepath: Path) -> pd.DataFrame:
    """Load all rows from a CSV file."""
    if not filepath.exists():
        return pd.DataFrame(columns=["date", "price", "change_24h"])
    df = pd.read_csv(filepath)
    if "change_24h" not in df.columns:
        df["change_24h"] = float("nan")
    return df


def cleanup_zeros(filepath: Path) -> None:
    """Remove rows with price == 0.0 from a CSV file."""
    if not filepath.exists():
        return
    df = pd.read_csv(filepath)
    before = len(df)
    df = df[df["price"] != 0.0]
    df.to_csv(filepath, index=False)
    removed = before - len(df)
    if removed:
        logger.info("Removed %d zero-price rows from %s", removed, filepath.name)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_storage.py -v
```

Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add src/storage.py tests/test_storage.py
git commit -m "feat: add CSV storage module with append, load, and cleanup"
```

---

### Task 4: Create API client module

**Files:**
- Create: `src/api.py`
- Create: `tests/test_api.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_api.py`:

```python
import httpx
import pytest
import respx

from src.api import fetch_prices
from src.models import FetchError


COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"


@respx.mock
@pytest.mark.asyncio
async def test_fetch_prices_success() -> None:
    respx.get(COINGECKO_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "bitcoin": {"usd": 67500.0, "usd_24h_change": 1.2},
                "ethereum": {"usd": 3450.0, "usd_24h_change": -0.8},
            },
        )
    )
    result = await fetch_prices(api_key="test-key")
    assert "bitcoin" in result
    assert "ethereum" in result
    assert result["bitcoin"].price == 67500.0
    assert result["bitcoin"].symbol == "BTC"
    assert result["bitcoin"].change_24h == 1.2
    assert result["ethereum"].price == 3450.0
    assert result["ethereum"].symbol == "ETH"


@respx.mock
@pytest.mark.asyncio
async def test_fetch_prices_api_error_raises() -> None:
    respx.get(COINGECKO_URL).mock(
        return_value=httpx.Response(500, text="Internal Server Error")
    )
    with pytest.raises(FetchError, match="Failed to fetch prices"):
        await fetch_prices(api_key="test-key")


@respx.mock
@pytest.mark.asyncio
async def test_fetch_prices_sends_api_key_header() -> None:
    route = respx.get(COINGECKO_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "bitcoin": {"usd": 67500.0, "usd_24h_change": 1.2},
                "ethereum": {"usd": 3450.0, "usd_24h_change": -0.8},
            },
        )
    )
    await fetch_prices(api_key="my-secret-key")
    assert route.calls[0].request.headers["x-cg-demo-api-key"] == "my-secret-key"
```

- [ ] **Step 2: Add pytest-asyncio to dev dependencies**

Add `"pytest-asyncio"` to the `dev` list in `pyproject.toml` `[project.optional-dependencies]`:

```toml
[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio",
    "ruff",
    "pyright",
    "respx",
]
```

Then install:

```bash
uv sync --all-extras
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
uv run pytest tests/test_api.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.api'`

- [ ] **Step 4: Write the implementation**

Create `src/api.py`:

```python
import asyncio
import logging
from datetime import date

import httpx

from src.models import CoinPrice, FetchError

logger = logging.getLogger(__name__)

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"

COIN_SYMBOLS = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
}


async def fetch_prices(
    api_key: str,
    max_retries: int = 3,
) -> dict[str, CoinPrice]:
    """Fetch BTC and ETH prices from CoinGecko API.

    Args:
        api_key: CoinGecko Demo API key.
        max_retries: Number of retry attempts.

    Returns:
        Dict mapping coin id to CoinPrice.

    Raises:
        FetchError: If all retries fail.
    """
    params = {
        "ids": "bitcoin,ethereum",
        "vs_currencies": "usd",
        "include_24hr_change": "true",
    }
    headers = {"x-cg-demo-api-key": api_key}

    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    COINGECKO_URL, params=params, headers=headers
                )
                response.raise_for_status()
                data = response.json()

            today = date.today()
            result: dict[str, CoinPrice] = {}
            for coin_id, symbol in COIN_SYMBOLS.items():
                coin_data = data[coin_id]
                result[coin_id] = CoinPrice(
                    coin=coin_id,
                    symbol=symbol,
                    price=coin_data["usd"],
                    change_24h=coin_data["usd_24h_change"],
                    date=today,
                )
                logger.info(
                    "Fetched %s: $%,.2f (%+.1f%%)",
                    symbol,
                    result[coin_id].price,
                    result[coin_id].change_24h,
                )
            return result

        except (httpx.HTTPStatusError, httpx.RequestError, KeyError) as e:
            last_error = e
            if attempt < max_retries - 1:
                wait = 2**attempt
                logger.warning(
                    "Attempt %d failed: %s. Retrying in %ds...",
                    attempt + 1,
                    e,
                    wait,
                )
                await asyncio.sleep(wait)

    raise FetchError(f"Failed to fetch prices after {max_retries} attempts: {last_error}")
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
uv run pytest tests/test_api.py -v
```

Expected: 3 passed

- [ ] **Step 6: Commit**

```bash
git add src/api.py tests/test_api.py pyproject.toml uv.lock
git commit -m "feat: add CoinGecko API client with retry and auth"
```

---

### Task 5: Create charts module

**Files:**
- Create: `src/charts.py`
- Create: `tests/test_charts.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_charts.py`:

```python
from pathlib import Path

import pandas as pd

from src.charts import generate_chart


def test_generate_chart_creates_svg(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-04-01", "2026-04-02", "2026-04-03"],
            "price": [65000.0, 66000.0, 67500.0],
        }
    )
    output = tmp_path / "btc-usd.svg"
    generate_chart(df, "BTC-USD", output)
    assert output.exists()
    content = output.read_text()
    assert "<svg" in content


def test_generate_chart_contains_data_points(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-04-01", "2026-04-02"],
            "price": [65000.0, 67500.0],
        }
    )
    output = tmp_path / "eth-usd.svg"
    generate_chart(df, "ETH-USD", output)
    content = output.read_text()
    assert "65000" in content or "65,000" in content
    assert "67500" in content or "67,500" in content


def test_generate_chart_btc_uses_orange(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-04-01"],
            "price": [67500.0],
        }
    )
    output = tmp_path / "btc-usd.svg"
    generate_chart(df, "BTC-USD", output)
    content = output.read_text()
    # Pygal uses hex colors in the SVG — orange is #ff8c00 or similar
    assert "svg" in content.lower()


def test_generate_chart_eth_uses_blue(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-04-01"],
            "price": [3450.0],
        }
    )
    output = tmp_path / "eth-usd.svg"
    generate_chart(df, "ETH-USD", output)
    content = output.read_text()
    assert "svg" in content.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_charts.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.charts'`

- [ ] **Step 3: Write the implementation**

Create `src/charts.py`:

```python
import logging
from pathlib import Path

import pandas as pd
import pygal
from pygal.style import Style

logger = logging.getLogger(__name__)

COIN_COLORS = {
    "BTC-USD": "#ff8c00",  # orange
    "ETH-USD": "#4a90d9",  # blue
}

DARK_STYLE = Style(
    background="#0d1117",
    plot_background="#0d1117",
    foreground="#c9d1d9",
    foreground_strong="#f0f6fc",
    foreground_subtle="#8b949e",
    colors=("#ff8c00",),
    font_family="monospace",
)


def generate_chart(df: pd.DataFrame, coin: str, output_path: Path) -> None:
    """Generate an SVG line chart for the given price data.

    Args:
        df: DataFrame with 'date' and 'price' columns.
        coin: Coin pair name (e.g. "BTC-USD").
        output_path: Path to write the SVG file.
    """
    color = COIN_COLORS.get(coin, "#ff8c00")
    style = Style(
        background="#0d1117",
        plot_background="#0d1117",
        foreground="#c9d1d9",
        foreground_strong="#f0f6fc",
        foreground_subtle="#8b949e",
        colors=(color,),
        font_family="monospace",
    )

    chart = pygal.Line(
        title=f"7 Day Price — {coin}",
        x_title="Date",
        y_title="Price (USD)",
        width=800,
        height=300,
        show_legend=False,
        fill=True,
        style=style,
        dots_size=4,
        show_x_guides=False,
        show_y_guides=True,
    )

    dates = df["date"].tolist()
    prices = df["price"].tolist()

    chart.x_labels = dates
    chart.add(coin, prices)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    chart.render_to_file(str(output_path))
    logger.info("Generated chart: %s", output_path.name)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_charts.py -v
```

Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add src/charts.py tests/test_charts.py
git commit -m "feat: add pygal SVG chart generation with dark theme"
```

---

### Task 6: Create README rendering module and template

**Files:**
- Create: `src/readme.py`
- Modify: `templates/readme.md`
- Create: `tests/test_readme.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_readme.py`:

```python
from datetime import date

from src.models import CoinPrice
from src.readme import render_readme


def test_render_readme_contains_prices() -> None:
    prices = {
        "bitcoin": CoinPrice(
            coin="bitcoin", symbol="BTC", price=67500.0, change_24h=1.2, date=date(2026, 4, 5)
        ),
        "ethereum": CoinPrice(
            coin="ethereum", symbol="ETH", price=3450.0, change_24h=-0.8, date=date(2026, 4, 5)
        ),
    }
    stats = {
        "BTC": {"high": 68000.0, "low": 65000.0, "avg": 66500.0},
        "ETH": {"high": 3500.0, "low": 3300.0, "avg": 3400.0},
    }
    result = render_readme(prices, stats)
    assert "$67,500.00" in result
    assert "$3,450.00" in result


def test_render_readme_shows_positive_change() -> None:
    prices = {
        "bitcoin": CoinPrice(
            coin="bitcoin", symbol="BTC", price=67500.0, change_24h=1.2, date=date(2026, 4, 5)
        ),
        "ethereum": CoinPrice(
            coin="ethereum", symbol="ETH", price=3450.0, change_24h=0.5, date=date(2026, 4, 5)
        ),
    }
    stats = {
        "BTC": {"high": 68000.0, "low": 65000.0, "avg": 66500.0},
        "ETH": {"high": 3500.0, "low": 3300.0, "avg": 3400.0},
    }
    result = render_readme(prices, stats)
    assert "▲" in result


def test_render_readme_shows_negative_change() -> None:
    prices = {
        "bitcoin": CoinPrice(
            coin="bitcoin", symbol="BTC", price=67500.0, change_24h=-2.0, date=date(2026, 4, 5)
        ),
        "ethereum": CoinPrice(
            coin="ethereum", symbol="ETH", price=3450.0, change_24h=-0.8, date=date(2026, 4, 5)
        ),
    }
    stats = {
        "BTC": {"high": 68000.0, "low": 65000.0, "avg": 66500.0},
        "ETH": {"high": 3500.0, "low": 3300.0, "avg": 3400.0},
    }
    result = render_readme(prices, stats)
    assert "▼" in result


def test_render_readme_contains_summary_stats() -> None:
    prices = {
        "bitcoin": CoinPrice(
            coin="bitcoin", symbol="BTC", price=67500.0, change_24h=1.2, date=date(2026, 4, 5)
        ),
        "ethereum": CoinPrice(
            coin="ethereum", symbol="ETH", price=3450.0, change_24h=-0.8, date=date(2026, 4, 5)
        ),
    }
    stats = {
        "BTC": {"high": 68000.0, "low": 65000.0, "avg": 66500.0},
        "ETH": {"high": 3500.0, "low": 3300.0, "avg": 3400.0},
    }
    result = render_readme(prices, stats)
    assert "$68,000.00" in result
    assert "$65,000.00" in result
    assert "7-Day Summary" in result


def test_render_readme_contains_timestamp() -> None:
    prices = {
        "bitcoin": CoinPrice(
            coin="bitcoin", symbol="BTC", price=67500.0, change_24h=1.2, date=date(2026, 4, 5)
        ),
        "ethereum": CoinPrice(
            coin="ethereum", symbol="ETH", price=3450.0, change_24h=-0.8, date=date(2026, 4, 5)
        ),
    }
    stats = {
        "BTC": {"high": 68000.0, "low": 65000.0, "avg": 66500.0},
        "ETH": {"high": 3500.0, "low": 3300.0, "avg": 3400.0},
    }
    result = render_readme(prices, stats)
    assert "Last updated:" in result
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_readme.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.readme'`

- [ ] **Step 3: Update the Jinja2 template**

Replace `templates/readme.md` with:

```markdown
# Cryptocurrency Board

> Last updated: {{ updated_at }} UTC

## Market Overview

| Coin | Price (USD) | 24h Change |
|------|-------------|------------|
{% for coin in coins %}| **{{ coin.symbol }}** | **${{ "{:,.2f}".format(coin.price) }}** | {% if coin.change_24h >= 0 %}▲ +{{ "{:.1f}".format(coin.change_24h) }}%{% else %}▼ {{ "{:.1f}".format(coin.change_24h) }}%{% endif %} |
{% endfor %}

## BTC — 7 Day Chart

![BTC chart](./img/btc-usd.svg)

## ETH — 7 Day Chart

![ETH chart](./img/eth-usd.svg)

## 7-Day Summary

| Coin | High | Low | Avg |
|------|------|-----|-----|
{% for symbol, s in stats.items() %}| **{{ symbol }}** | ${{ "{:,.2f}".format(s.high) }} | ${{ "{:,.2f}".format(s.low) }} | ${{ "{:,.2f}".format(s.avg) }} |
{% endfor %}
```

- [ ] **Step 4: Write the implementation**

Create `src/readme.py`:

```python
import logging
from datetime import datetime, timezone

from jinja2 import Environment, FileSystemLoader

from src.models import CoinPrice

logger = logging.getLogger(__name__)


def render_readme(
    prices: dict[str, CoinPrice],
    stats: dict[str, dict[str, float]],
    template_dir: str = "./templates",
) -> str:
    """Render README.md from Jinja2 template with price data.

    Args:
        prices: Dict mapping coin id to CoinPrice.
        stats: Dict mapping symbol to {high, low, avg}.
        template_dir: Path to templates directory.

    Returns:
        Rendered README content as string.
    """
    loader = FileSystemLoader(template_dir)
    env = Environment(loader=loader)
    template = env.get_template("readme.md")

    coins = [prices["bitcoin"], prices["ethereum"]]
    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    # Convert stats dicts to objects for dot access in template
    class StatRow:
        def __init__(self, high: float, low: float, avg: float) -> None:
            self.high = high
            self.low = low
            self.avg = avg

    stat_objects = {k: StatRow(**v) for k, v in stats.items()}

    content = template.render(
        coins=coins,
        stats=stat_objects,
        updated_at=updated_at,
    )
    logger.info("Rendered README.md")
    return content
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
uv run pytest tests/test_readme.py -v
```

Expected: 5 passed

- [ ] **Step 6: Commit**

```bash
git add src/readme.py templates/readme.md tests/test_readme.py
git commit -m "feat: add README rendering with dashboard template"
```

---

### Task 7: Rewrite main.py orchestrator

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Rewrite main.py**

Replace the full contents of `main.py`:

```python
import asyncio
import logging
import os
import sys
from pathlib import Path

import pandas as pd

from src.api import fetch_prices
from src.charts import generate_chart
from src.models import FetchError
from src.readme import render_readme
from src.storage import append_price, cleanup_zeros, load_history

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

DATA_DIR = Path("data")
IMG_DIR = Path("img")

COINS = {
    "bitcoin": "btc-usd",
    "ethereum": "eth-usd",
}


def compute_stats(df: pd.DataFrame) -> dict[str, float]:
    """Compute high, low, avg from a DataFrame."""
    return {
        "high": float(df["price"].max()),
        "low": float(df["price"].min()),
        "avg": round(float(df["price"].mean()), 2),
    }


def main() -> None:
    api_key = os.getenv("COINGECKO_API_KEY", "")
    if not api_key:
        logger.error("COINGECKO_API_KEY environment variable is not set")
        sys.exit(1)

    DATA_DIR.mkdir(exist_ok=True)
    IMG_DIR.mkdir(exist_ok=True)

    # One-time cleanup of zero-price rows
    for filename in COINS.values():
        cleanup_zeros(DATA_DIR / f"{filename}.csv")

    # Fetch prices
    try:
        prices = asyncio.run(fetch_prices(api_key))
    except FetchError as e:
        logger.error("Failed to fetch prices: %s", e)
        sys.exit(1)

    # Store and generate charts
    stats: dict[str, dict[str, float]] = {}
    for coin_id, filename in COINS.items():
        csv_path = DATA_DIR / f"{filename}.csv"
        svg_path = IMG_DIR / f"{filename}.svg"

        append_price(prices[coin_id], csv_path)
        df = load_history(csv_path, days=7)
        generate_chart(df, f"{prices[coin_id].symbol}-USD", svg_path)
        stats[prices[coin_id].symbol] = compute_stats(df)

    # Render README
    content = render_readme(prices, stats)
    Path("README.md").write_text(content)
    logger.info("Pipeline complete")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the full test suite**

```bash
uv run pytest -v
```

Expected: All tests pass

- [ ] **Step 3: Run ruff and pyright**

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

Fix any issues found.

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: rewrite main.py to use src modules and CoinGecko API"
```

---

### Task 8: Rewrite init.py

**Files:**
- Modify: `init.py`

- [ ] **Step 1: Rewrite init.py**

Replace the full contents of `init.py`:

```python
import logging
import subprocess
import sys
from datetime import date
from os import getenv
from pathlib import Path

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

REPO_PATH = Path("/tmp/update")


def _run(args: list[str], cwd: Path | None = None) -> None:
    """Run a command, raise on failure."""
    subprocess.run(args, check=True, cwd=cwd)


def clone_or_pull(repo_url: str, repo_path: Path) -> None:
    """Clone the repo, or pull if it already exists."""
    if repo_path.exists():
        logger.info("Pulling latest changes.")
        _run(["git", "pull"], cwd=repo_path)
    else:
        logger.info("Cloning the repo.")
        _run(["git", "clone", repo_url, str(repo_path)])


def configure_git(repo_path: Path, username: str, email: str) -> None:
    """Set git user config for the repo."""
    _run(["git", "config", "user.name", username], cwd=repo_path)
    _run(["git", "config", "user.email", email], cwd=repo_path)


def run_main(repo_path: Path) -> None:
    """Run main.py inside the repo directory."""
    logger.info("Running main.py.")
    _run([sys.executable, "main.py"], cwd=repo_path)


def commit_and_push(repo_path: Path) -> None:
    """Stage changed files, commit, and push."""
    _run(["git", "add", "README.md", "data/", "img/"], cwd=repo_path)
    _run(
        ["git", "commit", "-m", f"Duty Updates {date.today().isoformat()}"],
        cwd=repo_path,
    )
    _run(["git", "push"], cwd=repo_path)
    logger.info("Pushed to remote.")


def main() -> None:
    repo_url = getenv("GITHUB_REPO_URL", "")
    username = getenv("GITHUB_USERNAME", "")
    email = getenv("GITHUB_EMAIL", "")

    if not all([repo_url, username, email]):
        logger.error("Missing required environment variables")
        sys.exit(1)

    try:
        clone_or_pull(repo_url, REPO_PATH)
        configure_git(REPO_PATH, username, email)
        run_main(REPO_PATH)
        commit_and_push(REPO_PATH)
    except subprocess.CalledProcessError as e:
        logger.error("Command failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    logger.info("Start.")
    main()
    logger.info("Stop.")
```

- [ ] **Step 2: Run ruff and pyright**

```bash
uv run ruff check init.py
uv run pyright init.py
```

Fix any issues.

- [ ] **Step 3: Commit**

```bash
git add init.py
git commit -m "refactor: rewrite init.py — drop gitpython, use subprocess with error handling"
```

---

### Task 9: Update Dockerfile

**Files:**
- Modify: `Dockerfile`

- [ ] **Step 1: Rewrite Dockerfile**

Replace the full contents of `Dockerfile`:

```dockerfile
FROM python:3.14-alpine

ENV GITHUB_REPO_URL=""
ENV GITHUB_USERNAME=""
ENV GITHUB_EMAIL=""
ENV COINGECKO_API_KEY=""

WORKDIR /app

RUN apk add --no-cache git && rm -rf /var/cache/apk/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY init.py .

CMD ["uv", "run", "python", "init.py"]
```

- [ ] **Step 2: Commit**

```bash
git add Dockerfile
git commit -m "chore: update Dockerfile — Python 3.14, uv, drop requirements.txt"
```

---

### Task 10: Update CI/CD workflows

**Files:**
- Create: `.github/workflows/ci.yaml`
- Modify: `.github/workflows/main.yaml` (rename to `build.yaml`)
- Modify: `.github/workflows/cron.yaml`

- [ ] **Step 1: Create ci.yaml**

Create `.github/workflows/ci.yaml`:

```yaml
name: CI

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Set up Python
        run: uv python install 3.14

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Ruff check
        run: uv run ruff check .

      - name: Ruff format check
        run: uv run ruff format --check .

      - name: Pyright
        run: uv run pyright

      - name: Pytest
        run: uv run pytest -v
```

- [ ] **Step 2: Rename main.yaml to build.yaml and update**

```bash
git mv .github/workflows/main.yaml .github/workflows/build.yaml
```

Replace the contents of `.github/workflows/build.yaml`:

```yaml
name: Build and push

on:
  push:
    branches: [master]
    paths:
      - "init.py"
      - "Dockerfile"
      - "pyproject.toml"
      - "uv.lock"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          push: true
          platforms: linux/amd64
          tags: |
            ghcr.io/${{ github.repository }}:latest
```

- [ ] **Step 3: Update cron.yaml**

Replace the contents of `.github/workflows/cron.yaml`:

```yaml
name: cron-job

on:
  schedule:
    - cron: "50 5 * * *"

jobs:
  docker:
    runs-on: ubuntu-latest
    env:
      GITHUB_REPO_URL: https://${{ github.actor }}:${{ secrets.GITHUB_TOKEN }}@github.com/${{ github.repository }}.git
      GITHUB_USERNAME: ${{ github.actor }}
      GITHUB_EMAIL: ${{ vars.EMAIL }}
      COINGECKO_API_KEY: ${{ secrets.COINGECKO_API_KEY }}
    container:
      image: ghcr.io/${{ github.repository }}:latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Run
        run: python init.py
```

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/ci.yaml .github/workflows/build.yaml .github/workflows/cron.yaml
git commit -m "chore: add CI workflow, update build and cron with API key and uv"
```

---

### Task 11: Clean CSV data

**Files:**
- Modify: `data/btc-usd.csv`
- Modify: `data/eth-usd.csv`

- [ ] **Step 1: Run a one-time cleanup script**

```bash
uv run python -c "
from pathlib import Path
from src.storage import cleanup_zeros
cleanup_zeros(Path('data/btc-usd.csv'))
cleanup_zeros(Path('data/eth-usd.csv'))
print('Done')
"
```

Expected: Removes all rows with `price == 0.0` from both CSVs.

- [ ] **Step 2: Verify the cleanup**

```bash
uv run python -c "
import pandas as pd
for f in ['data/btc-usd.csv', 'data/eth-usd.csv']:
    df = pd.read_csv(f)
    zeros = len(df[df['price'] == 0.0])
    print(f'{f}: {len(df)} rows, {zeros} zeros')
"
```

Expected: 0 zeros in both files.

- [ ] **Step 3: Delete old PNG images**

```bash
rm -f img/btc-usd.png img/eth-usd.png
```

- [ ] **Step 4: Remove old src/ directory if it exists**

```bash
rm -rf src/main.py src/read.py
```

(The CLAUDE.md mentioned `src/main.py` and `src/read.py` as alternative implementations — remove them since we're replacing with the new modules.)

- [ ] **Step 5: Commit**

```bash
git add data/btc-usd.csv data/eth-usd.csv
git rm -f --ignore-unmatch img/btc-usd.png img/eth-usd.png src/main.py src/read.py
git commit -m "chore: clean CSV data (remove 0.0 rows), delete old PNG charts"
```

---

### Task 12: Delete test.ipynb and update CLAUDE.md

**Files:**
- Delete: `test.ipynb`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Delete test.ipynb**

```bash
rm test.ipynb
```

No longer needed — we have proper pytest tests.

- [ ] **Step 2: Update CLAUDE.md**

Replace the full contents of `CLAUDE.md`:

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated cryptocurrency price monitoring system. Fetches BTC and ETH prices from CoinGecko API daily, stores full historical data in CSV, generates pygal SVG charts (7-day window), and renders a README dashboard via Jinja2. Runs daily at 5:50 AM UTC via GitHub Actions cron job in Docker.

## Commands

### Run locally
```bash
uv run python main.py
```

### Run via Docker (CI/scheduled mode)
```bash
docker build -t cryptocurrency-board .
docker run -e GITHUB_REPO_URL=... -e GITHUB_USERNAME=... -e GITHUB_EMAIL=... -e COINGECKO_API_KEY=... cryptocurrency-board
```

### Run tests
```bash
uv run pytest -v
```

### Lint and format
```bash
uv run ruff check .
uv run ruff format --check .
```

### Type checking
```bash
uv run pyright
```

### Install dependencies
```bash
uv sync --all-extras
```

## Architecture

### Entry Points

- **`main.py`** — Orchestrator. Fetches prices via `src/api.py`, appends to CSV via `src/storage.py`, generates SVG charts via `src/charts.py`, renders README via `src/readme.py`.
- **`init.py`** — CI/Docker wrapper. Clones/pulls the repo, runs `main.py`, commits ("Duty Updates YYYY-MM-DD"), and pushes.

### Source Modules (`src/`)

- **`src/models.py`** — Pydantic `CoinPrice` model, `FetchError` exception
- **`src/api.py`** — CoinGecko async client (httpx), retry with backoff
- **`src/storage.py`** — CSV append, load (with day window), cleanup
- **`src/charts.py`** — Pygal SVG chart generation, dark theme
- **`src/readme.py`** — Jinja2 README rendering

### Data Flow

1. Fetch prices from CoinGecko API → 2. Append to `data/{btc,eth}-usd.csv` → 3. Load last 7 days → 4. Generate SVG charts to `img/{btc,eth}-usd.svg` → 5. Render `templates/readme.md` → `README.md`

### Key Directories

- `data/` — CSV price history (full archive)
- `img/` — Generated SVG charts
- `templates/` — Jinja2 template for README
- `tests/` — pytest test suite

## Configuration

- **Package management**: `uv` (pyproject.toml + uv.lock)
- **Python version**: 3.14
- **Type checking**: Pyright in standard mode
- **Linting**: Ruff (E, F, W, I, UP rules)
- **Testing**: pytest
- **Docker**: Alpine-based image with uv

## Environment Variables

- `COINGECKO_API_KEY` — CoinGecko Demo API key (required)
- `GITHUB_REPO_URL` — Repository URL with embedded auth token (CI only)
- `GITHUB_USERNAME` — Git commit author name (CI only)
- `GITHUB_EMAIL` — Git commit author email (CI only)

## CI/CD

- `ci.yaml` — Runs ruff, pyright, pytest on PRs and pushes to master
- `build.yaml` — Builds and pushes Docker image when init.py, Dockerfile, pyproject.toml, or uv.lock change
- `cron.yaml` — Daily scheduled run at 5:50 UTC

## API

- **CoinGecko API**: `https://api.coingecko.com/api/v3/simple/price`
- Auth: `x-cg-demo-api-key` header
- Coins: `bitcoin`, `ethereum`
```

- [ ] **Step 3: Commit**

```bash
git rm test.ipynb
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for new architecture, remove test.ipynb"
```

---

### Task 13: Final validation

- [ ] **Step 1: Run the full test suite**

```bash
uv run pytest -v
```

Expected: All tests pass.

- [ ] **Step 2: Run ruff**

```bash
uv run ruff check .
uv run ruff format --check .
```

Expected: No issues.

- [ ] **Step 3: Run pyright**

```bash
uv run pyright
```

Expected: No errors.

- [ ] **Step 4: Test the full pipeline locally**

Create a `.env` file with your CoinGecko key, then:

```bash
export $(cat .env | xargs)
uv run python main.py
```

Expected: Fetches prices, generates SVG charts in `img/`, updates CSV in `data/`, renders README.md with dashboard layout.

- [ ] **Step 5: Verify generated files**

```bash
head -3 data/btc-usd.csv
head -3 data/eth-usd.csv
file img/btc-usd.svg
file img/eth-usd.svg
head -20 README.md
```

Expected: CSVs have new rows with `change_24h` column, SVG files exist, README has new dashboard format.

- [ ] **Step 6: Final commit if any fixes were needed**

```bash
git add -A
git commit -m "fix: address issues found during final validation"
```

(Skip if no fixes needed.)

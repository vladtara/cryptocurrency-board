# CLAUDE.md

## Project Overview

Cryptocurrency-board is an automated cryptocurrency price monitoring and visualization system. It fetches real-time BTC and ETH prices from the Blockchain.com API, maintains 7-day rolling historical data in CSV files, generates Matplotlib charts, and auto-generates a README with current prices and embedded charts. A GitHub Actions cron job runs daily at 5:50 AM UTC via Docker.

## Tech Stack

- **Language**: Python 3.12 (Alpine Docker image)
- **Async HTTP**: aiohttp + asyncio
- **Data**: pandas (CSV read/write), pydantic (API response validation)
- **Visualization**: matplotlib
- **Templating**: jinja2 (README generation from `templates/readme.md`)
- **Date/Time**: pendulum
- **Git Automation**: gitpython
- **CI/CD**: GitHub Actions, Docker, GitHub Container Registry (ghcr.io)

## Project Structure

```
main.py          # Core logic: fetch prices, update CSVs, generate charts, render README
init.py          # Git automation: clone/pull, run main.py, commit and push
data/            # CSV files (btc-usd.csv, eth-usd.csv) - 7-day rolling price history
img/             # Generated PNG charts (btc-usd.png, eth-usd.png)
templates/       # Jinja2 template for README.md generation
.github/workflows/
  cron.yaml      # Daily scheduled job (5:50 AM UTC)
  main.yaml      # Docker build and push on master changes
```

## Build & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main pipeline (fetch, chart, render)
python main.py

# Run with git automation (used in Docker/CI)
python init.py
```

## Docker

```bash
docker build -t cryptocurrency-board .
docker run --env GITHUB_REPO_URL="..." --env GITHUB_USERNAME="..." --env GITHUB_EMAIL="..." cryptocurrency-board
```

## Environment Variables (for init.py / CI)

- `GITHUB_REPO_URL` - Repository URL with auth token
- `GITHUB_USERNAME` - Git commit author name
- `GITHUB_EMAIL` - Git commit author email

## Code Conventions

- PEP 8 style, 4-space indentation
- Full type annotations on function parameters and return types
- Google-style docstrings with Args/Returns sections
- snake_case for functions/variables, PascalCase for classes
- Async context managers for HTTP sessions
- No formal test suite; `test.ipynb` used for manual/exploratory validation

## Key Patterns

- **Data pipeline**: async fetch -> pydantic validation -> pandas CSV append -> matplotlib chart -> jinja2 README
- **Pydantic BaseModel** (`Data` class) validates API response structure
- **7-day rolling window**: CSVs are sorted by date and trimmed to last 7 entries
- **Atomic git commits**: `init.py` stages only specific files (README.md, data/*, img/*)
- **Commit messages**: Format is `Duty Updates YYYY-MM-DD`

## API

- Endpoint: `https://api.blockchain.com/v3/exchange/tickers/{symbol}`
- Symbols: `BTC-USD`, `ETH-USD`
- Response field used: `last_trade_price`

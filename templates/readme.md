# Cryptocurrency Board

> Last updated: {{ updated_at }} UTC

## Market Overview

| Coin | Price (USD) | 24h Change |
|------|-------------|------------|
{% for coin in coins %}| **{{ coin.symbol }}** | **${{ "{:,.2f}".format(coin.price) }}** | {% if coin.change_24h >= 0 %}▲ +{{ "{:.1f}".format(coin.change_24h) }}%{% else %}▼ {{ "{:.1f}".format(coin.change_24h) }}%{% endif %} |
{% endfor %}

## Multi-Window Summary

{% for window_label, window in window_rows.items() %}
### {{ window_label }}

| Coin | Min | Max | Avg | Median | Return % | Volatility |
|------|-----|-----|-----|--------|----------|------------|
| **BTC** | ${{ "{:,.2f}".format(window.BTC.min) }} | ${{ "{:,.2f}".format(window.BTC.max) }} | ${{ "{:,.2f}".format(window.BTC.avg) }} | ${{ "{:,.2f}".format(window.BTC.median) }} | {{ "{:+.1f}".format(window.BTC.return_pct) }}% | {{ "{:.2f}".format(window.BTC.volatility) }}% |
| **ETH** | ${{ "{:,.2f}".format(window.ETH.min) }} | ${{ "{:,.2f}".format(window.ETH.max) }} | ${{ "{:,.2f}".format(window.ETH.avg) }} | ${{ "{:,.2f}".format(window.ETH.median) }} | {{ "{:+.1f}".format(window.ETH.return_pct) }}% | {{ "{:.2f}".format(window.ETH.volatility) }}% |

{% endfor %}

## BTC Charts

{% for chart in charts.BTC %}![BTC {{ chart.label }} chart]({{ chart.path }})

{% endfor %}

## ETH Charts

{% for chart in charts.ETH %}![ETH {{ chart.label }} chart]({{ chart.path }})

{% endfor %}

{% if "1Y" in window_rows %}
## Deep Stats

### 1Y

| Coin | Range % | Drawdown % |
|------|---------|------------|
| **BTC** | {{ "{:.1f}".format(window_rows["1Y"].BTC.range_pct) }}% | {{ "{:.1f}".format(window_rows["1Y"].BTC.drawdown_pct) }}% |
| **ETH** | {{ "{:.1f}".format(window_rows["1Y"].ETH.range_pct) }}% | {{ "{:.1f}".format(window_rows["1Y"].ETH.drawdown_pct) }}% |
{% endif %}

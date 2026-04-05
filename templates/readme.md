# Cryptocurrency Board

> Last updated: {{ updated_at }} UTC

## Market Overview

| Coin | Price (USD) | 24h Change |
|------|-------------|------------|
{% for coin in coins %}| **{{ coin.symbol }}** | **${{ "{:,.2f}".format(coin.price) }}** | {% if coin.change_24h >= 0 %}▲ +{{ "{:.1f}".format(coin.change_24h) }}%{% else %}▼ {{ "{:.1f}".format(coin.change_24h) }}%{% endif %} |
{% endfor %}

## 7-Day Dashboard

{% if "7D" in window_rows %}
| Coin | Min | Max | Avg | Median | Return % | Volatility |
|------|-----|-----|-----|--------|----------|------------|
| **BTC** | ${{ "{:,.2f}".format(window_rows["7D"].BTC.min) }} | ${{ "{:,.2f}".format(window_rows["7D"].BTC.max) }} | ${{ "{:,.2f}".format(window_rows["7D"].BTC.avg) }} | ${{ "{:,.2f}".format(window_rows["7D"].BTC.median) }} | {{ "{:+.1f}".format(window_rows["7D"].BTC.return_pct) }}% | {{ "{:.2f}".format(window_rows["7D"].BTC.volatility) }}% |
| **ETH** | ${{ "{:,.2f}".format(window_rows["7D"].ETH.min) }} | ${{ "{:,.2f}".format(window_rows["7D"].ETH.max) }} | ${{ "{:,.2f}".format(window_rows["7D"].ETH.avg) }} | ${{ "{:,.2f}".format(window_rows["7D"].ETH.median) }} | {{ "{:+.1f}".format(window_rows["7D"].ETH.return_pct) }}% | {{ "{:.2f}".format(window_rows["7D"].ETH.volatility) }}% |

{% for chart in charts.BTC %}{% if chart.label == "7D" %}![BTC 7D chart]({{ chart.path }})

{% endif %}{% endfor %}
{% for chart in charts.ETH %}{% if chart.label == "7D" %}![ETH 7D chart]({{ chart.path }})

{% endif %}{% endfor %}
{% endif %}

## Extended Windows

{% for window_label, window in window_rows.items() %}
{% if window_label != "7D" %}
### {{ window_label }}

| Coin | Min | Max | Avg | Median | Return % | Volatility |
|------|-----|-----|-----|--------|----------|------------|
| **BTC** | ${{ "{:,.2f}".format(window.BTC.min) }} | ${{ "{:,.2f}".format(window.BTC.max) }} | ${{ "{:,.2f}".format(window.BTC.avg) }} | ${{ "{:,.2f}".format(window.BTC.median) }} | {{ "{:+.1f}".format(window.BTC.return_pct) }}% | {{ "{:.2f}".format(window.BTC.volatility) }}% |
| **ETH** | ${{ "{:,.2f}".format(window.ETH.min) }} | ${{ "{:,.2f}".format(window.ETH.max) }} | ${{ "{:,.2f}".format(window.ETH.avg) }} | ${{ "{:,.2f}".format(window.ETH.median) }} | {{ "{:+.1f}".format(window.ETH.return_pct) }}% | {{ "{:.2f}".format(window.ETH.volatility) }}% |

{% endif %}
{% endfor %}

## BTC Charts

{% for chart in charts.BTC %}{% if chart.label != "7D" %}![BTC {{ chart.label }} chart]({{ chart.path }})

{% endif %}{% endfor %}

## ETH Charts

{% for chart in charts.ETH %}{% if chart.label != "7D" %}![ETH {{ chart.label }} chart]({{ chart.path }})

{% endif %}{% endfor %}

{% if "1Y" in window_rows %}
## Deep Stats

### 1Y

| Coin | Range % | Drawdown % |
|------|---------|------------|
| **BTC** | {{ "{:.1f}".format(window_rows["1Y"].BTC.range_pct) }}% | {{ "{:.1f}".format(window_rows["1Y"].BTC.drawdown_pct) }}% |
| **ETH** | {{ "{:.1f}".format(window_rows["1Y"].ETH.range_pct) }}% | {{ "{:.1f}".format(window_rows["1Y"].ETH.drawdown_pct) }}% |
{% endif %}

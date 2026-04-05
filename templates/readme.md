# Cryptocurrency Board

> Last updated: {{ updated_at }} UTC

## Market Overview

| Coin                    | Price (USD)           | 24h Change                              |
| ----------------------- | --------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| {% for coin in coins %} | **{{ coin.symbol }}** | **${{ "{:,.2f}".format(coin.price) }}** | {% if coin.change_24h >= 0 %}▲ +{{ "{:.1f}".format(coin.change_24h) }}%{% else %}▼ {{ "{:.1f}".format(coin.change_24h) }}%{% endif %} |

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

## 30D Dashboard

{% if "30D" in window_rows %}
| Coin | Min | Max | Avg | Median | Return % | Volatility |
|------|-----|-----|-----|--------|----------|------------|
| **BTC** | ${{ "{:,.2f}".format(window_rows["30D"].BTC.min) }} | ${{ "{:,.2f}".format(window_rows["30D"].BTC.max) }} | ${{ "{:,.2f}".format(window_rows["30D"].BTC.avg) }} | ${{ "{:,.2f}".format(window_rows["30D"].BTC.median) }} | {{ "{:+.1f}".format(window_rows["30D"].BTC.return_pct) }}% | {{ "{:.2f}".format(window_rows["30D"].BTC.volatility) }}% |
| **ETH** | ${{ "{:,.2f}".format(window_rows["30D"].ETH.min) }} | ${{ "{:,.2f}".format(window_rows["30D"].ETH.max) }} | ${{ "{:,.2f}".format(window_rows["30D"].ETH.avg) }} | ${{ "{:,.2f}".format(window_rows["30D"].ETH.median) }} | {{ "{:+.1f}".format(window_rows["30D"].ETH.return_pct) }}% | {{ "{:.2f}".format(window_rows["30D"].ETH.volatility) }}% |

![BTC 30D chart](./img/btc-usd-30d.svg)

![ETH 30D chart](./img/eth-usd-30d.svg)
{% endif %}

## 90D Dashboard

{% if "90D" in window_rows %}
| Coin | Min | Max | Avg | Median | Return % | Volatility |
|------|-----|-----|-----|--------|----------|------------|
| **BTC** | ${{ "{:,.2f}".format(window_rows["90D"].BTC.min) }} | ${{ "{:,.2f}".format(window_rows["90D"].BTC.max) }} | ${{ "{:,.2f}".format(window_rows["90D"].BTC.avg) }} | ${{ "{:,.2f}".format(window_rows["90D"].BTC.median) }} | {{ "{:+.1f}".format(window_rows["90D"].BTC.return_pct) }}% | {{ "{:.2f}".format(window_rows["90D"].BTC.volatility) }}% |
| **ETH** | ${{ "{:,.2f}".format(window_rows["90D"].ETH.min) }} | ${{ "{:,.2f}".format(window_rows["90D"].ETH.max) }} | ${{ "{:,.2f}".format(window_rows["90D"].ETH.avg) }} | ${{ "{:,.2f}".format(window_rows["90D"].ETH.median) }} | {{ "{:+.1f}".format(window_rows["90D"].ETH.return_pct) }}% | {{ "{:.2f}".format(window_rows["90D"].ETH.volatility) }}% |

![BTC 90D chart](./img/btc-usd-90d.svg)

![ETH 90D chart](./img/eth-usd-90d.svg)
{% endif %}

## 180D Dashboard

{% if "180D" in window_rows %}
| Coin | Min | Max | Avg | Median | Return % | Volatility |
|------|-----|-----|-----|--------|----------|------------|
| **BTC** | ${{ "{:,.2f}".format(window_rows["180D"].BTC.min) }} | ${{ "{:,.2f}".format(window_rows["180D"].BTC.max) }} | ${{ "{:,.2f}".format(window_rows["180D"].BTC.avg) }} | ${{ "{:,.2f}".format(window_rows["180D"].BTC.median) }} | {{ "{:+.1f}".format(window_rows["180D"].BTC.return_pct) }}% | {{ "{:.2f}".format(window_rows["180D"].BTC.volatility) }}% |
| **ETH** | ${{ "{:,.2f}".format(window_rows["180D"].ETH.min) }} | ${{ "{:,.2f}".format(window_rows["180D"].ETH.max) }} | ${{ "{:,.2f}".format(window_rows["180D"].ETH.avg) }} | ${{ "{:,.2f}".format(window_rows["180D"].ETH.median) }} | {{ "{:+.1f}".format(window_rows["180D"].ETH.return_pct) }}% | {{ "{:.2f}".format(window_rows["180D"].ETH.volatility) }}% |

![BTC 180D chart](./img/btc-usd-180d.svg)

![ETH 180D chart](./img/eth-usd-180d.svg)
{% endif %}

## 1Y Dashboard

{% if "1Y" in window_rows %}
| Coin | Min | Max | Avg | Median | Return % | Volatility |
|------|-----|-----|-----|--------|----------|------------|
| **BTC** | ${{ "{:,.2f}".format(window_rows["1Y"].BTC.min) }} | ${{ "{:,.2f}".format(window_rows["1Y"].BTC.max) }} | ${{ "{:,.2f}".format(window_rows["1Y"].BTC.avg) }} | ${{ "{:,.2f}".format(window_rows["1Y"].BTC.median) }} | {{ "{:+.1f}".format(window_rows["1Y"].BTC.return_pct) }}% | {{ "{:.2f}".format(window_rows["1Y"].BTC.volatility) }}% |
| **ETH** | ${{ "{:,.2f}".format(window_rows["1Y"].ETH.min) }} | ${{ "{:,.2f}".format(window_rows["1Y"].ETH.max) }} | ${{ "{:,.2f}".format(window_rows["1Y"].ETH.avg) }} | ${{ "{:,.2f}".format(window_rows["1Y"].ETH.median) }} | {{ "{:+.1f}".format(window_rows["1Y"].ETH.return_pct) }}% | {{ "{:.2f}".format(window_rows["1Y"].ETH.volatility) }}% |

![BTC 1Y chart](./img/btc-usd-1y.svg)

![ETH 1Y chart](./img/eth-usd-1y.svg)
{% endif %}

{% if "1Y" in window_rows %}

---

## Deep Stats

### 1Y

| Coin    | Range %                                                 | Drawdown %                                                 |
| ------- | ------------------------------------------------------- | ---------------------------------------------------------- |
| **BTC** | {{ "{:.1f}".format(window_rows["1Y"].BTC.range_pct) }}% | {{ "{:.1f}".format(window_rows["1Y"].BTC.drawdown_pct) }}% |
| **ETH** | {{ "{:.1f}".format(window_rows["1Y"].ETH.range_pct) }}% | {{ "{:.1f}".format(window_rows["1Y"].ETH.drawdown_pct) }}% |

{% endif %}

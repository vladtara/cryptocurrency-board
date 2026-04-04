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

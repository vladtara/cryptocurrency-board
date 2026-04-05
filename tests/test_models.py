from datetime import date

import pytest
from pydantic import ValidationError

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
    with pytest.raises(ValidationError):
        CoinPrice(
            coin="bitcoin",
            symbol="BTC",
            price=0.0,
            change_24h=0.0,
            date=date(2026, 4, 5),
        )


def test_coin_price_rejects_negative_price() -> None:
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

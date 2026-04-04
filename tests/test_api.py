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

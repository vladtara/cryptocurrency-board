import httpx
import pytest
import respx

import src.api as api_module
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
async def test_fetch_prices_logs_formatted_prices(
    caplog: pytest.LogCaptureFixture,
) -> None:
    respx.get(COINGECKO_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "bitcoin": {"usd": 66876.0, "usd_24h_change": -0.2357752960385911},
                "ethereum": {"usd": 3450.0, "usd_24h_change": 1.2},
            },
        )
    )

    with caplog.at_level("INFO", logger="src.api"):
        await fetch_prices(api_key="test-key")

    assert "Fetched BTC: $66,876.00 (-0.2%)" in caplog.text
    assert "Fetched ETH: $3,450.00 (+1.2%)" in caplog.text


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


@respx.mock
@pytest.mark.asyncio
async def test_fetch_prices_malformed_json_raises_fetch_error() -> None:
    respx.get(COINGECKO_URL).mock(return_value=httpx.Response(200, text="not json"))

    with pytest.raises(FetchError, match="Failed to fetch prices"):
        await fetch_prices(api_key="test-key", max_retries=1)


@respx.mock
@pytest.mark.asyncio
async def test_fetch_prices_retries_then_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sleep_calls: list[int] = []

    async def fake_sleep(delay: int) -> None:
        sleep_calls.append(delay)

    monkeypatch.setattr(api_module.asyncio, "sleep", fake_sleep)

    route = respx.get(COINGECKO_URL).mock(
        side_effect=[
            httpx.Response(500, text="Internal Server Error"),
            httpx.Response(
                200,
                json={
                    "bitcoin": {"usd": 67500.0, "usd_24h_change": 1.2},
                    "ethereum": {"usd": 3450.0, "usd_24h_change": -0.8},
                },
            ),
        ]
    )

    result = await fetch_prices(api_key="test-key")

    assert result["bitcoin"].price == 67500.0
    assert len(route.calls) == 2
    assert sleep_calls == [1]

import asyncio
import logging
from datetime import date

import httpx
from pydantic import ValidationError

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

        except (
            httpx.HTTPStatusError,
            httpx.RequestError,
            KeyError,
            ValidationError,
            ValueError,
        ) as e:
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

    raise FetchError(
        f"Failed to fetch prices after {max_retries} attempts: {last_error}"
    )

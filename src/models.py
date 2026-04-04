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

import aiohttp
import logging
from cachetools import TTLCache
from datetime import datetime

from conversion_service.config import CACHE_TTL, EXCHANGE_ACCESS_KEY, EXCHANGE_RATE_API_URL

# In-memory cache for exchange rates
exchange_rate_cache = TTLCache(maxsize=100, ttl=CACHE_TTL)


async def fetch_exchange_rate(from_currency: str, to_currency: str, date: str) -> float:
    """
    Fetch exchange rate from external API or cache if available.
    :param from_currency: Currency to convert from.
    :param to_currency: Currency to convert to.
    :param date: Date for which to fetch the exchange rate.
    :return: Exchange rate.
    """
    # Check if exchange rate is already cached
    cache_key = (from_currency, to_currency, date)
    if cache_key in exchange_rate_cache:
        logging.info(f"Using cached exchange rate for {from_currency} to {to_currency} on {date}")
        return exchange_rate_cache[cache_key]

    # Format date to match API requirements
    formatted_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")
    params = {
        "access_key": EXCHANGE_ACCESS_KEY,
        "from": from_currency,
        "to": to_currency,
        "amount": 1,
        "date": formatted_date
    }

    # Fetch exchange rate from API
    async with aiohttp.ClientSession() as session:
        async with session.get(EXCHANGE_RATE_API_URL, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('success'):
                    rate = data['result']
                    exchange_rate_cache[cache_key] = rate
                    logging.info(f"Fetched new exchange rate: {rate}")
                    return rate
                else:
                    raise ValueError(f"Failed to fetch exchange rate: {data.get('error')}")
            else:
                raise ValueError(f"Error fetching exchange rate: HTTP {response.status}")

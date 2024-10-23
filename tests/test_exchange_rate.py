from unittest import mock

import pytest
from cachetools import TTLCache

from conversion_service.exchange_rate_api import fetch_exchange_rate
from unittest.mock import patch


@pytest.mark.asyncio
async def test_fetch_exchange_rate_from_api():
    """
    Test fetching exchange rate from the API.
    """
    mock_response = {
        "success": True,
        "result": 0.82
    }

    # Patch aiohttp.ClientSession to mock API call
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.return_value.__aenter__.return_value.json = mock.AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value.status = 200

        test_cache = TTLCache(maxsize=100, ttl=600)  # Create an isolated cache for the test
        rate = await fetch_exchange_rate(
            from_currency='USD',
            to_currency='EUR',
            date='2021-05-18T21:32:42.324Z',
            cache=test_cache
        )

    assert rate == 0.82


@pytest.mark.asyncio
async def test_exchange_rate_cache():
    """
    Test exchange rate caching.
    """
    mock_response = {
        "success": True,
        "result": 0.82
    }

    # Patch aiohttp.ClientSession to mock API call
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.return_value.__aenter__.return_value.json = mock.AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value.status = 200

        test_cache = TTLCache(maxsize=100, ttl=600)  # Create an isolated cache for the test

        # First call to fetch from API
        rate = await fetch_exchange_rate(
            from_currency='USD',
            to_currency='EUR',
            date='2021-05-18T21:32:42.324Z',
            cache=test_cache
        )
        assert rate == 0.82

        # Second call should hit the cache, no API call should be made
        mock_get.reset_mock()  # Clear the mock call history
        cached_rate = await fetch_exchange_rate(
            from_currency='USD',
            to_currency='EUR',
            date='2021-05-18T21:32:42.324Z',
            cache=test_cache
        )
        assert cached_rate == 0.82
        mock_get.assert_not_called()

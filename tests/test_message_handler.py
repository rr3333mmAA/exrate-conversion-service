import pytest
from unittest.mock import patch
from conversion_service.message_handler import handle_conversion_request


@pytest.mark.asyncio
async def test_handle_conversion_success():
    """
    Test the successful conversion request.
    """
    with patch('conversion_service.exchange_rate_api.fetch_exchange_rate', return_value=0.82):
        message = {
            "type": "message",
            "id": 456,
            "payload": {
                "marketId": 123456,
                "selectionId": 987654,
                "odds": 2.2,
                "stake": 253.67,
                "currency": "USD",
                "date": "2021-05-18T21:32:42.324Z"
            }
        }

        response = await handle_conversion_request(message)

        assert response['type'] == 'message'
        assert response['payload']['stake'] == round(253.67 * 0.818185, 5)
        assert response['payload']['currency'] == 'EUR'


@pytest.mark.asyncio
async def test_handle_conversion_error():
    """
    Test the error handling in the conversion request.
    """
    with patch('conversion_service.exchange_rate_api.fetch_exchange_rate', side_effect=ValueError("Invalid currency")):
        message = {
            "type": "message",
            "id": 456,
            "payload": {
                "marketId": 123456,
                "selectionId": 987654,
                "odds": 2.2,
                "stake": 253.67,
                "currency": "INVALID",
                "date": "2021-05-18T21:32:42.324Z"
            }
        }

        response = await handle_conversion_request(message)

        assert response['type'] == 'error'
        assert "Unable to convert stake" in response['message']

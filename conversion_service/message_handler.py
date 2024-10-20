import logging
from datetime import datetime, UTC
from conversion_service.exchange_rate_api import fetch_exchange_rate


async def handle_conversion_request(message: dict) -> dict:
    """
    Handle incoming conversion request, calculate the updated stake, and return the response.
    :param message: Incoming message.
    :return: Response message.
    """
    try:
        payload = message['payload']
        from_currency = payload['currency']
        to_currency = "EUR"
        stake = payload['stake']
        date = payload['date']
        m_id = message['id']

        # Fetch exchange rate and convert stake
        rate = await fetch_exchange_rate(from_currency, to_currency, date)
        converted_stake = round(stake * rate, 5)

        # Prepare response message
        response = {
            "type": "message",
            "id": m_id,
            "payload": {
                "marketId": payload['marketId'],
                "selectionId": payload['selectionId'],
                "odds": payload['odds'],
                "stake": converted_stake,
                "currency": to_currency,
                "date": datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            }
        }
        return response

    except Exception as e:
        logging.error(f"Error handling conversion request: {str(e)}")
        return {
            "type": "error",
            "id": message['id'],
            "message": f"Unable to convert stake. Error: {str(e)}"
        }

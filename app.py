import asyncio
import logging

from conversion_service.config import CURRENCY_ASSIGNMENT_WS
from conversion_service.websocket_manager import websocket_loop
from conversion_service.utils import setup_logging, parse_arguments


async def main():
    """
    Main function to start the WebSocket client.
    """
    args = parse_arguments()
    await websocket_loop(CURRENCY_ASSIGNMENT_WS, show_messages=args.show_messages)

if __name__ == "__main__":
    setup_logging()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Service interrupted. Shutting down.")

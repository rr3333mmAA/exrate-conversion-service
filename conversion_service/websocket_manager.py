import asyncio
from json import JSONDecodeError
from typing import Optional

import websockets
import json
import logging
from datetime import datetime, UTC

from conversion_service.config import HEARTBEAT_INTERVAL, HEARTBEAT_TIMEOUT
from conversion_service.message_handler import handle_conversion_request

# Global variable to track the last heartbeat received
last_heartbeat_received: Optional[float] = None


async def send_heartbeat(websocket):
    """
    Send periodic heartbeat messages.
    :param websocket: WebSocket connection.
    """
    while True:
        try:
            await asyncio.sleep(HEARTBEAT_INTERVAL)
            await websocket.send(json.dumps({"type": "heartbeat"}))
        except Exception as e:
            logging.error(f"Error sending heartbeat: {str(e)}.")
            return


async def monitor_heartbeat():
    """
    Monitor if heartbeats are received within the allowed timeframe.
    """
    global last_heartbeat_received
    while True:
        if last_heartbeat_received and (datetime.now(UTC).timestamp() - last_heartbeat_received) > HEARTBEAT_TIMEOUT:
            logging.warning("No heartbeat received within 2 seconds. Reconnecting...")
            raise ConnectionError("Heartbeat timeout")  # Explicitly raise to break out of the loop
        await asyncio.sleep(1)


async def receive_messages(websocket, show_messages=False):
    """
    Receive messages from the WebSocket and handle them accordingly.
    :param websocket: WebSocket connection.
    :param show_messages: Flag to enable logging of request and response messages.
    """
    global last_heartbeat_received
    while True:
        message = await websocket.recv()
        try:
            message = json.loads(message)
        except JSONDecodeError as e:
            logging.error(f"Error decoding message: {str(e)}. Message: '{message}'")

        if message['type'] == 'heartbeat':
            logging.info("Received heartbeat.")
            last_heartbeat_received = datetime.now(UTC).timestamp()
            continue

        if message['type'] == 'message':
            response = await handle_conversion_request(message)
            if show_messages:
                logging.info(f"Request message:\n{json.dumps(message, indent=2)}")
                logging.info(f"Response message:\n{json.dumps(response, indent=2)}")
            await websocket.send(json.dumps(response))


async def websocket_loop(websocket_url, show_messages=False):
    global last_heartbeat_received
    while True:
        try:
            async with websockets.connect(websocket_url) as websocket:
                logging.info("Connected to WebSocket.")

                # Initialize last heartbeat received time
                last_heartbeat_received = datetime.now(UTC).timestamp()

                # Create tasks for heartbeats and receiving messages
                _heartbeat_task = asyncio.create_task(send_heartbeat(websocket))
                _monitor_task = asyncio.create_task(monitor_heartbeat())
                _receive_task = asyncio.create_task(receive_messages(websocket, show_messages))

                # Wait for any task to complete or raise an exception
                done, pending = await asyncio.wait(
                    [_heartbeat_task, _monitor_task, _receive_task],
                    return_when=asyncio.FIRST_COMPLETED
                )

                # Cancel any pending tasks (e.g., in case of a failure or exception)
                for task in pending:
                    task.cancel()

                # Handle any exceptions that occurred
                for task in done:
                    if task.exception():
                        raise task.exception()

        except Exception as e:
            logging.error(f"Connection error: {str(e)}. Reconnecting...")
            await asyncio.sleep(HEARTBEAT_TIMEOUT)  # Wait before reconnecting

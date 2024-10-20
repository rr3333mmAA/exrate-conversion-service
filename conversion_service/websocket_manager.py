import asyncio
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


async def monitor_heartbeat(websocket):
    """
    Monitor if heartbeats are received within the allowed timeframe.
    :param websocket: WebSocket connection.
    """
    global last_heartbeat_received
    while True:
        if last_heartbeat_received and (datetime.now(UTC).timestamp() - last_heartbeat_received) > HEARTBEAT_TIMEOUT:
            logging.warning("No heartbeat received within 2 seconds. Reconnecting...")
            await websocket.close()
            return
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
        message = json.loads(message)

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
    """
    Main loop to connect to the WebSocket and handle incoming messages.
    :param websocket_url: WebSocket URL.
    :param show_messages: Flag to enable logging of request and response messages.
    """
    global last_heartbeat_received
    while True:
        try:
            async with websockets.connect(websocket_url) as websocket:
                logging.info("Connected to WebSocket.")

                # Initialize last heartbeat received time
                last_heartbeat_received = datetime.now(UTC).timestamp()

                # Create tasks for heartbeats and receiving messages
                _heartbeat_task = asyncio.create_task(send_heartbeat(websocket))
                _monitor_task = asyncio.create_task(monitor_heartbeat(websocket))

                await receive_messages(websocket, show_messages)

        except Exception as e:
            logging.error(f"Connection error: {str(e)}. Reconnecting...")
            await asyncio.sleep(HEARTBEAT_TIMEOUT)  # Wait before reconnecting

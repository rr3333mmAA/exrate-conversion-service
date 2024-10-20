# Exchange Rate Conversion Service

This service provides real-time currency conversion from various currencies to EUR over a WebSocket connection. The service connects to `wss://currency-assignment.ematiq.com` and handles conversion requests, sends periodic heartbeat messages, and automatically reconnects if the connection is lost. Additionally, the service caches exchange rates for 2 hours to minimize external API traffic.

## Features

- **Currency Conversion:** Converts a given currency to EUR based on the specified date.
- **Heartbeat Monitoring:** Sends and monitors bi-directional heartbeat messages every second.
- **Automatic Reconnection:** Reconnects to the WebSocket if no heartbeat is received for 2 seconds.
- **Cache:** Caches exchange rates for 2 hours to reduce API load.
- **Optional Argument:** `--show-messages` for logging incoming requests and outgoing responses.

## Requirements
- `Python 3.12`
- `Poetry 1.8.3`

## Installation
This project uses [Poetry](https://python-poetry.org/) for dependency management. To set up the project locally, follow these steps:
1. Clone the repository: 
```bash
git clone https://github.com/rr3333mmAA/exrate-conversion-service.git
cd exrate-conversion-service
```
2. Create `.env` file with the following content:
```bash
# .env
EXCHANGE_ACCESS_KEY=<your_exchange_access_key>
```
3. Install dependencies:
```bash
poetry install
```
4. Activate the virtual environment:
```bash
poetry shell
```

## Running the Service
To start the WebSocket service, run the following command:
```bash
poetry run python app.py
```
To enable request/response message logging, use the `--show-messages` flag:
```bash
poetry run python app.py --show-messages
```

## Running Tests
To run the test suite, use the following command:
```bash
poetry run pytest
```


## Architecture & Technical Decisions
### WebSocket Connection
The service maintains a persistent connection to the `currency-assignment` WebSocket service (`wss://currency-assignment.ematiq.com`).

### Heartbeat Management
The service sends periodic heartbeat messages and monitors incoming heartbeats to detect potential connection issues. If no heartbeat is received for 2 seconds, the connection is closed and re-established.

To track the timestamp of the last received heartbeat, a global variable (`last_heartbeat_received`) is used. This allows the `receive_messages` and `monitor_heartbeat` functions to share and update the timestamp of the last heartbeat across different tasks. The use of a global variable simplifies the coordination between these asynchronous functions, ensuring that the WebSocket connection remains healthy and reconnects if necessary.

### Exchange Rate API
The external exchange rates are fetched from the `https://exchangerate.host` API. To minimize API calls, exchange rates are cached for 2 hours. The cache uses the `TTLCache` from the `cachetools` library to automatically expire entries after 2 hours.

### Logging and Monitoring
With the `--show-messages` flag, the service can log request/response messages, which is useful for debugging and monitoring.
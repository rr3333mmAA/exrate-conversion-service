from os import getenv

from dotenv import load_dotenv

load_dotenv()

# Constants
EXCHANGE_ACCESS_KEY = getenv("EXCHANGE_ACCESS_KEY")
CURRENCY_ASSIGNMENT_WS = "wss://currency-assignment.ematiq.com"
EXCHANGE_RATE_API_URL = "https://api.exchangerate.host/convert"
CACHE_TTL = 7200  # 2 hours in seconds
HEARTBEAT_INTERVAL = 1  # seconds
HEARTBEAT_TIMEOUT = 2  # seconds

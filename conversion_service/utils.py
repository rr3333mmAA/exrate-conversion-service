import argparse
import logging


def setup_logging():
    """
    Setup logging configuration.
    """
    logging.basicConfig(level=logging.INFO)


def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Exchange Rate Conversion Service")
    parser.add_argument("--show-messages", action="store_true", help="show request and response messages")
    return parser.parse_args()

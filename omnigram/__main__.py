import asyncio
import logging
import sys
from .handler import handler

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
asyncio.run(handler())

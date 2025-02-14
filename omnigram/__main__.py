import asyncio
import logging
import sys

from omnigram.server import serve

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
asyncio.run(serve())

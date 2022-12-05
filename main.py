import asyncio
import json
import os

from decouple import config

import bot
from rocket.util import setup_logging

logger = setup_logging()

if __name__ == "__main__":
  if os.name != "nt":
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

  bot.create(
    config("DISCORD_TOKEN", cast=str)
  ).run()

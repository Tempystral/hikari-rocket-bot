import asyncio
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import os

from decouple import config

import bot

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(ch)

fh = TimedRotatingFileHandler(filename="./logs/rocketbot.log", when="midnight")
fh.setFormatter(logging.Formatter("%(levelname)-1.1s %(asctime)23.23s %(name)s: %(message)s"))
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

if __name__ == "__main__":
  if os.name != "nt":
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

  with open(config("SETTINGS_FILE"), "r") as f:
    notif_settings = json.load(f)

  asyncio.run(bot.run(config("DISCORD_TOKEN"), config("CACHE"), notif_settings))

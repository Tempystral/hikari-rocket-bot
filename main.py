import asyncio
import json
import logging
import os

from decouple import config

import bot

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

if __name__ == "__main__":
  if os.name != "nt":
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

  with open(config("SETTINGS_FILE"), "r") as f:
    notif_settings = json.load(f)

  asyncio.run(bot.run(config("DISCORD_TOKEN"), config("CACHE"), notif_settings))

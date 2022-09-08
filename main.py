import asyncio
import json
import os

from decouple import config

import bot
from modules.util import setup_logging

logger = setup_logging()

if __name__ == "__main__":
  if os.name != "nt":
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

  with open(config("SETTINGS_FILE"), "r") as f:
    notif_settings = json.load(f)

  asyncio.run(bot.run(config("DISCORD_TOKEN"), config("CACHE"), notif_settings))

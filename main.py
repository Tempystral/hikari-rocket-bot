import asyncio
import json
import os

import lightbulb
from decouple import config

import bot

if __name__ == "__main__":
  if os.name != "nt":
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

  bot = bot.create(
    config("DISCORD_TOKEN", cast=str)
  )

  bot.run()
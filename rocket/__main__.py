import os
from decouple import config
from rocket import bot

if __name__ == "__main__":
  if os.name != "nt":
    import uvloop
    uvloop.install()

  bot = bot.create(
    config("DISCORD_TOKEN", cast=str)
  )

  bot.run()
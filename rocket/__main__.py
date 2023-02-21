import os
from decouple import config
from rocket import bot
from rocket.util.config import get_settings

if __name__ == "__main__":
  if os.name != "nt":
    import uvloop
    uvloop.install()

  settings = get_settings()

  rocket = bot.create(
    settings.app.discord_token,
    [*settings.guilds],
    settings.app.log_level
  )

  rocket.run()
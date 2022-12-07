import json
import logging

import hikari
from lightbulb import BotApp

from rocket.util import setup_logging
from rocket.util.config import GUILDS, LOG_LEVEL

log = logging.getLogger("RocketBot")


class RocketBot(BotApp):
  def __init__(self, token:str, log_level:str):
    self.token: str = token

    self.guilds: list = GUILDS
    super().__init__(token=self.token,
                     prefix="$",
                     intents=hikari.Intents.ALL_GUILDS | hikari.Intents.ALL_MESSAGES | hikari.Intents.MESSAGE_CONTENT,
                     default_enabled_guilds=self.guilds,
                     #banner="bot",
                     logs=True
                    )

    setup_logging()

  async def on_starting(self, event:hikari.Event) -> None:
    log.info("Starting...")
  
  async def on_started(self, event:hikari.Event) -> None:
    log.info(f"Logged in as: {self.get_me()} with ID: {self.get_me().id}")
    guilds = [ await event.app.rest.fetch_guild(guild) for guild in self.guilds ]
    log.info("Logged into guilds:\n\t{guilds}".format(guilds="\n\t".join((f"{guild.name} : {guild.id}" for guild in guilds))))

  async def on_stopping(self, event:hikari.Event) -> None:
    log.info("Shutting down...")

def create(token:str, log_level:str = LOG_LEVEL) -> RocketBot:
  bot = RocketBot(token, log_level) # init
  # Listen for system events
  bot.subscribe(hikari.StartingEvent, bot.on_starting)
  bot.subscribe(hikari.StoppingEvent, bot.on_stopping)
  bot.subscribe(hikari.StartedEvent, bot.on_started)
  # Load extensions
  bot.load_extensions_from("./rocket/extensions/", must_exist=False)
  return bot

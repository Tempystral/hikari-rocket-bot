import json
import logging

import hikari
from decouple import config
from lightbulb import BotApp

log = logging.getLogger("RocketBot")
log.setLevel("DEBUG")


class RocketBot(BotApp):
  def __init__(self, token:str, log_level:str = "DEBUG"):
    self.token: str = token
    self.settings: dict = self.load_settings()
    self.guilds: list = [ guild["guild_id"] for guild in self.settings.get("servers") ]
    super().__init__(token=self.token,
                     prefix="!",
                     intents=hikari.Intents.ALL_GUILDS,
                     default_enabled_guilds=self.guilds,
                     #banner="bot",
                     logs=log_level
                    )

  async def on_starting(self, event:hikari.Event) -> None:
    log.info("Starting...")
    #self.d.aio_session = ClientSession()
  
  async def on_started(self, event:hikari.Event) -> None:
    log.info(f"Logged in as:\n\t{self.user}\nwith ID:\n\t{self.user.id}")
    log.info("Logged into guilds:\n\t{guilds}".format(guilds="\n\t".join((f"{s.name}:{s.id}" for s in self.guilds))))

  async def on_stopping(self, event:hikari.Event) -> None:
    log.info("Shutting down...")
    #await self.d.aio_session.close()

  def load_settings(self) -> dict:
    settings = None
    with open(config("SETTINGS_FILE"), "r") as f:
      settings = json.load(f)
    return settings

def create(token:str, log_level:str = None) -> RocketBot:
  bot = RocketBot(token, log_level) # init
  # Listen for system events
  bot.subscribe(hikari.StartingEvent, bot.on_starting)
  bot.subscribe(hikari.StoppingEvent, bot.on_stopping)
  # Load extensions
  bot.load_extensions_from("./rocket/extensions/", must_exist=False)
  return bot

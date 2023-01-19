import asyncio
import logging
import queue
from typing import Coroutine

import aiohttp
import hikari
from lightbulb import BotApp
from lightbulb.ext import tasks

from rocket.twitch import TwitchHelper, create_twitch_helper
from rocket.util.logging import setup_logging
from rocket.util.config import get_settings

log = logging.getLogger("rocket.bot")


class RocketBot(BotApp):
  def __init__(self, token:str, guilds:list[int], log_level:str):
    self.token = token
    self.guilds = guilds

    super().__init__(token=self.token,
                     prefix="$",
                     intents=hikari.Intents.GUILDS | hikari.Intents.GUILD_MESSAGES | hikari.Intents.GUILD_EMOJIS | hikari.Intents.GUILD_MESSAGE_REACTIONS | hikari.Intents.MESSAGE_CONTENT | hikari.Intents.GUILD_MEMBERS,
                     default_enabled_guilds=guilds,
                     #banner="bot",
                     logs=True
                    )

    self.d.session = aiohttp.ClientSession()
    self.d.settings = get_settings()
    self.d.helper = create_twitch_helper(self)
    self.d.tasks = set()
    self.d.msgQueue = queue.Queue()
    setup_logging(log_level)

  async def on_starting(self, event:hikari.Event) -> None:
    log.info("Starting...")
  
  async def on_started(self, event:hikari.Event) -> None:
    me = self.get_me()
    assert me is not None
    log.info(f"Logged in as: {me} with ID: {me.id}")
    guilds = [ await event.app.rest.fetch_guild(guild) for guild in self.guilds ]
    log.info("Logged into guilds:\n\t{guilds}".format(guilds="\n\t".join((f"{guild.name} : {guild.id}" for guild in guilds))))

  async def on_shard_ready(self, event:hikari.Event) -> None:
    usernames: list[str] = self.d.settings.get_all_users()
    await self.create_task(self.d.helper.subscribe(usernames))

  async def on_stopping(self, event:hikari.Event) -> None:
    await self.d.session.close()
    helper:TwitchHelper = self.d.helper
    asyncio.create_task(helper.shutdown())
    log.info("Saving data...")
    self.d.settings.save()
    log.info("Shutting down...")
  
  async def create_task(self, coro: Coroutine) -> asyncio.Task:
    task = asyncio.create_task(coro)
    self.d.get_as("tasks", set).add(task)
    task.add_done_callback(self.d.get_as("tasks", set).discard)
    return task

def create(token:str, guilds: list[int], log_level:str = "DEBUG") -> RocketBot:
  bot = RocketBot(token, guilds, log_level) # init
  # Listen for system events
  bot.subscribe(hikari.StartingEvent, bot.on_starting)
  bot.subscribe(hikari.StoppingEvent, bot.on_stopping)
  bot.subscribe(hikari.StartedEvent, bot.on_started)
  bot.subscribe(hikari.ShardReadyEvent, bot.on_shard_ready)
  # Load extensions
  bot.load_extensions_from("./rocket/extensions/", must_exist=False)
  tasks.load(bot)
  return bot

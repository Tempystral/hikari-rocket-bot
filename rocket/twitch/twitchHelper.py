from __future__ import annotations

import subprocess
from logging import getLogger

import aiohttp
from lightbulb import BotApp

from rocket.util.config import EVENTSUB_PORT, TWITCH_ID, TWITCH_SECRET
from twitchAPI.eventsub import EventSub
from twitchAPI.twitch import Twitch
from twitchAPI.helper import first

from . import TwitchResponse, TwitchStream

log = getLogger("twitchHelper")
TARGET_USERNAME = 'protonjon'


async def create_twitch_helper(bot:BotApp) -> TwitchHelper:
  helper = TwitchHelper(bot)
  await helper.setup()
  return helper

class TwitchHelper:
  def __init__(self, bot:BotApp):
    self._bot = bot

  async def setup(self):
    self.twitch = await Twitch(TWITCH_ID, TWITCH_SECRET)
    self.ngrok = await self.start_proxy()
    webhook_url = await self.get_proxy_url(self._bot.d.session)

    # basic setup, will run on port 8888 and a reverse proxy takes care of the https and certificate
    self.event_sub = EventSub(webhook_url, TWITCH_ID, EVENTSUB_PORT, self.twitch)

  async def start_proxy(self) -> subprocess.Popen:
    process = subprocess.Popen(f"ngrok http {EVENTSUB_PORT}".split(" "), shell=False, stdout=subprocess.DEVNULL)
    log.info(f"Started ngrok process {process.pid} on port {EVENTSUB_PORT}")
    return process

  async def get_proxy_url(self, session: aiohttp.ClientSession) -> dict:
    async with aiohttp.ClientSession() as session:
      response = await session.get(url="http://localhost:4040/api/tunnels")
      data = await response.json()
      try:
        url = data["tunnels"][0]["public_url"]
        log.info(f"Reverse proxy url: {url}")
        return url
      except KeyError as e:
        return None

  async def subscribe(self):
    user = await first(self.twitch.get_users(logins="TARGET_USERNAME"))
    # unsubscribe from all old events that might still be there
    await self.event_sub.unsubscribe_all()
    # start the eventsub client
    self.event_sub.start()
    log.info("EventSub client started")
    # subscribing to the desired eventsub hook for our user
    # the given function will be called every time this event is triggered
    await self.event_sub.listen_channel_follow(user.id, self.on_follow)
    log.info(f"Listening for follow events for user {user.display_name}")
    # eventsub will run in its own process

  async def on_follow(self, data: dict):
    log.info(f"New follow {data}")

  def get_live_channels(self, query: str) -> TwitchResponse:
    response = self.twitch.search_channels(query, live_only=True)
    return TwitchResponse(query, response)

  def get_thumbnail(self, channel:str, width:int, height:int) -> str:
    data:dict = self.twitch.get_streams(user_login=channel)
    if not data:
      log.error("Data not initialized!")
      return None
    if not data.get("data"):
      log.error("No streams found!")
      return None
    thumbnail:str = data.get("data")[0].get("thumbnail_url")
    return thumbnail.replace(r'{width}', str(width)).replace(r'{height}', str(height))

  def get_streams(self, twitch_channels:list[str]) -> list[TwitchStream]:
    return [self.get_live_channels(ch).parse_data() for ch in twitch_channels]

  def get_stream(self, channel:str) -> TwitchStream:
    data = self.get_live_channels(channel).parse_data()
    if data:
      log.info(f"Found data for channel: {channel} playing {data.game_name} since {data.started_at}")
    return data
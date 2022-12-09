from __future__ import annotations

from logging import getLogger

from lightbulb import BotApp
from pyngrok import conf, ngrok
from pyngrok.ngrok import NgrokTunnel
from twitchAPI.eventsub import EventSub
from twitchAPI.helper import first
from twitchAPI.twitch import Twitch

from rocket.util.config import (EVENTSUB_PORT, NGROK_CONF, NGROK_PATH,
                                TWITCH_ID, TWITCH_SECRET)

from . import TwitchResponse, TwitchStream

log = getLogger("rocket.twitch.helper")
TARGET_USERNAME = ''


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

    # basic setup, will run on port 8888 and a reverse proxy takes care of the https and certificate
    self.event_sub = EventSub(self.ngrok.public_url, TWITCH_ID, EVENTSUB_PORT, self.twitch)

  async def shutdown(self):
    ngrok.kill()
    await self.twitch.close()

  async def start_proxy(self) -> NgrokTunnel:
    config = conf.PyngrokConfig(ngrok_path=NGROK_PATH, config_path=NGROK_CONF, ngrok_version="v3")
    conf.set_default(config)
    tunnel:NgrokTunnel = ngrok.connect(EVENTSUB_PORT, "http", bind_tls=True)
    log.info(f"Started ngrok tunnel {tunnel.name} on port {EVENTSUB_PORT}")
    return tunnel

  async def subscribe(self):
    user = await first(self.twitch.get_users(logins=TARGET_USERNAME))
    # unsubscribe from all old events that might still be there
    await self.event_sub.unsubscribe_all()
    # start the eventsub client
    self.event_sub.start()
    log.info("EventSub client started")

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
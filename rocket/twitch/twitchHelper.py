from __future__ import annotations
import asyncio

from logging import getLogger
from typing import Coroutine

from lightbulb import BotApp
from pyngrok import conf, ngrok
from pyngrok.ngrok import NgrokTunnel
from twitchAPI.eventsub import EventSub
from twitchAPI.types import TwitchAPIException
from twitchAPI.twitch import Twitch, TwitchUser
from twitchAPI.oauth import UserAuthenticator, get_user_info
from rocket.twitch.auth import AuthServer

from rocket.util.config import ServerConfig

from . import TwitchResponse, TwitchStream

log = getLogger("rocket.twitch.helper")

async def create_twitch_helper(bot:BotApp) -> TwitchHelper:
  helper = TwitchHelper(bot)
  await helper.setup()
  return helper

class TwitchHelper:
  def __init__(self, bot:BotApp):
    self._bot = bot
    self.settings: ServerConfig = bot.d.settings

  @property
  def TWITCH_ID(self):
    return self.settings.app.twitch_id
  
  @property
  def TWITCH_SECRET(self):
    return self.settings.app.twitch_secret

  @property
  def EVENTSUB_PORT(self):
    return self.settings.app.eventsub_port

  @property
  def NGROK_PATH(self):
    return self.settings.app.ngrok_path

  @property
  def NGROK_CONF(self):
    return self.settings.app.ngrok_conf
  
  @property
  def CALLBACK_URL(self):
    return self.settings.app.callback_url

  async def setup(self):
    self.twitch = await Twitch(self.TWITCH_ID, self.TWITCH_SECRET)
    await self.twitch.authenticate_app(scope=[])
    self.ngrok = self.start_proxy()

    # basic setup, will run on port 8888 and a reverse proxy takes care of the https and certificate
    self.event_sub = EventSub(self.ngrok.public_url, self.TWITCH_ID, self.EVENTSUB_PORT, self.twitch)

  async def shutdown(self):
    ngrok.kill()
    await self.twitch.close()

  def start_proxy(self) -> NgrokTunnel:
    config = conf.PyngrokConfig(ngrok_path=self.NGROK_PATH, config_path=self.NGROK_CONF, ngrok_version="v3")
    conf.set_default(config)
    tunnel:NgrokTunnel = ngrok.connect(self.EVENTSUB_PORT, "http", bind_tls=True)
    log.info(f"Started ngrok tunnel {tunnel.name} on port {self.EVENTSUB_PORT}")
    return tunnel

  async def subscribe(self, usernames: list[str]):
    users = self.twitch.get_users(logins=usernames)
    # unsubscribe from all old events that might still be there
    await self.event_sub.unsubscribe_all()
    # start the eventsub client
    self.event_sub.start()
    log.info("EventSub client started")

    async def follow(user: TwitchUser):
      # TODO add error handling
      await self.event_sub.listen_channel_follow(user.id, self.on_follow)
      log.info(f"Listening for follow events for user {user.display_name}")

    coros = [follow(user) async for user in users]
    asyncio.gather(*coros)
      
  
  async def authenticate(self, url: str, callback: Coroutine):

    # Start webserver
    # Listen for responses
    # Validate state
    # retrieve user token from response
    # Use UserAuthenticator to get access token and refresh token with the user token
    userauth = UserAuthenticator(self.twitch, [])
    authserver = AuthServer(self.twitch, [], self.CALLBACK_URL, userauth.state)

    user_token = await authserver.go(callback)
    try:
      assert user_token is not None
      tokens = await userauth.authenticate(user_token=user_token)

      assert tokens is not None
      (auth_token, refresh_token) = tokens
      await self.twitch.set_user_authentication(auth_token, [], refresh_token)

      userinfo:dict[str,str] = await get_user_info(tokens[0])
      if "preferred_username" in userinfo:
        self.settings.set_user_tokens(userinfo["preferred_username"], user_token, auth_token, refresh_token)

    except TwitchAPIException as e:
      log.warning("Failed to authenticate user due to: ", e)
    except AssertionError as ae:
      log.warning("One or more tokens were None! ", ae)
    

  async def on_follow(self, data: dict):
    log.info(f"New follow {data}")
    await self._bot.rest.create_message(content=f"New follow {data}", channel=1)

  # def get_live_channels(self, query: str) -> TwitchResponse:
  #   response = self.twitch.search_channels(query, live_only=True)
  #   return TwitchResponse(query, response)

  # def get_thumbnail(self, channel:str, width:int, height:int) -> str:
  #   data:dict = self.twitch.get_streams(user_login=channel)
  #   if not data:
  #     log.error("Data not initialized!")
  #     return None
  #   if not data.get("data"):
  #     log.error("No streams found!")
  #     return None
  #   thumbnail:str = data.get("data")[0].get("thumbnail_url")
  #   return thumbnail.replace(r'{width}', str(width)).replace(r'{height}', str(height))

  # def get_streams(self, twitch_channels:list[str]) -> list[TwitchStream]:
  #   return [self.get_live_channels(ch).parse_data() for ch in twitch_channels]

  # def get_stream(self, channel:str) -> TwitchStream:
  #   data = self.get_live_channels(channel).parse_data()
  #   if data:
  #     log.info(f"Found data for channel: {channel} playing {data.game_name} since {data.started_at}")
  #   return data
from __future__ import annotations

import asyncio
import uuid
from logging import getLogger

from hikari.embeds import Embed
from hikari.errors import NotFoundError
from lightbulb import BotApp
from pyngrok import conf, ngrok
from pyngrok.ngrok import NgrokTunnel
from twitchAPI.eventsub import EventSub
from twitchAPI.helper import first
from twitchAPI.oauth import (InvalidRefreshTokenException,
                             UnauthorizedException, UserAuthenticator,
                             refresh_access_token, validate_token)
from twitchAPI.twitch import Stream, Twitch, TwitchUser
from twitchAPI.types import EventSubSubscriptionConflict, TwitchAPIException

from rocket.twitch.auth import AuthServer
from rocket.util.config import ServerConfig
from rocket.util.config.serverConfig import UserConfig

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
    self.userauth = UserAuthenticator(self.twitch, [])
    self.authserver = AuthServer(self.twitch, [], self.CALLBACK_URL, self.userauth.state)

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

  async def __listen_online(self, user: TwitchUser):
    try:  
      await self.event_sub.listen_stream_online(user.id, self.on_start_streaming)
      log.info(f"Listening for online events for user {user.display_name}")
    except EventSubSubscriptionConflict as e:
      log.warning(f"Already listening for online events from user {user.display_name}")

  async def subscribe(self, usernames: list[str]):
    users = self.twitch.get_users(logins=usernames)
    # unsubscribe from all old events that might still be there
    await self.event_sub.unsubscribe_all()
    # start the eventsub client
    self.event_sub.start()
    log.info("EventSub client started")

    coros = [self.__listen_online(user) async for user in users]
    asyncio.gather(*coros)
  
  async def add_subscription(self, username: str):
    user = await first(self.twitch.get_users(logins=[username]))
    if user:
      await self.__listen_online(user)

  
  async def authenticate(self) -> tuple[str, str] | None:
    self.authserver = AuthServer(self.twitch, [], self.CALLBACK_URL, self.userauth.state)

    user_token = await self.authserver.go()
    try:
      assert user_token is not None
      tokens = await self.userauth.authenticate(user_token=user_token)

      assert tokens is not None
      (auth_token, refresh_token) = tokens
      await self.twitch.set_user_authentication(auth_token, [], refresh_token)
      return tokens
    except TwitchAPIException as e:
      log.warning("Failed to authenticate user due to: ", e)
    except AssertionError as ae:
      log.warning("One or more tokens were None! ", ae)
    
  async def validate(self, user: UserConfig) -> tuple[str, str] | None:
    response = await validate_token(user.auth_token)
    if "status" in response: # Invalid auth token
      try:
        auth_token, refresh_token = await refresh_access_token(user.refresh_token, self.TWITCH_ID, self.TWITCH_SECRET)
        return auth_token, refresh_token
        # self._bot.d.settings.set_user_tokens(user.username, user.user_token, auth_token, refresh_token)
      except InvalidRefreshTokenException:
        log.warning(f"Refresh token for {user.username} is invalid, must re-authenticate!")
      except UnauthorizedException:
        log.warning(f"Refresh and Auth tokens for {user.username} are invalid, must re-authenticate!")
    else: # Valid tokens
      return user.auth_token, user.refresh_token
  
  def create_thumbnail(self, stream: Stream, width:int, height:int) -> str:
    return stream.thumbnail_url.replace(r'{width}', str(width)).replace(r'{height}', str(height))

  async def on_start_streaming(self, data: dict):
    username = data['event']['broadcaster_user_login']
    display_name = data['event']['broadcaster_user_name']
    user_id = data['event']['broadcaster_user_id']
    log.info(f"User has started streaming: {username}")

    stream = await first(self.twitch.get_streams(user_id=[user_id]))
    if stream:
      notif = (
        Embed(title=f"{stream.title}", url=f"https://www.twitch.tv/{stream.user_login}", colour="#9146FF")
        .set_image(self.create_thumbnail(stream, 1280, 720))
        .set_author(name=display_name, icon=f"{stream.thumbnail_url}#{str(uuid.uuid4())}")
        .add_field(name="Game", value=stream.game_name, inline=True)
        .add_field(name="Started at", value=f"<t:{int(stream.started_at.timestamp())}>", inline=True)
      )

    for guild in self.settings.guilds.values():
      if guild.notification_channel and username in guild.watching:
        try:
          await self._bot.rest.create_message(
            channel=guild.notification_channel,
            content=f"{'@everyone, ' if guild.everyone else ''}{username} is live!")
          return
        except NotFoundError:
          pass
      log.warning(f"Guild {guild.name} had an improperly-configured channel!")

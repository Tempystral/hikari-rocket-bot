from __future__ import annotations

import json
from logging import getLogger
import os
from dataclasses import dataclass, field

from hikari import Role, Snowflakeish
from hikari.channels import GuildChannel

from dataclass_wizard import JSONWizard
from rocket.util.errors import (GuildExistsError, GuildNotFoundError,
                                UserNotFoundError)

log = getLogger("rocket.util.config")

settings: ServerConfig | None = None

def _load_settings(file:str) -> ServerConfig:
  settings:ServerConfig

  if not os.path.exists(file):
    settings = ServerConfig(AppConfig(), guilds={}, users=set())
    with open(file, "w") as f:
      f.write(settings.to_json())
  else:
    with open(file, "r") as f:
      data = json.load(f)
      settings = ServerConfig.from_dict(data)
  return settings

def get_settings(filename:str = "./settings.json") -> ServerConfig:
  return settings if settings else _load_settings(filename)

@dataclass(frozen=True)
class UserConfig:
  username: str
  id:int
  display_name:str
  #user_token:str
  auth_token:str
  refresh_token:str

@dataclass
class GuildConfig:
  guild_id:int
  streamer_role:int | None = None
  name:str | None = None
  notification_channel:int | None = None
  everyone:bool = False
  watching:set[str] = field(default_factory=set)

@dataclass
class AppConfig:
  twitch_id:str = ""
  twitch_secret:str = ""
  eventsub_port:int = 1234
  callback_url:str = "localhost"
  discord_token:str = ""
  
  ngrok_path:str = ""
  ngrok_conf:str = ""

  log_level:str = field(default="INFO")
  cache_file:str = field(default="./cache")

@dataclass
class ServerConfig(JSONWizard):
  class _(JSONWizard.Meta):
    key_transform_with_load = "SNAKE"

  app: AppConfig
  guilds: dict[int, GuildConfig] = field(default_factory=dict)
  users: set[UserConfig] = field(default_factory=set)

  def add_guild(self, guild_id: int, guild_name: str):
    if guild_id in self.guilds:
      raise GuildExistsError("Guild already exists!")
    self.guilds.setdefault(guild_id, GuildConfig(guild_id=guild_id, name=guild_name))
  
  def add_user(self, guild_id: int, username: str):
    self.__guild_exists(guild_id)
    self.guilds[guild_id].watching.add(username)
    
  def set_name(self, guild_id: int, name:str):
    self.__guild_exists(guild_id)
    self.guilds[guild_id].name = name

  def set_notification_channel(self, guild_id: int, channel: GuildChannel):
    self.__guild_exists(guild_id)
    self.guilds[guild_id].notification_channel = channel.id
    return channel.id

  def set_streamer_role(self, guild_id: int, role: Role):
    self.__guild_exists(guild_id)
    self.guilds[guild_id].streamer_role = role.id
    return role.id
  
  def set_notify(self, guild_id: int, notify:bool):
    self.__guild_exists(guild_id)
    self.guilds[guild_id].everyone = notify
    return notify
  
  def get_users(self, guild_id: int) -> list[UserConfig]:
    if guild_id in self.guilds:
      return [userconfig for user in self.get_guild(guild_id).watching if (userconfig := self.get_user(user)) is not None]
    return []
  
  def get_all_users(self) -> list[str]:
    return [user.username for user in self.users]
    
  def get_user(self, user: str) -> UserConfig | None:
    return next(filter(lambda u: u.username == user, self.users), None)

  def get_guild(self, guild_id: int) -> GuildConfig:
    self.__guild_exists(guild_id)
    return self.guilds[guild_id]

  def set_user_tokens(self, username: str, user_id: int, display_name: str, auth_token: str, refresh_token: str):
    if (user := self.get_user(username)):
      log.debug(f"Removing user {user.username}")
      self.users.remove(user) # Remove the existing user object first

    self.users.add(
      UserConfig(
      username=username,
      id=user_id,
      display_name=display_name,
      #user_token=user_token,
      auth_token=auth_token,
      refresh_token=refresh_token)
    )
    
  def __guild_exists(self, guild_id):
    if guild_id not in self.guilds:
      raise GuildNotFoundError("Guild is not configured! Please run `/admin setup`")
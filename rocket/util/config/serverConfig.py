from __future__ import annotations
import json
import os
from dataclasses import dataclass, field
from dataclass_wizard import JSONWizard
from hikari import Role, Snowflakeish
from rocket.util.errors import (GuildExistsError, GuildNotFoundError,
                                UserNotFoundError)

settings: ServerConfig = None

def _load_settings(file:str) -> ServerConfig:
  settings:ServerConfig

  if not os.path.exists(file):
    settings = ServerConfig(guilds={}, users=[])
    with open(file, "w") as f:
      f.write(settings.to_json())
  else:
    with open(file, "r") as f:
      data = json.load(f)
      settings = ServerConfig.from_dict(data)
  return settings

def get_settings(filename:str = "./settings.json") -> ServerConfig:
  return settings if settings else _load_settings(filename)

@dataclass
class UserConfig:
  id:int
  username:str
  display_name:str
  user_token:str = ""
  refresh_token:str = ""

@dataclass
class GuildConfig:
  name:str | None = None
  guild_id:int | None = None
  notification_channel:int | None = None
  everyone:bool = False
  elevated_roles:list[int] = field(default_factory=list)
  watching:list[str] = field(default_factory=list)

@dataclass
class AppConfig:
  twitch_id:str
  twitch_secret:str
  eventsub_port:int
  discord_token:str
  
  ngrok_path:str
  ngrok_conf:str

  log_level:str = field(default="INFO")
  cache_file:str = field(default="./cache")

@dataclass
class ServerConfig(JSONWizard):
  class _(JSONWizard.Meta):
    key_transform_with_load = "SNAKE"

  app: AppConfig
  guilds: dict[int, GuildConfig] = field(default_factory=dict)
  users: list[UserConfig] = field(default_factory=list)

  def add_guild(self, guild_id: int):
    guild = self.guilds.setdefault(guild_id, GuildConfig())
    if guild:
      raise GuildExistsError("Guild already exists!")

  def set_name(self, guild_id: int, name:str):
    if guild_id not in self.guilds:
      raise GuildNotFoundError("Guild is not configured! Please run `!add_guild`")
    self.guilds[guild_id].name = name

  def set_notification_channel(self, guild_id: int, channel: Snowflakeish):
    if guild_id not in self.guilds:
      raise GuildNotFoundError("Guild is not configured! Please run `!add_guild`")
    self.guilds[guild_id].notification_channel = channel


  def add_elevated_role(self, guild_id: int, role: Role):
    if guild_id not in self.guilds:
      raise GuildNotFoundError("Guild is not configured! Please run `!add_guild`")
    self.guilds[guild_id].elevated_roles.add(role.id)
  
  def remove_elevated_role(self, guild_id: int, role: Role):
    if guild_id not in self.guilds:
      raise GuildNotFoundError("Guild is not configured! Please run `!add_guild`")
    try:
      self.guilds[guild_id].elevated_roles.remove(role.id)
    except ValueError as e:
      raise UserNotFoundError("User not found.")
  
  def set_notify(self, guild_id: int, notify:bool):
    if guild_id not in self.guilds:
      raise GuildNotFoundError("Guild is not configured! Please run `!add_guild`")
    self.guilds[guild_id].everyone = notify
  
  def get_users(self, guild_id: int) -> list[UserConfig]:
    if guild_id in self.guilds:
      return [userconfig for user in self.get_guild(guild_id).watching if (userconfig := self.get_user(user)) is not None]
    return []
    
  def get_user(self, user: str) -> UserConfig | None:
    return next(filter(lambda u: u.username == user, self.users), None)

  def get_guild(self, guild_id: int) -> GuildConfig:
    return self.guilds[guild_id]

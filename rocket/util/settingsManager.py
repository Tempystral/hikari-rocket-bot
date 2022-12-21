import json
import os
from typing import Protocol

import aiofiles
from hikari import Role, Snowflakeish

from rocket.util.serverConfig import GuildConfig, ServerConfig, UserConfig
from rocket.util.helper import find


class SettingsHelper:
  def __init__(self, settings_file:str):
    self.settings = self._load_settings(settings_file)
    
  def _load_settings(self, file:str) -> ServerConfig:
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
    
  def add_guild(self, guild_id: int):
    guild = self.settings.guilds.setdefault(guild_id, GuildConfig())
    if guild:
      pass # raise Error # An error to indicate that the guild was already in the database

  def set_name(self, guild_id: int, name:str):
    try:
      self.settings.guilds[guild_id].name = name
    except KeyError as e:
      pass # raise Error # An error to indicate no guild is present

  def set_notification_channel(self, guild_id: int, channel: Snowflakeish):
    try:
      self.settings.guilds[guild_id].notification_channel = channel
    except KeyError as e:
      pass

  def add_elevated_role(self, guild_id: int, role: Role):
    try:
      self.settings.guilds[guild_id].elevated_roles.add(role.id)
    except KeyError as e:
      pass
  
  def remove_elevated_role(self, guild_id: int, role: Role):
    try:
      if guild_id in self.settings.guilds:
        self.settings.guilds[guild_id].elevated_roles.remove(role.id)
    except KeyError as e:
      pass
  
  def set_notify(self, guild_id: int, notify:bool):
    try:
      self.settings.guilds[guild_id].everyone = notify
    except KeyError as e:
      pass
  
  def get_users(self, guild_id: int) -> list[UserConfig]:
    if guild_id in self.settings.guilds:
      return [userconfig for user in self.get_guild(guild_id).watching if (userconfig := self.get_user(user)) is not None]
    return []
    
  def get_user(self, user: str) -> UserConfig | None:
    return next(filter(lambda u: u.username == user, self.settings.users), None)

  def get_guild(self, guild_id: int) -> GuildConfig:
    return self.settings.guilds[guild_id]
import lightbulb as lb
from hikari import MessageFlag
from lightbulb.converters import GuildChannelConverter
from lightbulb.converters.special import BooleanConverter, RoleConverter
from rocket.extensions.checks import has_elevated_role_in_guild

from rocket.util.config import ServerConfig

admin_plugin = lb.Plugin("Admin")

@admin_plugin.command
@lb.add_checks(has_elevated_role_in_guild())
@lb.command("admin", "Manage server-specific settings for the bot", hidden=True)
@lb.implements(lb.SlashCommandGroup, lb.PrefixCommandGroup)
async def admin_group(ctx: lb.Context) -> None:
  pass

@admin_group.child
@lb.option("role", "The role to add", type=RoleConverter)
@lb.command("addmodrole", "Adds a moderator role for this server.", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def add_mod_role(ctx: lb.Context):
  pass

@admin_group.child
@lb.option("role", "The role to remove", type=RoleConverter)
@lb.command("removemodrole", "Adds a moderator role for this server.", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def remove_mod_role(ctx: lb.Context):
  pass

@admin_group.child
@lb.option("channel", "The channel to post in", type=GuildChannelConverter)
@lb.command("setnotifchannel", "Sets the channel Rocket will post notifications in.", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def set_notification_channel(ctx: lb.Context):
  pass

@admin_group.child
@lb.option("option", "true or false", type=BooleanConverter)
@lb.command("notify", "Set whether Rocket will ping @everyone for new announcements.", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def set_everyone(ctx: lb.Context):
  pass

@admin_group.child
@lb.command("start", "Start listening for livestreams", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def start(ctx: lb.Context):
  pass

@admin_group.child
@lb.command("stop", "Stop listening for livestreams", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def stop(ctx: lb.Context):
  pass

def load(bot: lb.BotApp) -> None:
  bot.add_plugin(admin_plugin)

def unload(bot: lb.BotApp) -> None:
  bot.remove_plugin(admin_plugin)
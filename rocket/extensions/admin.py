import lightbulb as lb
from hikari import MessageFlag
from lightbulb.converters import GuildChannelConverter
from lightbulb.converters.special import BooleanConverter, RoleConverter

from rocket.util.config import ELEVATED_ROLES

admin_plugin = lb.Plugin("Admin")

@admin_plugin.command
@lb.add_checks('''elevated role(s) for calling server specifically''')
@lb.command("admin", "Manage server-specific settings for the bot", hidden=True)
@lb.implements(lb.SlashCommandGroup, lb.PrefixCommandGroup)
async def admin_group(ctx: lb.Context) -> None:
  pass

@admin_group.child
@lb.option("Role", "The role to add", type=RoleConverter)
@lb.command("addmodrole", "Adds a moderator role for this server.", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def add_mod_role(ctx: lb.Context):
  pass

@admin_group.child
@lb.option("Role", "The role to remove", type=RoleConverter)
@lb.command("removemodrole", "Adds a moderator role for this server.", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def remove_mod_role(ctx: lb.Context):
  pass

@admin_group.child
@lb.option("Channel", "The channel to post in", type=GuildChannelConverter)
@lb.command("setNotifChannel", "Sets the channel Rocket will post notifications in.", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def set_notification_channel(ctx: lb.Context):
  pass

@admin_group.child
@lb.command("everyone", "Set whether Rocket will ping @everyone for new announcements.", inherit_checks=True)
@lb.option("option", "true or false", type=BooleanConverter)
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
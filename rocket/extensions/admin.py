from logging import getLogger

import hikari
import lightbulb as lb
from hikari.permissions import Permissions

from rocket.twitch import TwitchHelper
from rocket.util.config import ServerConfig
from rocket.util.errors import GuildNotFoundError, RocketBotException

log = getLogger("rocket.extensions.admin")

admin_plugin = lb.Plugin("Admin")

@admin_plugin.command
@lb.add_checks(lb.has_guild_permissions(Permissions.MANAGE_ROLES))
@lb.command("admin", "Manage server-specific settings for the bot")
@lb.implements(lb.SlashCommandGroup, lb.PrefixCommandGroup)
async def admin_group(ctx: lb.Context) -> None:
  pass

@admin_group.child
@lb.command("set", "Set variables", inherit_checks=True)
@lb.implements(lb.SlashSubGroup, lb.PrefixSubGroup)
async def set_command(ctx: lb.Context):
  pass

@set_command.child
@lb.option("role", "The role to add", type=hikari.OptionType.ROLE)
@lb.command("streamer", "Sets the streamer role on this server.", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def set_streamer_role(ctx: lb.Context):
  settings: ServerConfig = ctx.bot.d.settings
  assert ctx.guild_id
  role = settings.set_streamer_role(ctx.guild_id, ctx.options.role)
  await ctx.respond(f"Set streamer role: <@&{role}>")

@set_command.child
@lb.option("channel", "The channel to post in", type=hikari.OptionType.CHANNEL)
@lb.command("channel", "Sets the channel Rocket will post notifications in.", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def set_notification_channel(ctx: lb.Context):
  settings: ServerConfig = ctx.bot.d.settings
  assert ctx.guild_id
  channel = settings.set_notification_channel(ctx.guild_id, ctx.options.channel)
  await ctx.respond(f"Set notification channel: <#{channel}>")

@set_command.child
@lb.option("option", "true or false", type=bool)
@lb.command("everyone", "Set whether Rocket will ping @everyone for new announcements.", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def set_everyone(ctx: lb.Context):
  settings: ServerConfig = ctx.bot.d.settings
  assert ctx.guild_id
  notify = settings.set_notify(ctx.guild_id, ctx.options.option)
  await ctx.respond(f"Bot will ping server: **{str(notify)}**")

@admin_group.child
@lb.option("everyone", "Whether or not to notify @everyone", type=bool)
@lb.option("channel", "The channel Rocket will post in", type=hikari.OptionType.CHANNEL)
@lb.option("role", "Which role will be used by streamers?", type=hikari.OptionType.ROLE)
@lb.command("setup", "Set up the guild to use Rocket", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def setup(ctx: lb.Context):
  settings: ServerConfig = ctx.bot.d.settings
  assert ctx.guild_id

  settings.add_guild(ctx.guild_id, ctx.get_guild().name)

  role = settings.set_streamer_role(ctx.guild_id, ctx.options.role)
  channel = settings.set_notification_channel(ctx.guild_id, ctx.options.channel)
  notify = settings.set_notify(ctx.guild_id, ctx.options.everyone)

  response = ( hikari.Embed(description=f"Registered **{ctx.get_guild().name}**")
    .add_field("Notification channel", f"<@&{role}>")
    .add_field("Streamer role", f"<#{channel}>")
    .add_field("Notify everyone", str(notify))
  )
  await ctx.respond(embed=response)

@admin_group.child
@lb.command("start", "Start listening for livestreams", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def start(ctx: lb.Context):
  helper: TwitchHelper = ctx.bot.d.helper
  settings: ServerConfig = ctx.bot.d.settings

  await helper.setup()
  await helper.subscribe(settings.get_all_users())

@admin_group.child
@lb.command("stop", "Stop listening for livestreams", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def stop(ctx: lb.Context):
  helper: TwitchHelper = ctx.bot.d.helper
  await helper.event_sub.stop()
  await helper.shutdown()

@admin_plugin.set_error_handler
async def on_error(event: lb.events.CommandErrorEvent) -> bool | None:
  log.warning(f"Caught exception: {type(event.exception)}")

  # if isinstance(event.exception, lb.errors.CommandInvocationError):
  if isinstance(event.exception, RocketBotException):
    await event.context.respond(event.exception.message, flags=hikari.MessageFlag.EPHEMERAL)
    return True # To tell the bot not to propogate this error event up the chain


def load(bot: lb.BotApp) -> None:
  bot.add_plugin(admin_plugin)

def unload(bot: lb.BotApp) -> None:
  bot.remove_plugin(admin_plugin)
from logging import getLogger
from queue import Queue

import hikari
import lightbulb as lb
from hikari.embeds import Embed
from hikari.errors import NotFoundError
from lightbulb.ext import tasks

from rocket.extensions.checks import has_streamer_role_in_guild
from rocket.twitch import TwitchHelper
from rocket.util.config import ServerConfig
from rocket.util.errors import RocketBotException
from twitchAPI.helper import first
from twitchAPI.oauth import get_user_info

log = getLogger("rocket.extensions.notifier")

twitch_plugin = lb.Plugin("notifier")

@twitch_plugin.command
@lb.add_checks(has_streamer_role_in_guild())
@lb.command("twitch", "Perform Twitch-related actions", hidden=False)
@lb.implements(lb.SlashCommandGroup, lb.PrefixCommandGroup)
async def twitch_group(ctx: lb.Context) -> None:
  pass

@twitch_group.child
@lb.option("username", "Your Twitch username", type=str)
@lb.command("authenticate", "Perform Twitch-related actions", aliases=["auth"], hidden=False)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def authorize_user(ctx: lb.Context):
  helper: TwitchHelper = ctx.bot.d.helper
  settings: ServerConfig = ctx.bot.d.settings

  log.info(f"{ (settings is ctx.bot.d.settings) = }")

  tokens = None

  assert ctx.options.username
  assert ctx.guild_id

  if ctx.options.username in settings.get_all_users():
    if ctx.options.username not in settings.get_guild(ctx.guild_id).watching:
      settings.add_user(ctx.guild_id, ctx.options.username)
    # Attempt to re-validate
    if (user := settings.get_user(ctx.options.username)):
      tokens = await helper.validate(user)
  
  if not tokens: # User is not in the list or has invalid tokens
    await ctx.respond(f"You need to authorize Rocketbot with Twitch. Please sign in at <{helper.userauth.return_auth_url()}>", flags=hikari.MessageFlag.EPHEMERAL)
    tokens = await helper.authenticate()
  
  user = await first(helper.twitch.get_users(logins=[ctx.options.username]))
  
  if tokens and user:
    userinfo:dict[str,str] = await get_user_info(tokens[0])
    log.debug(f"User retrieved: {userinfo.get('preferred_username')} | id: {userinfo.get('sub')}")
    if userinfo.get("sub") == user.id:
      log.debug(f"Verified: {user.display_name} is correct user, adding to list of users")
      settings.update_user(ctx.options.username, int(user.id), user.display_name, tokens[0], tokens[1])
      await helper.add_subscription(ctx.options.username)

      await ctx.respond(
        hikari.Embed(description=f"User successfully authenticated!", colour="#6441a5")
        .set_author(name=user.display_name, icon=user.profile_image_url))
      return

@twitch_plugin.set_error_handler
async def on_error(event: lb.events.CommandErrorEvent) -> bool | None:
  log.warning(f"Caught exception: {type(event.exception)}")

  # if isinstance(event.exception, lb.errors.CommandInvocationError):
  if isinstance(event.exception, RocketBotException):
    await event.context.respond(event.exception.message, flags=hikari.MessageFlag.EPHEMERAL)
    return True # To tell the bot not to propogate this error event up the chain

@tasks.task(s=10, auto_start=True, pass_app=True)
async def twitch_event(bot: lb.BotApp):
  queue = bot.d.get_as("msgQueue", Queue)
  helper = bot.d.get_as("helper", TwitchHelper)
  settings = bot.d.get_as("settings", ServerConfig)

  if not queue.empty():
    user_id = queue.get()
    channels = await helper.twitch.get_channel_information(broadcaster_id=user_id)
    user = await first(helper.twitch.get_users(user_ids=[user_id]))
    if user and channels and (channel := channels[0]):
      notif = (
        Embed(title=f"{channel.title}", url=f"https://www.twitch.tv/{channel.broadcaster_login}", colour="#9146FF")
        .set_image(helper.create_thumbnail(channel.broadcaster_login, 1280, 720))
        .set_author(name=channel.broadcaster_name, icon=user.profile_image_url, url=f"https://www.twitch.tv/{channel.broadcaster_login}")
        .add_field(name="Game", value=channel.game_name, inline=True)
        .add_field(name="Tags", value=" ".join((f"`{tag}`" for tag in channel.tags)), inline=True)
        # .add_field(name="Started at", value=f"<t:{int(stream.started_at.timestamp())}>", inline=True)
      )
      
      for guild in (g for g in settings.guilds.values() if user.login in g.watching):
        if guild.notification_channel is None:
          log.warning(f"Guild {guild.name} had an improperly-configured channel!")
        else:
          try:
            await bot.rest.create_message(
              channel=guild.notification_channel,
              content=f"{'@everyone, ' if guild.everyone else ''}{user.display_name} is live!",
              embed=notif
              )
            log.info(f"Created message in {guild.name} for streamer {user.login}")
          except NotFoundError:
            pass
        

def load(bot: lb.BotApp) -> None:
  bot.add_plugin(twitch_plugin)

def unload(bot: lb.BotApp) -> None:
  bot.remove_plugin(twitch_plugin)
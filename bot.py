from logging import getLogger

from hikari import Embed, RESTApp, TokenType
from hikari.errors import ForbiddenError

from decouple import config
from modules import TwitchHelper, cacheManager, get_stream, parseTimestamp
from modules.util import find

log = getLogger("bot")
log.setLevel("DEBUG")

async def run(token:str, cache:str, settings: dict):
  # We acquire a client with a given token. This allows one REST app instance
  # with one internal connection pool to be reused.
  async with RESTApp().acquire(token, TokenType.BOT) as client:
    twitch = TwitchHelper()
    cm = cacheManager(cache)

    channels = {ch for server in settings["servers"] for ch in server["watching"]}
    for channel in channels:
      stream = get_stream(channel)
      if stream and not cm.contains(channel):
        # If the stream is live and has NOT been announced
        for server in find(lambda x: channel in x["watching"], settings["servers"]):
          # If the selected channel is not in the cache, an embed can be posted
          notif = Embed(title=f"{stream.title}",
                        url=f"https://www.twitch.tv/{stream.broadcaster_login}",
                        colour="#9146FF")\
                  .set_image(twitch.get_thumbnail(channel, 1280, 720))\
                  .set_author(name=stream.display_name, icon=stream.thumbnail_url)\
                  .add_field(name="Game", value=stream.game_name, inline=True)\
                  .add_field(name="Started at", value=parseTimestamp(stream.started_at), inline=True)
          
          message_text = f"{'@everyone, ' if server['everyone'] else ''}{stream.display_name} is live!"
          try:
            await client.create_message(channel=server["notification_channel"], content=message_text, embed=notif)
          except ForbiddenError as e:
            log.error(f"Not authorized to post in server: {server['name']}!")
        
        cm.put(channel) # Add the channel to the cache so it isn't announced again

      elif not stream and cm.contains(channel):
        #If the stream is not live but is still in the cache
        cm.remove(channel)
      else:
        if cm.contains(channel):
          log.debug(f"{channel} already announced, skipping...")
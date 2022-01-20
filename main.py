import asyncio
import hikari
from decouple import config

from modules import TwitchHelper, cacheManager, parseTimestamp

discord_token = config("DISCORD_TOKEN")
notif_channel = config("NOTIFICATION_CHANNEL")
twitch_channels:list = config("TWITCH_CHANNELS").split(",")

bot = hikari.RESTApp()
cm = cacheManager(config("CACHE"))

async def run(token:str, notif_channel:str, twitch_channels:list):
    # We acquire a client with a given token. This allows one REST app instance
    # with one internal connection pool to be reused.
    async with bot.acquire(token, hikari.TokenType.BOT) as client:
        for twitch_channel in twitch_channels:
            # Init twitch helper for each channel, then search for live stream
            twitchHelper = TwitchHelper(twitch_channel)
            data = twitchHelper.poll_stream().read_user_data()

            if data: # If a live stream was found:
                if not cm.checkCache(twitch_channel): # If the selected channel is not in the cache, an embed can be posted
                    notif = hikari.Embed(title=f"{data['title']}",
                                        url=f"https://www.twitch.tv/{data['broadcaster_login']}",
                                        colour="#9146FF")\
                        .set_image(twitchHelper.get_stream_thumbnail(1280, 720))\
                        .set_author(name=data["display_name"], icon=data["thumbnail_url"])\
                        .add_field(name="Game", value=data["game_name"], inline=True)\
                        .add_field(name="Started at", value=parseTimestamp(data["started_at"]), inline=True)

                    await client.create_message(channel=notif_channel, content="@everyone", embed=notif)
                    cm.writeCache(twitch_channel) # Add the channel to the cache so it isn't announced again
            else:
                # If no data was found, the stream is not live. Remove the channel from the cache so it can be reannounced in the future.
                cm.removeEntry(twitch_channel)

asyncio.run(run(discord_token, notif_channel, twitch_channels))

#pprint(twitchHelper.poll_stream("macaw45").read_user_data())

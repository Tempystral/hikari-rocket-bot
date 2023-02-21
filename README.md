# Rocket: A simple twitch stream notifier
 
## Setup
Create a settings.json file in the root directory of the app. You can also generate this file by running and exiting the app. The format is as follows:
```json
{
  "app": {
    "twitch_id": "",
    "twitch_secret": "",
    "eventsub_host": null,
    "eventsub_port": 8888,
    "oauth_callback_url": "localhost",
    "oauth_callback_port": 17563,
    "discord_token": "",
    "ngrok_path": "",
    "ngrok_conf": "",
    "log_level": "INFO"
  },
  "guilds": {},
  "users": []
}
```

Fill out the information in the app section to get the bot connected to Discord and Twitch. The ngrok fields are optional, as ngrok should only be used in a dev environment. You should instead host a reverse proxy which directs traffic to the eventsub and oauth callback services.

## Run the bot
You can start the bot with `python -m rocket`. A virtual environment and terminal such as tmux or screen are recommended.
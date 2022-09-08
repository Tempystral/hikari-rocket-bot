# hikari-bot
 
Create a settings.json file in the root directory of the bot. The format is as follows:
```json
{
  "servers": [
    {
      "name": string, // Descriptive name, for logging only
      "server_id": number, // Server ID
      "notification_channel": number, // Channel ID
      "watching": [ // Twitch usernames for this server to watch
        string,
        ...
      ],
      "everyone": boolean // Whether the bot should tag @everyone in this server
    },
    ...
  ]
}
```
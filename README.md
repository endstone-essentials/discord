# Discord for Endstone

A Discord integration plugin for Endstone servers.

## Features
- [x] In-game chat and Discord chat integration.
- [x] Notifications for player join and leave events.
- [x] Player death messages synced to Discord.
- [x] Execute in-game server commands directly from Discord.
- [ ] Future support for console logs in Discord.

---

## Requirements
To use this plugin, ensure you have:
- [Endstone 0.5 or higher](https://github.com/EndstoneMC/endstone).
- A valid Discord bot token.
- The relevant permissions in your Discord server to send messages.

---

## Installation

1. **Download the plugin** from the release page and place it into the Endstone server's plugins folder.
2. Restart or reload your Endstone server to generate the configuration file.

---

## Configuration

1. Navigate to the generated configuration file:
   ```toml
   token = "ENTER_YOUR_TOKEN_HERE"

   [channels]
   chat = "CHANNEL_ID"    # for chat, player, and status messages
   console = "CHANNEL_ID" # for command execution outputs
   ```

2. **Update the configuration:**
   - `token`: Replace `"ENTER_YOUR_TOKEN_HERE"` with your Discord bot token. You can create a bot and obtain its token from the [Discord Developer Portal](https://discord.com/developers/applications).
   - `chat`: Enter the channel ID where in-game chat and player events (e.g., join, leave messages) should appear.
   - `console`: Enter the channel ID for executing server commands.

3. Save the configuration file and restart/reload the server for the changes to take effect.

---

## Usage

Once the plugin is installed and configured:
1. Messages sent in your in-game chat will appear in the configured Discord `chat` channel, and vice versa.
2. Player events, such as joins, leaves, and deaths, will automatically appear in the `chat` channel.
3. Server administrators can execute commands in the Discord `console` channel.

---

## Troubleshooting

- **Bot not sending messages?**
  - Verify the `token` is set correctly and the bot is online.
  - Ensure the bot has permission to send messages in the specified channels.
  - Verify the channel IDs are correct.

- **Configuration changes not taking effect?**
  - Check the server logs for errors and restart your server after modifying the configuration file.

---

## License
This plugin is distributed under the MIT license. See the [LICENSE](LICENSE) file for details.

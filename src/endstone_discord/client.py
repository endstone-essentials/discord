import multiprocessing as mp
from typing import Any

import discord
from discord.ext import tasks


class DiscordClient(discord.Client):
    def __init__(
        self,
        *,
        config: dict,
        to_discord: mp.SimpleQueue,
        from_discord: mp.SimpleQueue,
        intents: discord.Intents,
        **options: Any,
    ):
        super().__init__(intents=intents, **options)
        self._config = config
        self._from_endstone = to_discord
        self._to_endstone = from_discord

    @tasks.loop(seconds=1)
    async def main_loop(self, channels: dict[str, discord.TextChannel]):
        while not self._from_endstone.empty():
            msg = self._from_endstone.get()
            event, data = msg["event"], msg.get("data", None)
            match event:
                case "join":
                    player_name = data["player_name"]
                    if "chat" in channels:
                        embed = discord.Embed(
                            description=f"{player_name} joined the server!",
                            color=discord.Color.green(),
                        )
                        await channels["chat"].send(embed=embed)
                case "leave":
                    player_name = data["player_name"]
                    if "chat" in channels:
                        embed = discord.Embed(
                            description=f"{player_name} left the server!",
                            color=discord.Color.red(),
                        )
                        await channels["chat"].send(embed=embed)
                case "chat":
                    player_name, message = data["player_name"], data["message"]
                    if "chat" in channels:
                        await channels["chat"].send(f"<{player_name}> {message}")
                case "close":
                    if "chat" in channels:
                        embed = discord.Embed(
                            description=f"🛑 Server stopped.",
                            color=discord.Color.red(),
                        )
                    await channels["chat"].send(embed=embed)
                    await self.close()

    async def on_ready(self) -> None:
        channels = {
            channel_type: self.get_channel(int(channel_id))
            for channel_type, channel_id in self._config["channels"].items()
        }
        if "chat" in channels:
            embed = discord.Embed(
                description=f"🟢 Server started.",
                color=discord.Color.green(),
            )
            await channels["chat"].send(embed=embed)
        self.main_loop.start(channels)

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if message.channel.id != int(self._config["channels"].get("chat", 0)) or int(self._config["channels"].get("console", 0)):
            return
        self._to_endstone.put({"event": "message", "data": {"message": f"<{message.author}> {message.content}"}})

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
        self.pre_player_total = 0

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
                            description=f"📥 {player_name} joined the server!",
                            color=discord.Color.green(),
                        )
                        await channels["chat"].send(embed=embed)
                case "leave":
                    player_name = data["player_name"]
                    if "chat" in channels:
                        embed = discord.Embed(
                            description=f"📤 {player_name} left the server!",
                            color=discord.Color.red(),
                        )
                        await channels["chat"].send(embed=embed)
                case "chat":
                    player_name, message = data["player_name"], data["message"]
                    if "chat" in channels:
                        await channels["chat"].send(f"<{player_name}> {message}")
                case "channel_topic":
                    player_list = data["player_list"]
                    if "chat" in channels and len(player_list) != self.pre_player_total:
                        await channels["chat"].edit(topic=f"Total players currently joined: {len(player_list)}")
                case "death":
                    if "chat" in channels:
                        death_message = data["death_message"]
                        embed = discord.Embed(
                            description=f"💀 {death_message}",
                            color=discord.Color.red(),
                        )
                        await channels["chat"].send(embed=embed)
                case "close":
                    if "chat" in channels:
                        embed = discord.Embed(
                            description=f"🛑 Server stopped.",
                            color=discord.Color.red(),
                        )
                    await channels["chat"].send(embed=embed)
                    await channels["chat"].edit(topic=f"Server offline.")
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
            await channels["chat"].edit(topic=f"Total player currently joined: 0")
        self.main_loop.start(channels)

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if message.channel.id == int(self._config["channels"].get("chat", 0)):
            self._to_endstone.put(
                {
                    "event": "message",
                    "data": {"message": f"<{message.author}> {message.content}"}
                }
            )
        if message.channel.id == int(self._config["channels"].get("console", 0)):
            self._to_endstone.put({
                "event": "console",
                "data": {"command": message.content}
            })

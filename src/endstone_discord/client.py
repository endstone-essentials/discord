import multiprocessing

import discord
from discord.ext import tasks


def main(queue: multiprocessing.SimpleQueue, config: dict):
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = discord.Client(queue=queue, config=config, intents=intents)

    @tasks.loop(seconds=1)
    async def main_loop(channels: dict[str, discord.TextChannel]):
        while not queue.empty():
            msg = queue.get()
            event, data = msg["event"], msg["data"]
            match event:
                case "join":
                    player_name = data["player_name"]
                    if "join" in channels:
                        await channels["join"].send(f"{player_name} joined the server!")
                case "leave":
                    player_name = data["player_name"]
                    if "leave" in channels:
                        await channels["leave"].send(f"{player_name} left the server!")

    @client.event
    async def on_ready() -> None:
        channels = {
            channel_type: client.get_channel(int(channel_id)) for channel_type, channel_id in config["channels"].items()
        }
        main_loop.start(channels)

    client.run(token=config["token"])

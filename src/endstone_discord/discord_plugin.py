import multiprocessing as mp
import os
import sys

import discord
from endstone.event import (
    event_handler,
    PlayerChatEvent, 
    PlayerJoinEvent, 
    PlayerQuitEvent,
    PlayerDeathEvent
)
from endstone.plugin import Plugin
from endstone import ColorFormat

from endstone_discord.client import DiscordClient

if sys.platform == "win32":
    mp.set_executable(os.path.join(sys.prefix, "python.exe"))
else:
    mp.set_executable(os.path.join(sys.prefix, "bin", "python"))


def run_discord_client(config: dict, to_discord: mp.SimpleQueue, from_discord: mp.SimpleQueue):
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = DiscordClient(config=config, to_discord=to_discord, from_discord=from_discord, intents=intents)
    client.run(token=config["token"])

# noinspection PyAttributeOutsideInit
class DiscordPlugin(Plugin):
    api_version = "0.4"

    def on_enable(self):
        self.save_default_config()
        self.register_events(self)

        self._to_discord = mp.SimpleQueue()
        self._from_discord = mp.SimpleQueue()
        self._process = mp.Process(target=run_discord_client, args=(self.config, self._to_discord, self._from_discord))
        self._process.start()

        self.server.scheduler.run_task_timer(self, self.handle_from_discord, delay=0, period=20 * 1)
        self.server.scheduler.run_task_timer(self, self.update_topic, delay=0, period=20 * 300)

    def on_disable(self):
        self._to_discord.put({"event": "close"})
        if self._process.is_alive():
            self._process.join()

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent) -> None:
        self._to_discord.put(
            {
                "event": "join",
                "data": {"player_name": event.player.name}
            }
        )

    @event_handler
    def on_player_quit(self, event: PlayerQuitEvent) -> None:
        self._to_discord.put(
            {
                "event": "leave",
                "data": {"player_name": event.player.name}
            }
        )

    @event_handler
    def on_player_chat(self, event: PlayerChatEvent) -> None:
        self._to_discord.put(
            {
                "event": "chat",
                "data": {"player_name": event.player.name, "message": event.message},
            }
        )
    
    @event_handler
    def on_player_death(self, event: PlayerDeathEvent) -> None:
        self._to_discord.put(
            {
                "event": "death",
                "data": {"death_message": event.death_message},
            }
        )

    def handle_from_discord(self):
        while not self._from_discord.empty():
            msg = self._from_discord.get()
            event, data = msg["event"], msg["data"]
            match event:
                case "message":
                    self.server.broadcast_message("[Discord] " + data["message"])
                case "console":
                    self.server.dispatch_command(self.server.command_sender, data["command"])
        
    def update_topic(self):
        self._to_discord.put(
            {
                "event": "channel_topic",
                "data": {"player_list": [player.name for player in self.server.online_players]}
            }
        )
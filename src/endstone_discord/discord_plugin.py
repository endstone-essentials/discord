import multiprocessing
import os
import sys

from endstone.event import event_handler, PlayerJoinEvent, PlayerQuitEvent
from endstone.plugin import Plugin

from endstone_discord.client import main

if sys.platform == "win32":
    multiprocessing.set_executable(os.path.join(sys.prefix, "python.exe"))
else:
    multiprocessing.set_executable(os.path.join(sys.prefix, "bin", "python"))


class DiscordPlugin(Plugin):
    api_version = "0.4"

    def on_enable(self):
        self.save_default_config()
        self.register_events(self)

        self._queue = multiprocessing.SimpleQueue()
        self._process = multiprocessing.Process(target=main, args=(self._queue, self.config))
        self._process.start()

    def on_disable(self):
        if self._process.is_alive():
            self._process.terminate()
            self._process.join()

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent) -> None:
        self._queue.put(
            {
                "event": "join",
                "data": {"player_name": event.player.name},
            }
        )

    @event_handler
    def on_player_quit(self, event: PlayerQuitEvent) -> None:
        self._queue.put(
            {
                "event": "leave",
                "data": {"player_name": event.player.name},
            }
        )

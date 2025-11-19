import logging
import threading
import time

from elite_relay.journal import JournalEntry, JournalMonitor
from elite_relay.plugins import registry
from elite_relay.settings import Settings

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=Settings.read().log_level,
    datefmt='%Y-%m-%d %H:%M:%S',
)


class App:
    def __init__(self):
        self.monitor = JournalMonitor(self.settings.logs_dir)
        self._stop = threading.Event()

    @property
    def settings(self) -> Settings:
        return Settings.read()

    def handle_entry(self, entry: JournalEntry):
        for i, plugin_config in enumerate(self.settings.plugins, start=1):
            plugin_id = f'{i} ({plugin_config})'
            if not plugin_config.enabled:
                logging.debug(
                    f'Plugin {plugin_id} is disabled, skipping handling {entry}'
                )
                continue
            plugin_cls = registry.get(plugin_config.plugin)
            if not plugin_cls:
                logging.warning(f'Plugin {plugin_id} is invalid')
                continue
            plugin_obj = plugin_cls(entry, plugin_config)
            # noinspection PyBroadException
            try:
                result = plugin_obj.handle()
            except Exception:
                logging.exception(f'Plugin {plugin_id} failed to handle {entry}')
                continue
            if result:
                logging.info(f'Plugin {plugin_id} handled {entry}')
                time.sleep(self.settings.event_interval)
            else:
                logging.debug(f'Plugin {plugin_id} skipped handling {entry}')

    def start(self):
        logging.info(
            f'Listening for new Elite: Dangerous journal entries in "{self.settings.logs_dir}"'
        )
        while not self._stop.is_set():
            try:
                for entry in self.monitor.iter_entries():
                    self.handle_entry(entry)
                time.sleep(self.settings.poll_interval)
            except KeyboardInterrupt:
                self.stop()
        logging.info('Shutting down')

    def stop(self):
        self._stop.set()


def run():
    App().start()


if __name__ == '__main__':
    run()

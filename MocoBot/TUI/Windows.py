import _thread

from textual.app import App, ComposeResult
from textual.widgets import Log
from ..System import init


class LogApp(App):
    """An app with a simple log."""

    def compose(self) -> ComposeResult:
        yield Log()

    def on_ready(self) -> None:
        self.print("Hello, World!")
        _thread.start_new_thread(init, (True, self))

    def print(self, s):
        log = self.query_one(Log)
        log.write_line(f"{s}")

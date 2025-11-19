"""Status bar widget for the GORO TUI."""
import logging
from datetime import datetime
from typing import List, Deque
from collections import deque
from rich.text import Text
from textual.reactive import reactive
from textual.widgets import Static, RichLog
from textual.containers import Container

class StatusBar(Container):
    """Status bar widget with logging support."""

    status = reactive("Ready")
    max_log_entries = 1000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_entries: Deque[str] = deque(maxlen=self.max_log_entries)
        self.rich_log = RichLog(highlight=True, markup=True, wrap=True)
        self.rich_log.styles.height = "100%"
        self.rich_log.styles.border = ("round", "gray")

    def compose(self):
        yield self.rich_log

    def on_mount(self) -> None:
        """Set up logging when the widget is mounted."""
        # Add a custom handler to capture logs
        self.handler = LogHandler(self)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self.handler.setFormatter(formatter)
        logging.basicConfig(
            level=logging.INFO,
            handlers=[self.handler],
            force=True
        )
        logging.info("Application started")

    def watch_status(self, status: str) -> None:
        """Update the status message and log it."""
        self.log(f"Status: {status}")

    def log(self, message: str, level: str = "info") -> None:
        """Add a log message to the status bar.
        
        Args:
            message: The message to log
            level: The log level (info, warning, error, debug)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        level_color = {
            "info": "green",
            "warning": "yellow",
            "error": "red",
            "debug": "blue"
        }.get(level.lower(), "white")
        
        log_text = Text()
        log_text.append(f"[{timestamp}] ", style=f"dim {level_color}")
        log_text.append(f"{message}", style=level_color)
        
        self.rich_log.write(log_text)
        self.rich_log.scroll_end(animate=False)


class LogHandler(logging.Handler):
    """Custom logging handler that writes to the status bar."""
    
    def __init__(self, status_bar: StatusBar):
        super().__init__()
        self.status_bar = status_bar
    
    def emit(self, record):
        """Eit a log record to the status bar."""
        try:
            msg = self.format(record)
            self.status_bar.log(msg, record.levelname.lower())
        except Exception:
            self.handleError(record)

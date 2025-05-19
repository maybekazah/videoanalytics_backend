
from rich.console import Console
from rich.logging import RichHandler
from logging.handlers import RotatingFileHandler
import logging

from api.configs.app import DJANGO_LOGS, DJANGO_DEBUG

console = Console(force_terminal=True)


class ColorfulFormatter(logging.Formatter):
    """Кастомный форматтер для добавления цвета в текст логов."""
    LEVEL_COLORS = {
        "DEBUG": "[green]",
        "INFO": "[cyan]",
        "WARNING": "[yellow]",
        "ERROR": "[bold red]",
        "CRITICAL": "[bold white on red]",
    }

    def format(self, record):
        level_color = self.LEVEL_COLORS.get(record.levelname, "")
        message = super().format(record)
        return f"{level_color}{message}[/]"


def setup_logging():
    file_handler = RotatingFileHandler(
        filename=f'{DJANGO_LOGS}django.log',
        maxBytes=5 * 1024 * 1024,  
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    console_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        rich_tracebacks=True,
        markup=True
    )

    console_handler.setFormatter(ColorfulFormatter("%(message)s"))

    if DJANGO_DEBUG:
        logging_level = logging.DEBUG
    else: 
        logging_level = logging.WARNING    
    # Настройка логирования
    logging.basicConfig(
        level=logging_level,
        handlers=[file_handler, console_handler]  # Файловый и консольный обработчики
    )


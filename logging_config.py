import copy
import logging
import logging.config
from pathlib import Path

class CompactMessage(logging.Formatter):
    
    def format(self, record):
        info = copy.copy(record)
        info.exc_info = None
        info.exc_text = None
        info.stack_info = None
        return super().format(info)

def setup_logging():
    Path("logs").mkdir(exist_ok=True)

    config = {
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "console": {
                "()": CompactMessage,
                "format": "%(asctime)s | %(levelname)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "file": {
                "format": (
                    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
                ),
            },
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "console",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/app.log",
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 5,
                "encoding": "utf-8",
                "level": "DEBUG",
                "formatter": "file",
            },
        },

        "loggers": {
            "sqlalchemy": {"level": "WARNING"},
            "httpx": {"level": "WARNING"},
            "httpcore": {"level": "WARNING"},
            "urllib3": {"level": "WARNING"},
        },

        "root": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
        },
    }

    logging.config.dictConfig(config)
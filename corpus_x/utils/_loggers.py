import sys
from pathlib import Path

from loguru import logger


def set_basic_handler(filename: str):
    return [
        {
            "sink": sys.stdout,
            "format": "{message}",
            "level": "ERROR",
        },
        {
            "sink": f"logs/{filename}.log",
            "format": "{message}",
            "level": "WARNING",
            "serialize": True,
        },
    ]


def set_info_handler(filename: str):
    return [
        {
            "sink": sys.stdout,
            "format": "{message}",
            "level": "DEBUG",
        },
        {
            "sink": f"logs/{filename}.log",
            "format": "{message}",
            "level": "INFO",
            "serialize": True,
        },
    ]


logger.configure(
    handlers=[
        {
            "sink": "logs/debug.log",
            "format": "{message}",
            "level": "DEBUG",
            "serialize": True,
        },
        {
            "sink": "logs/error.log",
            "format": "{message}",
            "level": "ERROR",
            "serialize": True,
        },
    ]
)


def clear_logs(p: Path = Path().cwd() / "logs"):
    for i in p.glob("*"):
        if i.is_file():
            i.unlink()

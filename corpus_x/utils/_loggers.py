import sys


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

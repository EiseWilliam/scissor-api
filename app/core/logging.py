# def log_this(message) -> None:
#     print(f"LOG: {message}")
from typing import Literal

from termcolor import colored
from termcolor.termcolor import Color  # type: ignore


def pick_color(prefix: Literal["INFO", "ERROR", "WARNING", "DONE"]) -> Color:
    if prefix == "INFO":
        return "cyan"
    elif prefix == "ERROR":
        return "red"
    elif prefix == "WARNING":
        return "yellow"
    elif prefix == "DONE":
        return "green"
    else:
        return "white"


def log_this(message: str | list, prefix: Literal["INFO", "ERROR", "WARNING", "DONE"] = "INFO") -> None:
    """
    prints to terminal the given message with a colored 'INFO' prefix.

    """
    color = pick_color(prefix)
    if isinstance(message, list):
        for m in message:
            print(colored(f"{prefix}:    ", color), m)
    elif isinstance(message, str):
        print(colored(f"{prefix}:    ", color), message[0].upper() + message.strip()[1:])
    else:
        return None

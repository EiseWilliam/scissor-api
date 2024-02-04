# def log_this(message) -> None:
#     print(f"LOG: {message}")
from calendar import c
from termcolor import colored, cprint, ATTRIBUTES, HIGHLIGHTS, COLORS
    

def log_this(message: str) -> None:
    """
    prints to terminal the given message with a colored 'INFO' prefix.

    """
    print(colored("INFO:    ", "cyan"), message[0].upper() + message.strip()[1:])

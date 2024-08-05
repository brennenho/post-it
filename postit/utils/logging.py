import logging

from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger with the specified name.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: A logger instance.
    """
    return logging.getLogger(name)

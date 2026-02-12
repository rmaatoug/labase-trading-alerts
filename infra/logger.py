import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(log_path: str = "logs/bot.log") -> logging.Logger:
    """
    Single source of truth logger:
    - always logs to file (rotating)
    - safe to call multiple times (no duplicate handlers)
    """
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("labase")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Remove existing handlers (prevents duplicates / stale state)
    for h in list(logger.handlers):
        logger.removeHandler(h)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    fh = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=10)
    fh.setFormatter(fmt)
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)

    return logger

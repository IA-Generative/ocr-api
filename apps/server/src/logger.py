from loguru import logger as _logger
import os
import sys
from typing import Optional
from logging import Logger


def setup_logger(name: str = "ocr_api", level: Optional[str] = None, *, serialize: bool = True) -> Logger:
    """Configure et retourne un logger `loguru` lié au service.

    - Utilise `ENVIRONMENT` pour choisir le niveau par défaut (development -> DEBUG, else INFO).
    - Remplace les handlers existants et ajoute une sortie console (stderr).
    - Si `log_file` est fourni ou `LOG_FILE` env var est définie, ajoute aussi un sink fichier.
    """
    env = os.getenv("ENVIRONMENT", "production")
    default_level = "DEBUG" if env == "development" else "INFO"
    level = level or os.getenv("LOG_LEVEL") or default_level

    # Clear existing handlers and add our sinks
    _logger.remove()
    _logger.add(
        sys.stderr,
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {extra[service]} | {message}",
        serialize=serialize,
    )

    return _logger.bind(service=name)


# Initialise le logger principal
service_name = os.getenv("SERVICE_NAME", "ocr_worker")
logger = setup_logger(service_name)


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"

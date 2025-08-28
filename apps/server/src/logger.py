import logging
import logging.config
import yaml
import os
from pathlib import Path
from typing import Optional


def load_logging_config(config_path: str = "../configs/logging.yaml", environment: Optional[str] = None) -> dict:
    """
    Charge la configuration de logging depuis un fichier YAML

    Args:
        config_path: Chemin vers le fichier de configuration
        environment: Environnement spécifique (development, production, testing)

    Returns:
        Configuration de logging
    """
    config_file = Path(__file__).parent / config_path

    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Applique la configuration spécifique à l'environnement si fournie
    if environment and environment in config.get("environments", {}):
        env_config = config["environments"][environment]
        # Merge la configuration d'environnement avec la configuration de base
        for key, value in env_config.items():
            if key in config:
                if isinstance(config[key], dict) and isinstance(value, dict):
                    config[key].update(value)
                else:
                    config[key] = value

    return config


def setup_logger(name: str = "ocr_api", config_path: str = "../configs/logging.yaml") -> logging.Logger:
    """
    Configure et retourne un logger basé sur la configuration YAML

    Args:
        name: Nom du logger
        config_path: Chemin vers le fichier de configuration

    Returns:
        Logger configuré
    """
    # Détermine l'environnement depuis les variables d'environnement
    environment = os.getenv("ENVIRONMENT", "production")

    # Charge et applique la configuration
    config = load_logging_config(config_path, environment)
    logging.config.dictConfig(config)

    return logging.getLogger(name)


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

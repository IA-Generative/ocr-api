import logging
import logging.config
import yaml
import os
from pathlib import Path
from typing import Optional


def _deep_merge(base: dict, override: dict) -> dict:
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


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
        # Merge en profondeur (une fusion superficielle écraserait par exemple
        # loggers.ocr_worker.propagate en ne gardant que les clés surchargées).
        _deep_merge(config, config["environments"][environment])

    return config


class _ComponentFilter(logging.Filter):
    """Injects the deploy-provided COMPONENT (api/worker) into every log record."""

    def __init__(self, component: str):
        super().__init__()
        self.component = component

    def filter(self, record: logging.LogRecord) -> bool:
        record.component = self.component
        return True


def setup_logger(
    name: str = "ocr_api", config_path: str = "../configs/logging.yaml", component: str = "unknown"
) -> logging.Logger:
    """
    Configure et retourne un logger basé sur la configuration YAML

    Args:
        name: Nom du logger
        config_path: Chemin vers le fichier de configuration
        component: Composant du déploiement (api, worker), injecté dans chaque log

    Returns:
        Logger configuré
    """
    # Détermine l'environnement depuis les variables d'environnement
    environment = os.getenv("ENVIRONMENT", "production")

    # Charge et applique la configuration
    config = load_logging_config(config_path, environment)
    logging.config.dictConfig(config)

    for handler in logging.root.handlers:
        handler.addFilter(_ComponentFilter(component))

    return logging.getLogger(name)


# COMPONENT is set explicitly by the Helm chart ("api" or "worker"). SERVICE_NAME
# now defaults from it, so a pod that misses the SERVICE_NAME override logs under
# its own component's name instead of always falling back to the worker's.
component = os.getenv("COMPONENT", "worker")
service_name = os.getenv("SERVICE_NAME", f"ocr_{component}")
logger = setup_logger(service_name, component=component)


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"

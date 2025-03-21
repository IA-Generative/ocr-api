import toml
from pathlib import Path


def get_version():
    pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"

    try:
        with open(pyproject_path, "r") as f:
            data = toml.loads(f.read())
            return data["project"]["version"]
    except Exception:
        return "0.0.0"  # Valeur par défaut si erreur


__version__ = get_version()

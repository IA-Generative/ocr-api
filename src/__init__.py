from importlib.metadata import version, PackageNotFoundError
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


try:
    __version__ = version("mcr_gateway")
except PackageNotFoundError:
    __version__ = get_version()  # Valeur par défaut si le package n'est pas installé
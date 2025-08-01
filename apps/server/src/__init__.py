import toml
from pathlib import Path


def get_version():
    pyproject_path = Path(__file__).resolve().parent / "pyproject.toml"

    try:
        with open(pyproject_path, "r") as f:
            data = toml.loads(f.read())
            return data["project"]["version"], data["project"]["name"]
    except Exception:
        return "0.1.0", "ocr-api"


__version__, __name__ = get_version()

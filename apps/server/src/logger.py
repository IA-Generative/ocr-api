import logging
from uuid import uuid4
from pythonjsonlogger.json import JsonFormatter

logger = logging.getLogger(str(uuid4()))
logger.setLevel(logging.DEBUG)
logger.handlers = []
handler = logging.StreamHandler()

formatter = JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(name)s %(pathname)s %(lineno)d %(message)s",
    rename_fields={
        "asctime": "@timestamp",
        "levelname": "level",
        "pathname": "file_path",
        "lineno": "line",
        "message": "msg",
    },
)
# handler.setFormatter(formatter)

logger.addHandler(handler)


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"

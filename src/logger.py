import logging 
from uuid import uuid4
from pythonjsonlogger import jsonlogger

logger = logging.getLogger(str(uuid4()))
logger.setLevel(logging.DEBUG)
logger.handlers.clear()
handler = logging.StreamHandler()

formatter = jsonlogger.JsonFormatter(
    fmt='%(asctime)s %(levelname)s %(name)s %(pathname)s %(lineno)d %(message)s',
    rename_fields={
        'asctime': '@timestamp',
        'levelname': 'level',
        'pathname': 'file_path',
        'lineno': 'line',
        'message': 'msg'
    }
)
handler.setFormatter(formatter)

logger.addHandler(handler)
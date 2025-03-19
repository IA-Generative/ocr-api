import logging
import datetime
from fastapi import APIRouter, status
from ..schemas.health import HealthCheck
from .inference import ocr_model
from .. import __version__

logger = logging.getLogger(__name__)

router = APIRouter()

up_time = datetime.datetime.now().isoformat()


@router.get("/", tags=["healthcheck"],
            summary="Perform a Health Check",
            response_description="Return HTTP Status Code 200 (OK)",
            status_code=status.HTTP_200_OK,
            response_model=HealthCheck,)
async def get_health():
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """

    return {
        "version": __version__,
        "up_time": up_time,
        "extras": {},
        "dependencies": [{"paddle_version": ocr_model.__version__}],
    }

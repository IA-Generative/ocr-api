import datetime
from fastapi import APIRouter, status
from src.schemas.health import Health, HealthError
from src import __version__, __name__
from src.logger import logger
from src.connector import s3_client_connector, get_db

router = APIRouter(tags=["Health"])

up_time = datetime.datetime.now().isoformat()


@router.get(
    "/health",
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=Health,
)
async def get_health():
    logger.debug("health hit")
    dependencies = []
    status = "healthy"

    health_s3 = s3_client_connector.get_health()
    dependencies.append(health_s3)
    if isinstance(health_s3, HealthError):
        status = "unhealthy"

    return Health(
        name=__name__,
        version=__version__,
        up_time=up_time,
        status=status,
        dependencies=dependencies,
    )

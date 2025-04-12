import datetime
from fastapi import APIRouter, status
from src.schemas.health import Health
from src import __version__, __name__
from fastdeploy import __version__ as fast_version
from src.logger import logger

router = APIRouter()

up_time = datetime.datetime.now().isoformat()


@router.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=Health,
)
async def get_health():

    logger.debug("health hit")

    return Health(
        name=__name__,
        version=__version__,
        up_time=up_time,
        status="healthy",
        dependencies=[
            Health(
                name="fastdeploy",
                version=fast_version,
                up_time=up_time,
                status="healthy",
            )
        ],
    )

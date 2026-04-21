import asyncio
import datetime
from fastapi import APIRouter, Response, status

from src import __name__, __version__
from src.connector.db_connector import db_client_connector
from src.connector.broker_connector import redis_client_connector
from src.schemas.health import Health

from ..connectors import s3_client_connector

router = APIRouter(tags=["Health"])

up_time = datetime.datetime.now().isoformat()


@router.get(
    "/health",
    summary="Perform a Health Check",
    response_description="Return health of all dependencies",
    status_code=status.HTTP_200_OK,
    response_model=Health,
)
async def get_health(response: Response):
    # Run all health checks concurrently without blocking the event loop
    db_health, redis_health, s3_health = await asyncio.gather(
        db_client_connector.aget_health(),
        asyncio.to_thread(redis_client_connector.get_health),
        asyncio.to_thread(s3_client_connector.get_health),
    )

    dependencies = [db_health, redis_health, s3_health]
    api_status = "healthy"
    for health_dep in dependencies:
        if health_dep.status == "unhealthy":
            api_status = "unhealthy"
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return Health(
        name=__name__,
        version=__version__,
        up_time=up_time,
        status=api_status,
        dependencies=dependencies,
    )

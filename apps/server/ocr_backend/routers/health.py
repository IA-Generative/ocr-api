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
    dependencies = []
    api_status = "healthy"
    for dep in [db_client_connector, redis_client_connector, s3_client_connector]:
        health_dep: Health = dep.get_health()
        if health_dep.status == "unhealthy":
            api_status = "unhealthy"
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        dependencies.append(health_dep)

    return Health(
        name=__name__,
        version=__version__,
        up_time=up_time,
        status=api_status,
        dependencies=dependencies,
    )

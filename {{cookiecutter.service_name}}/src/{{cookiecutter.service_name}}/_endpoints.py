"""Endpoints of the service."""

import typing as t

import dependency_injector.wiring as di_wiring
import fastapi as fa
import fastapi.responses as fa_resp

import {{cookiecutter.service_name}}._containers as di_c
import {{cookiecutter.service_name}}._dtos as dtos
import {{cookiecutter.service_name}}._services as svc


RESOURCE_PREFIX: t.Final[str] = "/health"
api_router = fa.APIRouter(
    prefix=RESOURCE_PREFIX, default_response_class=fa_resp.ORJSONResponse
)


@api_router.get("/")
@di_wiring.inject
async def return_health(
    healthcheck_svc: svc.HealthService = fa.Depends(
        di_wiring.Provide[di_c.Container.healthcheck_svc]
    ),
) -> dtos.HealthCheckDTO:
    """Return health status.

    Args:
        healthcheck_svc: A service that handles healthchecks' use cases.

    Returns:
        The health status.
    """
    healthcheck = await healthcheck_svc.get_healthcheck()
    return dtos.HealthCheckDTO(**healthcheck.dict())

import logging

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.config import config
from src.service.health_check.checks import pg, sentry, uptime
from src.service.health_check.dto import HealthOut
from src.service.health_check.service import HealthCheckService, Probe, ProbeResult


logger = logging.getLogger(__name__)


class HealthCheckRouter(APIRouter):
    def __init__(self, *probes: Probe):
        super().__init__()

        for probe in probes:
            self.add_probe_route(probe)

    def add_probe_route(self, probe: Probe):
        async def handle_request(
            health_check: HealthCheckService = Depends(),
        ):
            probe_result: ProbeResult = await health_check.run_probe(probe)
            return JSONResponse(
                content=jsonable_encoder(
                    HealthOut(
                        status=probe_result.status.name,
                        version=config.app_version,
                        checks=probe_result.checks,
                    )
                ),
                status_code=probe_result.status.code,
                media_type="application/health+json",
            )

        self.add_api_route(
            path=f"/{probe.name}",
            endpoint=handle_request,
            response_model=HealthOut,
            summary=f"Probe {probe.name}",
            tags=["Telemetry"],
            responses={
                status.HTTP_200_OK: {
                    "description": "Indicates that service is healty",
                },
                status.HTTP_503_SERVICE_UNAVAILABLE: {
                    "description": "Indicates that service is unhealty",
                },
            },
        )


health_check_router = HealthCheckRouter(
    Probe(
        name="live",
        checks=[
            uptime.UptimeCheck(),
        ],
    ),
    Probe(
        name="ready",
        checks=[
            pg.PgCheck(component_id="pg:online"),
            sentry.SentryCheck(component_id="sentry:configured"),
        ],
    ),
)

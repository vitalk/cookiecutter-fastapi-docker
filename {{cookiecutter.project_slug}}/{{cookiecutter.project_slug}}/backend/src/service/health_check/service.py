import asyncio
from itertools import chain, groupby
import logging

from src.service.health_check.dto import (
    CheckResult,
    Probe,
    ProbeResult,
    Status,
)


logger = logging.getLogger(__name__)


healthy_status = Status(code=200, name="pass")
warn_status = Status(code=200, name="warn")
fail_status = Status(code=503, name="fail")


class HealthCheckService:
    async def run_probe(self, probe: Probe) -> ProbeResult:
        checks = [check() for check in probe.checks]
        check_results: list[CheckResult] = await asyncio.gather(*checks)

        checks_by_component = {}
        for component_id, checks in groupby(
            check_results,
            key=lambda c: c.component_id,
        ):
            checks_by_component[component_id] = list(checks)

        probe_status = await self.get_service_status(checks_by_component)

        return ProbeResult(
            status=probe_status,
            checks=checks_by_component,
        )

    async def get_service_status(
        self,
        checks: dict[str, list[CheckResult]],
    ) -> Status:
        for check in chain.from_iterable(checks.values()):
            if check.status == warn_status.name:
                return warn_status
            elif check.status == fail_status.name:
                return fail_status

        return healthy_status

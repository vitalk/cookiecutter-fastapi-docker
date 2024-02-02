from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from itertools import chain, groupby
import logging

from src.service.health_check.dto import (
    CheckResult,
    CheckComponentType,
)


logger = logging.getLogger(__name__)


@dataclass
class Check(ABC):
    component_id: str
    component_type: CheckComponentType = CheckComponentType.component

    @abstractmethod
    async def __call__(self) -> CheckResult:
        raise NotImplementedError


@dataclass(frozen=True)
class Probe:
    name: str
    checks: list[Check]


@dataclass(frozen=True)
class ProbeResultStatus:
    code: int
    name: str


@dataclass(frozen=True)
class ProbeResult:
    status: ProbeResultStatus
    checks: dict[str, list[CheckResult]]


healthy_status = ProbeResultStatus(code=200, name="pass")
warn_status = ProbeResultStatus(code=200, name="warn")
fail_status = ProbeResultStatus(code=503, name="fail")


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

        probe_status = await self.get_probe_result_status(checks_by_component)

        return ProbeResult(
            status=probe_status,
            checks=checks_by_component,
        )

    async def get_probe_result_status(
        self,
        checks: dict[str, list[CheckResult]],
    ) -> ProbeResultStatus:
        for check in chain.from_iterable(checks.values()):
            if check.status == warn_status.name:
                return warn_status
            elif check.status == fail_status.name:
                return fail_status

        return healthy_status

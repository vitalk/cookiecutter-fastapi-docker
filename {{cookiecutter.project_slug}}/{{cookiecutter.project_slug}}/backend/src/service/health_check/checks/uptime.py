from dataclasses import dataclass
from datetime import UTC, datetime
import time

from src.service.health_check.dto import CheckComponentType, CheckResult
from src.service.health_check.service import Check, healthy_status


@dataclass
class UptimeCheck(Check):
    component_id: str = "uptime"
    component_type: CheckComponentType = CheckComponentType.system

    def __post_init__(self):
        self.started_at = time.monotonic()

    async def __call__(self) -> CheckResult:
        uptime = time.monotonic() - self.started_at
        return CheckResult(
            component_id=self.component_id,
            component_type=self.component_type,
            observed_value=f"{uptime:.3f}",
            observed_unit="s",
            status=healthy_status.name,
            time=datetime.now(UTC).isoformat(),
        )

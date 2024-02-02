from datetime import UTC, datetime

from src.config import config
from src.service.health_check.dto import CheckResult
from src.service.health_check.service import Check, healthy_status, warn_status


class SentryCheck(Check):
    component_id = "sentry:configured"

    async def __call__(self) -> CheckResult:
        check_result = healthy_status if config.sentry_dsn else warn_status

        return CheckResult(
            component_id=self.component_id,
            component_type=self.component_type,
            status=check_result.name,
            time=datetime.now(UTC).isoformat(),
        )

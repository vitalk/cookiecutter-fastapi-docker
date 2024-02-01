from dataclasses import dataclass
from datetime import datetime, UTC

from sqlalchemy import text

from src.infra.database.session import async_session
from src.service.health_check.dto import (
    Check,
    CheckComponentType,
    CheckResult,
    Status,
)
from src.service.health_check.service import fail_status, healthy_status


@dataclass
class PsqlCheck(Check):
    component_type: CheckComponentType = CheckComponentType.datastore

    async def __call__(self) -> CheckResult:
        check_result: Status

        try:
            async with async_session() as session:
                await session.execute(text("select true"))
        except:  # noqa: E722
            check_result = fail_status
        else:
            check_result = healthy_status

        return CheckResult(
            component_id=self.component_id,
            component_type=self.component_type,
            status=check_result.name,
            time=datetime.now(UTC).isoformat(),
        )

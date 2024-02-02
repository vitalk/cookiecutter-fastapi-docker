"""
https://datatracker.ietf.org/doc/html/draft-inadarei-api-health-check

Example Output:

    {
      "status": "pass",
      "version": "1",
      "releaseId": "1.2.2",
      "serviceId": "f03e522f-1f44-4062-9b55-9587f91c9c41",
      "description": "health of authz service",
      "checks": {
        "cassandra:responseTime": [
          {
            "componentId": "dfd6cf2b-1b6e-4412-a0b8-f6f7797a60d2",
            "componentType": "datastore",
            "observedValue": 250,
            "observedUnit": "ms",
            "status": "pass",
            "affectedEndpoints" : [
              "/users/{userId}",
              "/customers/{customerId}/status",
              "/shopping/{anything}"
            ],
            "time": "2018-01-17T03:36:48Z",
            "output": ""
          }
        ],
        "cassandra:connections": [
          {
            "componentId": "dfd6cf2b-1b6e-4412-a0b8-f6f7797a60d2",
            "componentType": "datastore",
            "observedValue": 75,
            "status": "warn",
            "time": "2018-01-17T03:36:48Z",
            "output": "",
            "links": {
              "self": "http://api.example.com/dbnode/dfd6cf2b/health"
            }
          }
        ],
        "uptime": [
          {
            "componentType": "system",
            "observedValue": 1209600.245,
            "observedUnit": "s",
            "status": "pass",
            "time": "2018-01-17T03:36:48Z"
          }
        ],
        "cpu:utilization": [
          {
            "componentId": "6fd416e0-8920-410f-9c7b-c479000f7227",
            "node": 1,
            "componentType": "system",
            "observedValue": 85,
            "observedUnit": "percent",
            "status": "warn",
            "time": "2018-01-17T03:36:48Z",
            "output": ""
          }
        ],
        "memory:utilization": [
          {
            "componentId": "6fd416e0-8920-410f-9c7b-c479000f7227",
            "node": 1,
            "componentType": "system",
            "observedValue": 8.5,
            "observedUnit": "GiB",
            "status": "warn",
            "time": "2018-01-17T03:36:48Z",
            "output": ""
          }
        ]
      }
    }

"""
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class CheckComponentType(str, Enum):
    component = "component"
    datastore = "datastore"
    system = "system"


class Base(BaseModel):
    ...


class CheckResult(Base):
    component_id: str = Field(
        default=...,
        description=(
            "A unique identifier of an instance of a specific sub-component/dependency of a service"
        ),
    )
    component_type: CheckComponentType = Field(
        default=...,
        description="A type of the component",
    )
    observed_value: Any = Field(
        default=None,
        description="Observed value of the component",
    )
    observed_unit: str | None = Field(
        default=None,
        description="Clarifies the unit of measurement in which observed value is reported",
    )
    status: str = Field(
        default=...,
        description="Indicates whether the service status is acceptable or not",
    )
    time: str | None = Field(
        default=None,
        description="The date-time, in ISO8601 format, at which the request was processed",
    )

    @field_validator("time")
    def validate_time_iso_8061(cls, v: str) -> str:  # noqa: N805
        try:
            datetime.fromisoformat(v)
        except ValueError as exc:
            raise exc
        return v


class HealthOut(Base):
    status: str = Field(
        default=...,
        description="Indicates whether the service status is acceptable or not",
    )
    version: str | None = Field(
        default=None,
        description="Public version of the service",
    )
    checks: dict[str, list[CheckResult]] | None = Field(
        default=None,
        description="Provides health status of logical downstream dependency or sub-component",
    )

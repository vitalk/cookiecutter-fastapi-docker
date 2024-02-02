from fastapi.testclient import TestClient

from src.config import AppConfig
from tests.base import BaseTestCase


class TestHealthLivenessProbe(BaseTestCase):
    base_url: str = "/api/0/health/live"

    async def test_get_ok(
        self,
        client: TestClient,
        test_app_config: AppConfig,
    ):
        res = client.get(self.get_url())
        assert res.status_code == 200

        given_json = res.json()
        assert given_json["status"] == "pass"
        assert given_json["version"] == test_app_config.app_version
        assert given_json["checks"]["uptime"]


class TestHealthReadinessProbe(BaseTestCase):
    base_url: str = "/api/0/health/ready"

    async def test_get_ok(
        self,
        client: TestClient,
        test_app_config: AppConfig,
    ):
        res = client.get(self.get_url())
        assert res.status_code == 200

        given_json = res.json()
        assert given_json["status"] == "warn"
        assert given_json["version"] == test_app_config.app_version
        assert given_json["checks"]["pg:online"]

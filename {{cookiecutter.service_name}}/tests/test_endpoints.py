"""Tests for the service's endpoints."""
import uuid

import fastapi.testclient as fa_tc
import pytest
import starlette.status as http_status


class TestHealth:
    """Tests for the health check endpoint.

    This is an example on how to write a test class for some behavior. In
    concrete services, you should rewrite it to suit your needs.
    """

    @pytest.fixture
    def health_endpoint(self) -> str:
        """Return the healthcheck endpoint address.

        Returns:
            The address of the healthcheck endpoint.
        """
        return "/health"

    def test_health_ok(
        self, test_client: fa_tc.TestClient, health_endpoint: str
    ) -> None:
        """Healthchecks should return OK.

        Args:
            test_client: The test client.
            health_endpoint: The endpoint that accepts healthchecks.
        """
        health_resp = test_client.get(health_endpoint)
        health_resp_json = health_resp.json()

        assert health_resp.status_code == http_status.HTTP_200_OK
        assert health_resp_json["status"] == "ok"
        assert uuid.UUID(health_resp_json["id"])

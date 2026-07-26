import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    """Verify GET / returns HTTP 200 with HTML landing dashboard."""
    response = client.get("/")
    assert response.status_code == 200
    assert "DeployGuard" in response.text
    assert "Blue/Green Deployment Demo" in response.text


def test_health_healthy_default():
    """Verify GET /health returns HTTP 200 and healthy status when FORCE_UNHEALTHY is false/unset."""
    with patch.dict(os.environ, {"FORCE_UNHEALTHY": "false"}, clear=False):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


def test_health_unhealthy_simulation():
    """Verify GET /health returns HTTP 503 and unhealthy status when FORCE_UNHEALTHY=true."""
    with patch.dict(os.environ, {"FORCE_UNHEALTHY": "true"}, clear=False):
        response = client.get("/health")
        assert response.status_code == 503
        assert response.json() == {"status": "unhealthy"}


def test_version_endpoint():
    """Verify GET /version returns exact deployment environment information."""
    env_vars = {
        "APP_VERSION": "v2.1.0",
        "ENVIRONMENT": "staging",
        "DEPLOYMENT_SLOT": "GREEN",
        "COMMIT_SHA": "fed9876",
        "BUILD_NUMBER": "42",
        "FORCE_UNHEALTHY": "false",
    }
    with patch.dict(os.environ, env_vars, clear=False):
        response = client.get("/version")
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "application": "DeployGuard",
            "version": "v2.1.0",
            "environment": "staging",
            "deployment_slot": "GREEN",
            "commit": "fed9876",
            "build_number": "42",
        }


def test_api_info_endpoint():
    """Verify GET /api/info returns complete metadata and operational health state."""
    env_vars = {
        "APP_VERSION": "v1.0.0",
        "ENVIRONMENT": "production",
        "DEPLOYMENT_SLOT": "BLUE",
        "COMMIT_SHA": "abc1234",
        "BUILD_NUMBER": "12",
        "FORCE_UNHEALTHY": "false",
    }
    with patch.dict(os.environ, env_vars, clear=False):
        response = client.get("/api/info")
        assert response.status_code == 200
        data = response.json()
        assert data["application"] == "DeployGuard"
        assert data["version"] == "v1.0.0"
        assert data["environment"] == "production"
        assert data["deployment_slot"] == "BLUE"
        assert data["commit"] == "abc1234"
        assert data["build_number"] == "12"
        assert data["health_status"] == "healthy"
        assert data["force_unhealthy"] is False


def test_environment_variable_reflection_in_root():
    """Verify environment variables are reflected on the dashboard HTML rendering."""
    env_vars = {
        "APP_VERSION": "v3.0.0-rc1",
        "ENVIRONMENT": "production",
        "DEPLOYMENT_SLOT": "GREEN",
        "COMMIT_SHA": "7894561",
        "BUILD_NUMBER": "99",
    }
    with patch.dict(os.environ, env_vars, clear=False):
        response = client.get("/")
        assert response.status_code == 200
        assert "v3.0.0-rc1" in response.text
        assert "GREEN" in response.text
        assert "#99" in response.text

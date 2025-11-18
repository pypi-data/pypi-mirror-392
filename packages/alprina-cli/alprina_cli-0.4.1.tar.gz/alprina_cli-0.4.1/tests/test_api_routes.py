"""
Comprehensive API Routes Testing Suite
Tests all FastAPI endpoints to ensure full functionality
"""

import pytest
import os
from fastapi.testclient import TestClient
from alprina_cli.api.main import app

# Test client
client = TestClient(app)

# Test data
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_CODE = """
def unsafe_query(user_input):
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    return query
"""


class TestHealthAndRoot:
    """Test basic health and root endpoints"""

    def test_root_endpoint(self):
        """Test GET /"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Alprina API"
        assert "version" in data
        assert "endpoints" in data

    def test_health_check(self):
        """Test GET /health"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestAuthenticationRoutes:
    """Test authentication endpoints"""

    @pytest.fixture(scope="class")
    def test_user_credentials(self):
        """Create a test user and return credentials"""
        # Register a test user
        response = client.post(
            "/v1/auth/register",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "full_name": "Test User"
            }
        )

        if response.status_code == 201:
            data = response.json()
            return {
                "email": TEST_EMAIL,
                "api_key": data["api_key"],
                "user_id": data["user_id"]
            }
        elif response.status_code == 400:
            # User already exists, try to login
            login_response = client.post(
                "/v1/auth/login",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                }
            )
            if login_response.status_code == 200:
                login_data = login_response.json()
                return {
                    "email": TEST_EMAIL,
                    "api_key": login_data["api_keys"][0]["key"],
                    "user_id": login_data["user"]["id"]
                }

        pytest.skip("Cannot create or login test user")

    def test_register_new_user(self):
        """Test POST /v1/auth/register"""
        import random
        random_email = f"test{random.randint(1000, 9999)}@example.com"

        response = client.post(
            "/v1/auth/register",
            json={
                "email": random_email,
                "password": TEST_PASSWORD,
                "full_name": "New Test User"
            }
        )

        # Should either succeed (201) or fail because user exists (400)
        assert response.status_code in [201, 400]

        if response.status_code == 201:
            data = response.json()
            assert "api_key" in data
            assert "user_id" in data
            assert data["email"] == random_email

    def test_login_user(self, test_user_credentials):
        """Test POST /v1/auth/login"""
        response = client.post(
            "/v1/auth/login",
            json={
                "email": test_user_credentials["email"],
                "password": TEST_PASSWORD
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "api_keys" in data
        assert len(data["api_keys"]) > 0

    def test_get_current_user(self, test_user_credentials):
        """Test GET /v1/auth/me"""
        response = client.get(
            "/v1/auth/me",
            headers={"Authorization": f"Bearer {test_user_credentials['api_key']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "usage" in data

    def test_list_api_keys(self, test_user_credentials):
        """Test GET /v1/auth/api-keys"""
        response = client.get(
            "/v1/auth/api-keys",
            headers={"Authorization": f"Bearer {test_user_credentials['api_key']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "api_keys" in data
        assert "total" in data

    def test_create_api_key(self, test_user_credentials):
        """Test POST /v1/auth/api-keys"""
        response = client.post(
            "/v1/auth/api-keys",
            headers={"Authorization": f"Bearer {test_user_credentials['api_key']}"},
            json={"name": "Test Key", "expires_days": 30}
        )

        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        assert "key_info" in data


class TestScanRoutes:
    """Test scan endpoints"""

    @pytest.fixture(scope="class")
    def auth_headers(self, test_user_credentials):
        """Get auth headers for scan tests"""
        return {"Authorization": f"Bearer {test_user_credentials['api_key']}"}

    def test_scan_code(self, auth_headers):
        """Test POST /v1/scan/code"""
        response = client.post(
            "/v1/scan/code",
            headers=auth_headers,
            json={
                "code": TEST_CODE,
                "language": "python",
                "profile": "code-audit"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "scan_id" in data
        assert "findings" in data or "message" in data

    def test_list_scans(self, auth_headers):
        """Test GET /v1/scans"""
        response = client.get(
            "/v1/scans",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "scans" in data
        assert "total" in data

    def test_list_scans_with_limit(self, auth_headers):
        """Test GET /v1/scans with limit parameter"""
        response = client.get(
            "/v1/scans?limit=5",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "scans" in data
        assert len(data["scans"]) <= 5


class TestDashboardRoutes:
    """Test dashboard endpoints"""

    @pytest.fixture(scope="class")
    def auth_headers(self, test_user_credentials):
        """Get auth headers for dashboard tests"""
        return {"Authorization": f"Bearer {test_user_credentials['api_key']}"}

    def test_get_vulnerabilities(self, auth_headers):
        """Test GET /v1/dashboard/vulnerabilities"""
        response = client.get(
            "/v1/dashboard/vulnerabilities",
            headers=auth_headers
        )

        assert response.status_code in [200, 503]  # 503 if DB not configured

        if response.status_code == 200:
            data = response.json()
            assert "vulnerabilities" in data
            assert "total_count" in data
            assert "critical_count" in data

    def test_get_recent_scans(self, auth_headers):
        """Test GET /v1/dashboard/scans/recent"""
        response = client.get(
            "/v1/dashboard/scans/recent",
            headers=auth_headers
        )

        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()
            assert "scans" in data
            assert "total_count" in data

    def test_get_trends(self, auth_headers):
        """Test GET /v1/dashboard/analytics/trends"""
        response = client.get(
            "/v1/dashboard/analytics/trends",
            headers=auth_headers
        )

        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()
            assert "trends" in data
            assert "period_days" in data


class TestAlertRoutes:
    """Test alert endpoints"""

    @pytest.fixture(scope="class")
    def auth_headers(self, test_user_credentials):
        """Get auth headers for alert tests"""
        return {"Authorization": f"Bearer {test_user_credentials['api_key']}"}

    def test_get_alerts(self, auth_headers):
        """Test GET /v1/alerts"""
        response = client.get(
            "/v1/alerts",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_unread_count(self, auth_headers):
        """Test GET /v1/alerts/unread-count"""
        response = client.get(
            "/v1/alerts/unread-count",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert isinstance(data["count"], int)


class TestAgentRoutes:
    """Test agent endpoints"""

    def test_list_agents(self):
        """Test GET /v1/agents"""
        response = client.get("/v1/agents")

        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert len(data["agents"]) > 0

        # Check first agent has required fields
        first_agent = data["agents"][0]
        assert "id" in first_agent
        assert "name" in first_agent
        assert "description" in first_agent


class TestAuthenticationFailures:
    """Test authentication failure cases"""

    def test_unauthorized_access(self):
        """Test that endpoints require authentication"""
        response = client.get("/v1/auth/me")
        assert response.status_code == 401

    def test_invalid_api_key(self):
        """Test with invalid API key"""
        response = client.get(
            "/v1/auth/me",
            headers={"Authorization": "Bearer invalid_key_123"}
        )
        assert response.status_code == 401

    def test_missing_bearer_prefix(self):
        """Test with missing Bearer prefix"""
        response = client.get(
            "/v1/auth/me",
            headers={"Authorization": "some_key"}
        )
        assert response.status_code == 401


# Run these tests with pytest:
# pytest cli/tests/test_api_routes.py -v
# pytest cli/tests/test_api_routes.py::TestAuthenticationRoutes -v
# pytest cli/tests/test_api_routes.py -v --tb=short

import pytest
from bbctl.projects import create_project


@pytest.fixture
def project_data():
    """Provides standard test data for projects"""
    return {
        "workspace": "test-workspace",
        "project_key": "TESTPROJ",
        "name": "Test Project",
        "description": "This is a test project.",
        "url": "https://api.bitbucket.org/2.0",
        "token": "test-token",
    }


@pytest.fixture
def api_endpoint(project_data):
    """Returns the full API endpoint URL for project creation"""
    return f"{project_data['url']}/workspaces/{project_data['workspace']}/projects"


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for all tests"""
    monkeypatch.setenv("BITBUCKET_TOKEN", "test-token")


@pytest.fixture
def create_test_project(project_data):
    """Helper to create a project using test data"""

    def _create():
        return create_project(
            project_data["url"],
            project_data["workspace"],
            project_data["project_key"],
            project_data["name"],
            project_data["description"],
            project_data["token"],
        )

    return _create


def test_successful_project_creation(
    requests_mock, project_data, api_endpoint, create_test_project
):
    """When API returns 201, project should be created successfully"""
    # Setup
    requests_mock.post(
        api_endpoint,
        status_code=201,
        json={"key": project_data["project_key"], "name": project_data["name"]},
    )

    # Execute
    create_test_project()

    # Verify
    assert requests_mock.call_count == 1
    request = requests_mock.request_history[0]
    assert request.json() == {
        "key": project_data["project_key"],
        "name": project_data["name"],
        "description": project_data["description"],
    }


def test_handles_duplicate_project_key(
    requests_mock, api_endpoint, create_test_project
):
    """Should exit gracefully when project key already exists"""
    # Setup
    requests_mock.post(
        api_endpoint,
        status_code=400,
        json={
            "type": "error",
            "error": {
                "message": "Bad request",
                "fields": {
                    "__all__": ["Project with this Owner and Key already exists."]
                },
            },
        },
    )

    # Execute & Verify
    with pytest.raises(SystemExit):
        create_test_project()

    assert requests_mock.call_count == 1


def test_handles_unauthorized_error(requests_mock, api_endpoint, create_test_project):
    """Should exit gracefully when API returns 401 unauthorized"""
    # Setup
    requests_mock.post(
        api_endpoint,
        status_code=401,
        json={"type": "error", "error": {"message": "Token is invalid or expired"}},
    )

    # Execute & Verify
    with pytest.raises(SystemExit):
        create_test_project()

    assert requests_mock.call_count == 1

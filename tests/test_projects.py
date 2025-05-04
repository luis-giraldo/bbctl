import pytest
import os
from bbctl.projects import create_project


def mock_bitbucket_api(requests_mock, url, status_code, response_json):
    """
    Helper function to mock the Bitbucket API response.
    """
    requests_mock.post(url, status_code=status_code, json=response_json)


def get_test_data():
    """
    Helper function to provide common test data.
    """
    return {
        "workspace": "test-workspace",
        "project_key": "TESTPROJ",
        "name": "Test Project",
        "description": "This is a test project.",
        "url": "https://api.bitbucket.org/2.0",  # Base URL only
        "token": "test-token",
    }


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """
    Automatically mock environment variables for all tests.
    """
    monkeypatch.setenv("BITBUCKET_TOKEN", "test-token")


def test_create_project_success(requests_mock):
    """
    Test that a project is created successfully when the API returns a 201 status code.
    """
    data = get_test_data()
    full_url = f"{data['url']}/workspaces/{data['workspace']}/projects"

    # Mock a successful response
    mock_bitbucket_api(
        requests_mock,
        full_url,
        status_code=201,
        response_json={"key": data["project_key"], "name": data["name"]},
    )

    # Call the function
    create_project(
        data["url"],
        data["workspace"],
        data["project_key"],
        data["name"],
        data["description"],
        data["token"],
    )

    # Assert the mocked endpoint was called
    assert requests_mock.called
    assert requests_mock.call_count == 1

    # Verify the payload sent in the request
    request = requests_mock.request_history[0]
    assert request.json() == {
        "key": data["project_key"],
        "name": data["name"],
        "description": data["description"],
    }


def test_create_project_duplicate_key(requests_mock):
    """
    Test that the function handles a duplicate project key error gracefully.
    """
    data = get_test_data()
    full_url = f"{data['url']}/workspaces/{data['workspace']}/projects"

    # Mock a duplicate key error response
    mock_bitbucket_api(
        requests_mock,
        full_url,
        status_code=400,
        response_json={
            "type": "error",
            "error": {
                "message": "Bad request",
                "fields": {"__all__": ["Project with this Owner and Key already exists."]},
            },
        },
    )

    # Call the function and expect a SystemExit
    with pytest.raises(SystemExit):
        create_project(
            data["url"],
            data["workspace"],
            data["project_key"],
            data["name"],
            data["description"],
            data["token"],
        )

    # Assert the mocked endpoint was called
    assert requests_mock.called
    assert requests_mock.call_count == 1


def test_create_project_unauthorized(requests_mock):
    """
    Test that the function handles an unauthorized error (401) gracefully.
    """
    data = get_test_data()
    full_url = f"{data['url']}/workspaces/{data['workspace']}/projects"

    # Mock an unauthorized error response
    mock_bitbucket_api(
        requests_mock,
        full_url,
        status_code=401,
        response_json={
            "type": "error",
            "error": {"message": "Token is invalid, expired, or not supported for this endpoint."},
        },
    )

    # Call the function and expect a SystemExit
    with pytest.raises(SystemExit):
        create_project(
            data["url"],
            data["workspace"],
            data["project_key"],
            data["name"],
            data["description"],
            data["token"],
        )

    # Assert the mocked endpoint was called
    assert requests_mock.called
    assert requests_mock.call_count == 1

import pytest
from bbctl.repositories import create_repository


def test_create_repository_success(requests_mock):
    # Mock the Bitbucket API endpoint
    workspace = "test-workspace"
    repo_slug = "test-repo"
    project_key = "TEST"
    is_private = True
    token = "test-token"
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}"

    # Mock a successful response
    requests_mock.post(url, status_code=201, json={"name": repo_slug})

    # Call the function
    create_repository(workspace, repo_slug, project_key, is_private, token)

    # Assert the mocked endpoint was called
    assert requests_mock.called
    assert requests_mock.call_count == 1

    # Verify the payload sent in the request
    request = requests_mock.request_history[0]
    assert request.json() == {
        "scm": "git",
        "is_private": is_private,
        "project": {"key": project_key},
    }


def test_create_repository_failure(requests_mock):
    # Mock the Bitbucket API endpoint
    workspace = "test-workspace"
    repo_slug = "test-repo"
    project_key = "TEST"
    is_private = True
    token = "test-token"
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}"

    # Mock a failure response
    requests_mock.post(url, status_code=400, json={"error": {"message": "Bad Request"}})

    # Call the function and capture logs
    with pytest.raises(SystemExit):  # Assuming the script exits on failure
        create_repository(workspace, repo_slug, project_key, is_private, token)

    # Assert the mocked endpoint was called
    assert requests_mock.called
    assert requests_mock.call_count == 1

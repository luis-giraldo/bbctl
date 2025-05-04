import pytest
import requests
from requests.auth import HTTPBasicAuth
from click.testing import CliRunner
from bbctl.branches import exempt_user_from_pull_request, cli


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to mock environment variables."""
    monkeypatch.setenv("BITBUCKET_API_URL", "https://api.bitbucket.org/2.0")
    monkeypatch.setenv("BITBUCKET_WORKSPACE", "test-workspace")
    monkeypatch.setenv("BITBUCKET_USERNAME", "test-username")
    monkeypatch.setenv("BITBUCKET_APP_PASSWORD", "test-password")


def test_exempt_user_success(requests_mock, mock_env_vars):
    """Test successful exemption of a user from pull request requirements."""
    workspace = "test-workspace"
    repo_slug = "test-repo"
    username = "test-user"
    api_url = "https://api.bitbucket.org/2.0"
    auth = HTTPBasicAuth("test-username", "test-password")
    url = f"{api_url}/repositories/{workspace}/{repo_slug}/branch-restrictions"

    # Mock a successful response
    requests_mock.post(url, status_code=201, json={"message": "Success"})

    # Call the function
    exempt_user_from_pull_request(workspace, repo_slug, username, api_url, auth)

    # Assert the mocked endpoint was called
    assert requests_mock.called
    assert requests_mock.call_count == 1

    # Verify the payload sent in the request
    request = requests_mock.request_history[0]
    assert request.json() == {
        "kind": "push",
        "branch_match_kind": "glob",
        "pattern": "master",
        "users": [{"type": "user", "username": username}],
    }


def test_exempt_user_failure(requests_mock, mock_env_vars):
    """Test failure when exempting a user from pull request requirements."""
    workspace = "test-workspace"
    repo_slug = "test-repo"
    username = "test-user"
    api_url = "https://api.bitbucket.org/2.0"
    auth = HTTPBasicAuth("test-username", "test-password")
    url = f"{api_url}/repositories/{workspace}/{repo_slug}/branch-restrictions"

    # Mock a failure response
    requests_mock.post(url, status_code=400, json={"error": {"message": "Bad Request"}})

    # Call the function and expect a SystemExit
    with pytest.raises(SystemExit):
        exempt_user_from_pull_request(workspace, repo_slug, username, api_url, auth)

    # Assert the mocked endpoint was called
    assert requests_mock.called
    assert requests_mock.call_count == 1


def test_cli_exempt_command_success(requests_mock, mock_env_vars):
    """Test the CLI exempt command for successful execution."""
    runner = CliRunner()
    workspace = "test-workspace"
    repo_slug = "test-repo"
    username = "test-user"
    api_url = "https://api.bitbucket.org/2.0"
    url = f"{api_url}/repositories/{workspace}/{repo_slug}/branch-restrictions"

    # Mock a successful response
    requests_mock.post(url, status_code=201, json={"message": "Success"})

    # Initialize the context obj with required values
    obj = {
        "workspace": workspace,
        "api_url": api_url,
        "auth": HTTPBasicAuth("test-username", "test-password")
    }

    # Run the CLI command with the context
    result = runner.invoke(
        cli,
        [
            "exempt",
            "--repo-slug",
            repo_slug,
            "--username",
            username,
        ],
        obj=obj  # Pass the context object
    )

    # Assert the CLI command ran successfully
    assert result.exit_code == 0
    assert "✅ User 'test-user' successfully exempted." in result.output
    assert requests_mock.called
    assert requests_mock.call_count == 1


def test_cli_exempt_command_failure(requests_mock, mock_env_vars):
    """Test the CLI exempt command for failure."""
    runner = CliRunner()
    workspace = "test-workspace"
    repo_slug = "test-repo"
    username = "test-user"
    api_url = "https://api.bitbucket.org/2.0"
    url = f"{api_url}/repositories/{workspace}/{repo_slug}/branch-restrictions"

    # Mock a failure response
    requests_mock.post(url, status_code=400, json={"error": {"message": "Bad Request"}})

    # Initialize the context obj with required values
    obj = {
        "workspace": workspace,
        "api_url": api_url,
        "auth": HTTPBasicAuth("test-username", "test-password")
    }

    # Run the CLI command with the context
    result = runner.invoke(
        cli,
        [
            "exempt",
            "--repo-slug",
            repo_slug,
            "--username",
            username,
        ],
        obj=obj
    )

    # Assert the CLI command failed
    assert result.exit_code != 0
    assert "❌ Failed to exempt user" in result.output
    assert "400 Client Error" in result.output  # Changed from "Bad Request"
    assert requests_mock.called
    assert requests_mock.call_count == 1
import pytest
from unittest.mock import patch, MagicMock
import requests
from bbctl.users import add_user_to_repo, remove_user_from_repo


@patch("bbctl.users.requests.put")
def test_add_user_to_repo_invalid_permission(mock_put):
    """
    Test the add_user_to_repo function with an invalid permission.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_put.return_value = mock_response

    mock_auth = MagicMock()
    workspace = "test-workspace"
    repo_slug = "test-repo"
    username = "test-user"
    permission = "invalid-permission"
    api_url = "https://api.bitbucket.org/2.0"

    # Act & Assert
    with pytest.raises(SystemExit):
        add_user_to_repo(repo_slug, username, permission, workspace, api_url, mock_auth)


@patch("bbctl.users.requests.delete")
def test_remove_user_from_repo_user_not_found(mock_delete):
    """
    Test the remove_user_from_repo function when the user is not found.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_delete.return_value = mock_response

    mock_auth = MagicMock()
    workspace = "test-workspace"
    repo_slug = "test-repo"
    username = "nonexistent-user"
    api_url = "https://api.bitbucket.org/2.0"

    # Act & Assert
    with pytest.raises(SystemExit):
        remove_user_from_repo(repo_slug, username, workspace, api_url, mock_auth)


@patch("bbctl.users.requests.put")
def test_add_user_to_repo_api_error(mock_put):
    """
    Test the add_user_to_repo function when the API returns an error.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_put.return_value = mock_response

    mock_auth = MagicMock()
    workspace = "test-workspace"
    repo_slug = "test-repo"
    username = "test-user"
    permission = "read"
    api_url = "https://api.bitbucket.org/2.0"

    # Act & Assert
    with pytest.raises(SystemExit):
        add_user_to_repo(repo_slug, username, permission, workspace, api_url, mock_auth)


@patch("bbctl.users.requests.delete")
def test_remove_user_from_repo_api_error(mock_delete):
    """
    Test the remove_user_from_repo function when the API returns an error.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_delete.return_value = mock_response

    mock_auth = MagicMock()
    workspace = "test-workspace"
    repo_slug = "test-repo"
    username = "test-user"
    api_url = "https://api.bitbucket.org/2.0"

    # Act & Assert
    with pytest.raises(SystemExit):
        remove_user_from_repo(repo_slug, username, workspace, api_url, mock_auth)

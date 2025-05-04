import pytest
from unittest.mock import patch, MagicMock
from bbctl.users import add_user_to_repo, remove_user_from_repo


@patch("bbctl.users.get_workspace")
@patch("bbctl.users.get_auth")
@patch("bbctl.users.requests.put")
def test_add_user_to_repo(mock_put, mock_get_auth, mock_get_workspace):
    """
    Test the add_user_to_repo function.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_put.return_value = mock_response

    mock_auth = MagicMock()
    mock_get_auth.return_value = mock_auth

    workspace = "test-workspace"
    repo_slug = "test-repo"
    username = "test-user"
    permission = "read"

    mock_get_workspace.return_value = workspace

    # Act
    add_user_to_repo(repo_slug, username, permission)

    # Assert
    mock_put.assert_called_once_with(
        f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/permissions-config/users/{username}",
        auth=mock_auth,
        json={"permission": permission},
    )


@patch("bbctl.users.get_workspace")
@patch("bbctl.users.get_auth")
@patch("bbctl.users.requests.delete")
def test_remove_user_from_repo(mock_delete, mock_get_auth, mock_get_workspace):
    """
    Test the remove_user_from_repo function.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 204
    mock_delete.return_value = mock_response

    mock_auth = MagicMock()
    mock_get_auth.return_value = mock_auth

    workspace = "test-workspace"
    repo_slug = "test-repo"
    username = "test-user"

    mock_get_workspace.return_value = workspace

    # Act
    remove_user_from_repo(repo_slug, username)

    # Assert
    mock_delete.assert_called_once_with(
        f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/permissions-config/users/{username}",
        auth=mock_auth,
    )
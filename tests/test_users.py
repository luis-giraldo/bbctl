import pytest
from unittest.mock import patch, MagicMock
import requests
from bbctl.users import add_user_to_repo, remove_user_from_repo, check_user_repo_permission


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


@patch("bbctl.users.check_user_repo_permission")
@patch("bbctl.users.requests.put")
def test_add_user_to_repo_success(mock_put, mock_check_permission):
    """
    Test successful addition of a user to a repository.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_put.return_value = mock_response
    
    # Mock that user has no existing permissions
    mock_check_permission.return_value = {}

    mock_auth = MagicMock()
    workspace = "test-workspace"
    repo_slug = "test-repo"
    username = "test-user"
    permission = "read"
    api_url = "https://api.bitbucket.org/2.0"

    # Act
    add_user_to_repo(repo_slug, username, permission, workspace, api_url, mock_auth)

    # Assert
    mock_check_permission.assert_called_once_with(repo_slug, username, workspace, api_url, mock_auth)
    mock_put.assert_called_once()
    url = f"{api_url}/repositories/{workspace}/{repo_slug}/permissions-config/users/{username}"
    mock_put.assert_called_with(url, auth=mock_auth, json={"permission": permission})


@patch("bbctl.users.check_user_repo_permission")
@patch("bbctl.users.click.echo")
def test_add_user_to_repo_already_has_same_permission(mock_echo, mock_check_permission):
    """
    Test adding a user who already has the same permission level.
    """
    # Arrange
    # Mock that user already has the same permission
    mock_check_permission.return_value = {"permission": "read"}

    mock_auth = MagicMock()
    workspace = "test-workspace"
    repo_slug = "test-repo"
    username = "test-user"
    permission = "read"
    api_url = "https://api.bitbucket.org/2.0"

    # Act
    add_user_to_repo(repo_slug, username, permission, workspace, api_url, mock_auth)

    # Assert
    mock_check_permission.assert_called_once_with(repo_slug, username, workspace, api_url, mock_auth)
    # Update the assertion to match the actual message format
    mock_echo.assert_called_once_with(f"ℹ️ User '{username}' already has '{permission}' permission on repository '{repo_slug}'. No changes made.")


@patch("bbctl.users.check_user_repo_permission")
@patch("bbctl.users.requests.put")
def test_add_user_to_repo_update_permission(mock_put, mock_check_permission):
    """
    Test updating a user's permission level.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_put.return_value = mock_response
    
    # Mock that user has a different permission
    mock_check_permission.return_value = {"permission": "read"}

    mock_auth = MagicMock()
    workspace = "test-workspace"
    repo_slug = "test-repo"
    username = "test-user"
    permission = "write"  # Different from current "read"
    api_url = "https://api.bitbucket.org/2.0"

    # Act
    add_user_to_repo(repo_slug, username, permission, workspace, api_url, mock_auth)

    # Assert
    mock_check_permission.assert_called_once_with(repo_slug, username, workspace, api_url, mock_auth)
    mock_put.assert_called_once()
    url = f"{api_url}/repositories/{workspace}/{repo_slug}/permissions-config/users/{username}"
    mock_put.assert_called_with(url, auth=mock_auth, json={"permission": permission})


@patch("bbctl.users.check_user_repo_permission")
@patch("bbctl.users.requests.put")
def test_add_user_to_repo_invalid_permission(mock_put, mock_check_permission):
    """
    Test adding a user with an invalid permission.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_put.return_value = mock_response
    
    # Mock that user has no existing permissions
    mock_check_permission.return_value = {}

    mock_auth = MagicMock()
    workspace = "test-workspace"
    repo_slug = "test-repo"
    username = "test-user"
    permission = "invalid-permission"
    api_url = "https://api.bitbucket.org/2.0"

    # Act & Assert
    with pytest.raises(SystemExit):
        add_user_to_repo(repo_slug, username, permission, workspace, api_url, mock_auth)


@patch("bbctl.users.check_user_repo_permission")
@patch("bbctl.users.requests.delete")
def test_remove_user_from_repo_success(mock_delete, mock_check_permission):
    """
    Test successful removal of a user from a repository.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 204
    mock_delete.return_value = mock_response
    
    # Mock that user has permissions
    mock_check_permission.return_value = {"permission": "read"}

    mock_auth = MagicMock()
    workspace = "test-workspace"
    repo_slug = "test-repo"
    username = "test-user"
    api_url = "https://api.bitbucket.org/2.0"

    # Act
    remove_user_from_repo(repo_slug, username, workspace, api_url, mock_auth)

    # Assert
    mock_check_permission.assert_called_once_with(repo_slug, username, workspace, api_url, mock_auth)
    mock_delete.assert_called_once()
    url = f"{api_url}/repositories/{workspace}/{repo_slug}/permissions-config/users/{username}"
    mock_delete.assert_called_with(url, auth=mock_auth)


@patch("bbctl.users.check_user_repo_permission")
@patch("bbctl.users.click.echo")
def test_remove_user_no_permissions(mock_echo, mock_check_permission):
    """
    Test removing a user who has no permissions.
    """
    # Arrange
    # Mock that user has no permissions
    mock_check_permission.return_value = {}

    mock_auth = MagicMock()
    workspace = "test-workspace"
    repo_slug = "test-repo"
    username = "nonexistent-user"
    api_url = "https://api.bitbucket.org/2.0"

    # Act
    remove_user_from_repo(repo_slug, username, workspace, api_url, mock_auth)

    # Assert
    mock_check_permission.assert_called_once_with(repo_slug, username, workspace, api_url, mock_auth)
    # Ensure the message about no permissions is displayed
    mock_echo.assert_called_once_with(f"ℹ️ User '{username}' has no permissions on repository '{repo_slug}'. Nothing to remove.")


@patch("bbctl.users.check_user_repo_permission")
@patch("bbctl.users.requests.delete")
def test_remove_user_from_repo_api_error(mock_delete, mock_check_permission):
    """
    Test removal when the API returns an error.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_delete.return_value = mock_response
    
    # Mock that user has permissions
    mock_check_permission.return_value = {"permission": "read"}

    mock_auth = MagicMock()
    workspace = "test-workspace"
    repo_slug = "test-repo"
    username = "test-user"
    api_url = "https://api.bitbucket.org/2.0"

    # Act & Assert
    with pytest.raises(SystemExit):
        remove_user_from_repo(repo_slug, username, workspace, api_url, mock_auth)


@patch("bbctl.users.requests.get")
def test_check_user_repo_permission_has_permission(mock_get):
    """
    Test checking when a user has permissions.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"permission": "read"}
    mock_get.return_value = mock_response

    mock_auth = MagicMock()
    workspace = "test-workspace"
    repo_slug = "test-repo"
    username = "test-user"
    api_url = "https://api.bitbucket.org/2.0"

    # Act
    result = check_user_repo_permission(repo_slug, username, workspace, api_url, mock_auth)

    # Assert
    assert result == {"permission": "read"}
    url = f"{api_url}/repositories/{workspace}/{repo_slug}/permissions-config/users/{username}"
    mock_get.assert_called_once_with(url, auth=mock_auth)


@patch("bbctl.users.requests.get")
def test_check_user_repo_permission_no_permission(mock_get):
    """
    Test checking when a user has no permissions.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    mock_auth = MagicMock()
    workspace = "test-workspace"
    repo_slug = "test-repo"
    username = "test-user"
    api_url = "https://api.bitbucket.org/2.0"

    # Act
    result = check_user_repo_permission(repo_slug, username, workspace, api_url, mock_auth)

    # Assert
    assert result == {}
    url = f"{api_url}/repositories/{workspace}/{repo_slug}/permissions-config/users/{username}"
    mock_get.assert_called_once_with(url, auth=mock_auth)

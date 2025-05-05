import os
import requests
from requests.auth import HTTPBasicAuth
import logging
from dotenv import load_dotenv
import click

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def check_user_repo_permission(
    repo_slug: str, username: str, workspace: str, api_url: str, auth: HTTPBasicAuth
) -> dict:
    """
    Check if a user already has permissions on a repository.

    Args:
        repo_slug (str): Repository slug
        username (str): Bitbucket username or email of the user to check
        workspace (str): The Bitbucket workspace ID
        api_url (str): The Bitbucket API base URL
        auth (HTTPBasicAuth): Authentication object

    Returns:
        dict: Permission details if user has access, empty dict if no access
    """
    url = f"{api_url}/repositories/{workspace}/{repo_slug}/permissions-config/users/{username}"

    logging.debug(
        f"Checking if user '{username}' has permissions on repository '{repo_slug}'..."
    )

    try:
        response = requests.get(url, auth=auth)

        if response.status_code == 200:
            permission_data = response.json()
            logging.debug(
                f"User '{username}' has '{permission_data.get('permission')}' permission on repository '{repo_slug}'"
            )
            return permission_data
        elif response.status_code == 404:
            logging.debug(
                f"User '{username}' has no permissions on repository '{repo_slug}'"
            )
            return {}
        else:
            logging.warning(
                f"Unexpected response when checking user permissions: {response.status_code}"
            )
            return {}
    except requests.exceptions.RequestException as e:
        logging.warning(f"Error checking user permissions: {e}")
        return {}


def add_user_to_repo(
    repo_slug: str,
    username: str,
    permission: str,
    workspace: str,
    api_url: str,
    auth: HTTPBasicAuth,
) -> None:
    """
    Grant a user access to a Bitbucket repository.

    Args:
        repo_slug (str): Repository slug
        username (str): Bitbucket username or email of the user to add
        permission (str): Permission level ('read', 'write', 'admin')
        workspace (str): The Bitbucket workspace ID
        api_url (str): The Bitbucket API base URL
        auth (HTTPBasicAuth): Authentication object
    """
    # Check if the user already has permissions
    existing_permission = check_user_repo_permission(
        repo_slug, username, workspace, api_url, auth
    )

    if existing_permission:
        current_permission = existing_permission.get("permission")
        if current_permission == permission:
            message = f"ℹ️ User '{username}' already has '{permission}' permission on repository '{repo_slug}'. No changes made."
            logging.info(message)
            click.echo(message)
            return
        else:
            # User has different permission level, will update
            logging.info(
                f"User '{username}' has '{current_permission}' permission, updating to '{permission}'..."
            )

    url = f"{api_url}/repositories/{workspace}/{repo_slug}/permissions-config/users/{username}"
    data = {"permission": permission}

    logging.info(
        f"Adding user '{username}' to repository '{repo_slug}' with '{permission}' permission..."
    )
    try:
        response = requests.put(url, auth=auth, json=data)
        response.raise_for_status()
        message = (
            f"✅ User '{username}' successfully added with '{permission}' permission."
        )
        logging.info(message)
        click.echo(message)
    except requests.exceptions.RequestException as e:
        error_message = f"❌ An error occurred while adding the user: {e}"
        logging.error(error_message)
        if e.response is not None:
            logging.error(f"Response: {e.response.text}")
        click.echo(error_message, err=True)
        raise SystemExit(1)


def remove_user_from_repo(
    repo_slug: str, username: str, workspace: str, api_url: str, auth: HTTPBasicAuth
) -> None:
    """
    Remove a user's access from a Bitbucket repository.

    Args:
        repo_slug (str): Repository slug
        username (str): Bitbucket username or email of the user to remove
        workspace (str): The Bitbucket workspace ID
        api_url (str): The Bitbucket API base URL
        auth (HTTPBasicAuth): Authentication object
    """
    # Check if the user has permissions to remove
    existing_permission = check_user_repo_permission(
        repo_slug, username, workspace, api_url, auth
    )

    if not existing_permission:
        message = f"ℹ️ User '{username}' has no permissions on repository '{repo_slug}'. Nothing to remove."
        logging.info(message)
        click.echo(message)
        return

    url = f"{api_url}/repositories/{workspace}/{repo_slug}/permissions-config/users/{username}"

    logging.info(f"Removing user '{username}' from repository '{repo_slug}'...")
    try:
        response = requests.delete(url, auth=auth)
        response.raise_for_status()
        message = f"✅ User '{username}' successfully removed from the repository."
        logging.info(message)
        click.echo(message)
    except requests.exceptions.RequestException as e:
        error_message = f"❌ An error occurred while removing the user: {e}"
        logging.error(error_message)
        if e.response is not None:
            logging.error(f"Response: {e.response.text}")
        click.echo(error_message, err=True)
        raise SystemExit(1)


@click.group()
def cli():
    """
    CLI tool for managing user permissions for Bitbucket repositories and groups.
    """
    pass


@cli.command(name="add-user")
@click.option("--repo-slug", required=True, help="The repository slug.")
@click.option(
    "--username", required=True, help="The Bitbucket username or email to add."
)
@click.option(
    "--permission",
    required=True,
    default="read",
    type=click.Choice(["read", "write", "admin"]),
    help="The permission level to grant.",
)
@click.pass_context
def add(ctx, repo_slug: str, username: str, permission: str) -> None:
    """
    Grant a user access to a Bitbucket repository.
    """
    add_user_to_repo(
        repo_slug,
        username,
        permission,
        ctx.obj["workspace"],
        ctx.obj["api_url"],
        ctx.obj["auth"],
    )


@cli.command(name="remove-user")
@click.option("--repo-slug", required=True, help="The repository slug.")
@click.option(
    "--username", required=True, help="The Bitbucket username or email to remove."
)
@click.pass_context
def remove(ctx, repo_slug: str, username: str) -> None:
    """
    Remove a user's access from a Bitbucket repository.
    """
    remove_user_from_repo(
        repo_slug, username, ctx.obj["workspace"], ctx.obj["api_url"], ctx.obj["auth"]
    )


def main():
    """
    Main entry point for the CLI.
    """
    # Validate required environment variables
    required_env_vars = [
        "BITBUCKET_API_URL",
        "BITBUCKET_WORKSPACE",
        "BITBUCKET_USERNAME",
        "BITBUCKET_APP_PASSWORD",
    ]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logging.error(
            f"❌ Missing required environment variables: {', '.join(missing_vars)}"
        )
        raise SystemExit(1)

    # Prepare shared context
    ctx = {
        "api_url": os.getenv("BITBUCKET_API_URL"),
        "workspace": os.getenv("BITBUCKET_WORKSPACE"),
        "auth": HTTPBasicAuth(
            os.getenv("BITBUCKET_USERNAME"), os.getenv("BITBUCKET_APP_PASSWORD")
        ),
    }

    # Run the CLI with the shared context
    cli(obj=ctx)


if __name__ == "__main__":
    main()

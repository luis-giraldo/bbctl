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


def get_auth() -> HTTPBasicAuth:
    """
    Retrieve authentication credentials from environment variables.

    Returns:
        HTTPBasicAuth: Authentication object for requests.
    """
    bitbucket_user = os.getenv("BITBUCKET_USERNAME")
    bitbucket_app_password = os.getenv("BITBUCKET_APP_PASSWORD")

    if not bitbucket_user or not bitbucket_app_password:
        logging.error(
            "❌ Missing BITBUCKET_USERNAME or BITBUCKET_APP_PASSWORD environment variables."
        )
        raise SystemExit(1)

    return HTTPBasicAuth(bitbucket_user, bitbucket_app_password)


def get_workspace() -> str:
    """
    Retrieve the workspace ID from the environment variables.

    Returns:
        str: The workspace ID.
    """
    workspace = os.getenv("BITBUCKET_WORKSPACE")
    if not workspace:
        logging.error("❌ Missing BITBUCKET_WORKSPACE environment variable.")
        raise SystemExit(1)
    return workspace


def get_api_url() -> str:
    """
    Retrieve the Bitbucket API base URL from the environment variables.

    Returns:
        str: The API base URL.
    """
    url = os.getenv("BITBUCKET_API_URL", "https://api.bitbucket.org/2.0")
    return url


def add_user_to_repo(repo_slug: str, username: str, permission: str) -> None:
    """
    Grant a user access to a Bitbucket repository.

    Args:
        repo_slug (str): Repository slug
        username (str): Bitbucket username or email of the user to add
        permission (str): Permission level ('read', 'write', 'admin')
    """
    workspace = get_workspace()
    url = f"{get_api_url()}/repositories/{workspace}/{repo_slug}/permissions-config/users/{username}"
    data = {"permission": permission}

    logging.info(
        f"Adding user '{username}' to repository '{repo_slug}' with '{permission}' permission..."
    )
    try:
        response = requests.put(url, auth=get_auth(), json=data)
        response.raise_for_status()
        logging.info(
            f"✅ User '{username}' successfully added with '{permission}' permission."
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ An error occurred while adding the user: {e}")
        if e.response is not None:
            logging.error(f"Response: {e.response.text}")
        raise SystemExit(1)


def remove_user_from_repo(repo_slug: str, username: str) -> None:
    """
    Remove a user's access from a Bitbucket repository.

    Args:
        repo_slug (str): Repository slug
        username (str): Bitbucket username or email of the user to remove
    """
    workspace = get_workspace()
    url = f"{get_api_url()}/repositories/{workspace}/{repo_slug}/permissions-config/users/{username}"

    logging.info(f"Removing user '{username}' from repository '{repo_slug}'...")
    try:
        response = requests.delete(url, auth=get_auth())
        response.raise_for_status()
        logging.info(f"✅ User '{username}' successfully removed from the repository.")
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ An error occurred while removing the user: {e}")
        if e.response is not None:
            logging.error(f"Response: {e.response.text}")
        raise SystemExit(1)


def add_user_to_group(group_slug: str, username_to_add: str) -> None:
    """
    Add a user to a Bitbucket group.

    Args:
        group_slug (str): Group slug (e.g., "developers")
        username_to_add (str): Bitbucket username or email of the user to add
    """
    workspace = get_workspace()
    url = f"{get_api_url()}/workspaces/{workspace}/groups/{group_slug}/members/{username_to_add}"

    logging.info(
        f"Adding user '{username_to_add}' to group '{group_slug}' in workspace '{workspace}'..."
    )
    try:
        response = requests.put(url, auth=get_auth())
        response.raise_for_status()
        logging.info(
            f"✅ User '{username_to_add}' successfully added to group '{group_slug}'."
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ An error occurred while adding the user to the group: {e}")
        if e.response is not None:
            logging.error(f"Response: {e.response.text}")
        raise SystemExit(1)


def remove_user_from_group(group_slug: str, username_to_remove: str) -> None:
    """
    Remove a user from a Bitbucket group.

    Args:
        group_slug (str): Group slug (e.g., "developers")
        username_to_remove (str): Bitbucket username or email of the user to remove
    """
    workspace = get_workspace()
    url = f"{get_api_url()}/workspaces/{workspace}/groups/{group_slug}/members/{username_to_remove}"

    logging.info(
        f"Removing user '{username_to_remove}' from group '{group_slug}' in workspace '{workspace}'..."
    )
    try:
        response = requests.delete(url, auth=get_auth())
        response.raise_for_status()
        logging.info(
            f"✅ User '{username_to_remove}' successfully removed from group '{group_slug}'."
        )
    except requests.exceptions.RequestException as e:
        logging.error(
            f"❌ An error occurred while removing the user from the group: {e}"
        )
        if e.response is not None:
            logging.error(f"Response: {e.response.text}")
        raise SystemExit(1)


@click.group()
def cli():
    """
    CLI tool for managing user permissions for Bitbucket repositories and groups.
    """
    pass


@cli.command()
@click.option("--repo-slug", required=True, help="The repository slug.")
@click.option(
    "--username", required=True, help="The Bitbucket username or email to add."
)
@click.option(
    "--permission",
    required=True,
    type=click.Choice(["read", "write", "admin"]),
    help="The permission level to grant.",
)
def add(repo_slug: str, username: str, permission: str) -> None:
    """
    Grant a user access to a Bitbucket repository.
    """
    add_user_to_repo(repo_slug, username, permission)


@cli.command()
@click.option("--repo-slug", required=True, help="The repository slug.")
@click.option(
    "--username", required=True, help="The Bitbucket username or email to remove."
)
def remove(repo_slug: str, username: str) -> None:
    """
    Remove a user's access from a Bitbucket repository.
    """
    remove_user_from_repo(repo_slug, username)


@cli.command()
@click.option(
    "--group-slug", required=True, help="The group slug (e.g., 'developers')."
)
@click.option(
    "--username", required=True, help="The Bitbucket username or email to add."
)
def add_to_group(group_slug: str, username: str) -> None:
    """
    Add a user to a Bitbucket group.
    """
    add_user_to_group(group_slug, username)


@cli.command()
@click.option(
    "--group-slug", required=True, help="The group slug (e.g., 'developers')."
)
@click.option(
    "--username", required=True, help="The Bitbucket username or email to remove."
)
def remove_from_group(group_slug: str, username: str) -> None:
    """
    Remove a user from a Bitbucket group.
    """
    remove_user_from_group(group_slug, username)


if __name__ == "__main__":
    cli()

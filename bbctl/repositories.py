import os
import requests
import logging
from dotenv import load_dotenv
import click

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


def create_repository(
    workspace: str, repo_slug: str, project_key: str, is_private: bool, token: str, base_url: str
) -> None:
    """
    Create a new repository in a Bitbucket workspace.

    Args:
        workspace (str): The Bitbucket workspace ID.
        repo_slug (str): The repository slug (lowercase, no spaces).
        project_key (str): The project key where the repository will be created.
        is_private (bool): Whether the repository is private.
        token (str): The Bitbucket API token.
        base_url (str): The base URL for the Bitbucket API.

    Returns:
        None
    """
    url = f"{base_url}/repositories/{workspace}/{repo_slug}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "scm": "git",
        "is_private": is_private,
        "project": {"key": project_key},
    }

    message = f"Creating repository '{repo_slug}' in workspace '{workspace}' under project '{project_key}'..."
    logging.info(message)
    click.echo(message)
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        error_message = f"❌ An error occurred while creating the repository: {e}"
        logging.error(error_message)
        click.echo(error_message, err=True)
        raise SystemExit(1)

    if response.status_code in (200, 201):
        success_message = f"✅ Repository '{repo_slug}' created successfully!"
        logging.info(success_message)
        click.echo(success_message)
    else:
        error_message = f"❌ Failed to create repository: {response.status_code}"
        logging.error(error_message)
        logging.error(response.json().get("error", {}).get("message", "Unknown error"))
        click.echo(error_message, err=True)
        raise SystemExit(1)


def repository_exists(workspace: str, repo_slug: str, token: str, base_url: str) -> bool:
    """
    Check if a repository with the given slug already exists in the workspace.

    Args:
        workspace (str): The Bitbucket workspace ID.
        repo_slug (str): The repository slug.
        token (str): The Bitbucket API token.
        base_url (str): The base URL for the Bitbucket API.

    Returns:
        bool: True if the repository exists, False otherwise.
    """
    url = f"{base_url}/repositories/{workspace}/{repo_slug}"
    headers = {"Authorization": f"Bearer {token}"}

    logging.debug(f"Checking if repository '{repo_slug}' exists in workspace '{workspace}'...")

    try:
        response = requests.get(url, headers=headers)
        # If we get a 200 response, the repository exists
        if response.status_code == 200:
            logging.info(f"Repository '{repo_slug}' already exists in workspace '{workspace}'")
            return True
        # If we get a 404 response, the repository does not exist
        elif response.status_code == 404:
            logging.debug(f"Repository '{repo_slug}' does not exist in workspace '{workspace}'")
            return False
        # Handle permission issues
        elif response.status_code == 403:
            logging.warning(f"Permission denied when checking if repository exists: {response.status_code}")
            # We can't determine if it exists due to permissions
            return False
        # Handle other status codes
        else:
            logging.warning(f"Unexpected response when checking repository existence: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logging.warning(f"Error checking if repository exists: {e}")
        return False


@click.group()
def cli():
    """
    CLI tool for managing Bitbucket repositories.
    """
    pass


@cli.command(name="create-repo")
@click.option("--repo-slug", required=True, help="The repository slug (lowercase, no spaces).")
@click.option("--project-key", required=True, help="The project key where the repository will be created.")
@click.option(
    "--is-private",
    is_flag=True,
    default=True,
    help="Whether the repository is private (default: true).",
)
def create(repo_slug: str, project_key: str, is_private: bool) -> None:
    """
    Create a new repository in a Bitbucket workspace.
    """
    # Read workspace and token from environment variables
    workspace = os.getenv("BITBUCKET_WORKSPACE")
    token = os.getenv("BITBUCKET_TOKEN")

    if not workspace or not token:
        logging.error("❌ Missing required environment variables: BITBUCKET_WORKSPACE or BITBUCKET_TOKEN")
        raise SystemExit(1)

    base_url = os.getenv("BITBUCKET_API_URL", "https://api.bitbucket.org/2.0")
    
    # Check if repository already exists
    if repository_exists(workspace, repo_slug, token, base_url):
        message = f"❌ Repository '{repo_slug}' already exists in workspace '{workspace}'"
        logging.error(message)
        click.echo(message, err=True)
        raise SystemExit(1)
    
    # If we get here, the repository doesn't exist, so create it
    create_repository(workspace, repo_slug, project_key, is_private, token, base_url)


def main():
    """
    Main entry point for the CLI.
    """
    # Validate required environment variables
    required_env_vars = ["BITBUCKET_API_URL"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logging.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        raise SystemExit(1)

    # Run the CLI
    cli()


if __name__ == "__main__":
    main()

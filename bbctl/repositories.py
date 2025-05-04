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

    logging.info(
        f"Creating repository '{repo_slug}' in workspace '{workspace}' under project '{project_key}'..."
    )
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ An error occurred while creating the repository: {e}")
        raise SystemExit(1)

    if response.status_code in (200, 201):
        logging.info(f"✅ Repository '{repo_slug}' created successfully!")
    else:
        logging.error(f"❌ Failed to create repository: {response.status_code}")
        logging.error(response.json().get("error", {}).get("message", "Unknown error"))
        raise SystemExit(1)  # Exit with a non-zero status code


@click.group()
def cli():
    """
    CLI tool for managing Bitbucket repositories.
    """
    pass


@cli.command()
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

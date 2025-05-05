import os
import logging
import click
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def create_project(
    url: str, workspace: str, project_key: str, name: str, description: str, token: str
) -> None:
    """
    Create a new project in a Bitbucket workspace.

    Args:
        url (str): The base URL for the Bitbucket API.
        workspace (str): The Bitbucket workspace ID.
        project_key (str): The unique key for the project.
        name (str): The name of the project.
        description (str): A description for the project.
        token (str): The Bitbucket API token.

    Returns:
        None
    """
    # Remove the redundant check here since it's already handled in the command function

    full_url = f"{url}/workspaces/{workspace}/projects"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "key": project_key,
        "name": name,
        "description": description,
    }

    logging.info(
        f"Creating project '{name}' in workspace '{workspace}' with key '{project_key}'..."
    )
    logging.debug(f"Payload: {payload}")

    try:
        response = requests.post(full_url, headers=headers, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        if e.response is not None:
            logging.error(f"Response: {e.response.text}")
        logging.error(f"❌ An error occurred while creating the project: {e}")
        raise SystemExit(1)

    if response.status_code in (200, 201):
        logging.info(f"✅ Project '{name}' created successfully!")
        click.echo(f"✅ Project '{name}' created successfully!")
    else:
        error_message = f"❌ Failed to create project: {response.status_code}"
        logging.error(error_message)
        logging.error(response.json().get("error", {}).get("message", "Unknown error"))
        click.echo(error_message, err=True)
        raise SystemExit(1)


def project_exists(url: str, workspace: str, project_key: str, token: str) -> bool:
    """
    Check if a project with the given key already exists in the workspace.

    Args:
        url (str): The base URL for the Bitbucket API.
        workspace (str): The Bitbucket workspace ID.
        project_key (str): The unique key for the project.
        token (str): The Bitbucket API token.

    Returns:
        bool: True if the project exists, False otherwise.
    """
    check_url = f"{url}/workspaces/{workspace}/projects/{project_key}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    logging.debug(
        f"Checking if project '{project_key}' exists in workspace '{workspace}'..."
    )

    try:
        response = requests.get(check_url, headers=headers)
        # If we get a 200 response, the project exists
        if response.status_code == 200:
            logging.info(
                f"Project '{project_key}' already exists in workspace '{workspace}'"
            )
            return True
        # If we get a 404 response, the project does not exist
        elif response.status_code == 404:
            logging.debug(
                f"Project '{project_key}' does not exist in workspace '{workspace}'"
            )
            return False
        # Handle other status codes
        else:
            logging.warning(
                f"Unexpected response when checking project existence: {response.status_code}"
            )
            return False
    except requests.exceptions.RequestException as e:
        logging.warning(f"Error checking if project exists: {e}")
        return False


@click.group()
def cli():
    """
    CLI tool for managing Bitbucket projects.
    """
    pass


@cli.command(name="create-project")
@click.option("--project-key", required=True, help="The unique key for the project.")
@click.option("--name", required=True, help="The name of the project.")
@click.option("--description", default="", help="A description for the project.")
def create_project_command(project_key: str, name: str, description: str) -> None:
    """
    Create a new project in a Bitbucket workspace.
    """
    # Validate required environment variables
    required_env_vars = [
        "BITBUCKET_WORKSPACE",
        "BITBUCKET_TOKEN",
        "BITBUCKET_API_URL",
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logging.error(
            f"❌ Missing required environment variables: {', '.join(missing_vars)}"
        )
        raise SystemExit(1)

    # If we get here, all required variables are present
    workspace = os.getenv("BITBUCKET_WORKSPACE")
    token = os.getenv("BITBUCKET_TOKEN")
    url = os.getenv("BITBUCKET_API_URL")

    # Check if project already exists before attempting to create
    if project_exists(url, workspace, project_key, token):
        error_message = f"❌ Project with key '{project_key}' already exists in workspace '{workspace}'"
        logging.error(error_message)
        click.echo(error_message, err=True)
        raise SystemExit(1)

    create_project(url, workspace, project_key, name, description, token)


def main():
    """
    Main entry point for the CLI.
    """
    cli()


if __name__ == "__main__":
    main()

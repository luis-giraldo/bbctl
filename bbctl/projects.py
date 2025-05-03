import os
import requests
import logging
from dotenv import load_dotenv
import click

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
BITBUCKET_API_BASE_URL = "https://api.bitbucket.org/2.0"


def create_project(workspace: str, project_key: str, name: str, description: str, token: str) -> None:
    """
    Create a new project in a Bitbucket workspace.

    Args:
        workspace (str): The Bitbucket workspace ID.
        project_key (str): The unique key for the project.
        name (str): The name of the project.
        description (str): A description for the project.
        token (str): The Bitbucket API token.

    Returns:
        None
    """
    url = f"{BITBUCKET_API_BASE_URL}/workspaces/{workspace}/projects/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "key": project_key,
        "name": name,
        "description": description,
    }

    logging.info(f"Creating project '{name}' in workspace '{workspace}' with key '{project_key}'...")
    logging.debug(f"Payload: {payload}")

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
    except requests.exceptions.RequestException as e:
        if e.response is not None:
            logging.error(f"Response: {e.response.text}")
        logging.error(f"❌ An error occurred while creating the project: {e}")
        raise SystemExit(1)

    if response.status_code in (200, 201):
        logging.info(f"✅ Project '{name}' created successfully!")
    else:
        logging.error(f"❌ Failed to create project: {response.status_code}")
        logging.error(response.json().get("error", {}).get("message", "Unknown error"))
        raise SystemExit(1)  # Exit with a non-zero status code


@click.command()
@click.option("--workspace", required=True, help="The Bitbucket workspace ID.")
@click.option("--project-key", required=True, help="The unique key for the project.")
@click.option("--name", required=True, help="The name of the project.")
@click.option("--description", default="", help="A description for the project.")
@click.option("--token", required=True, help="The Bitbucket API token.")
def main(workspace: str, project_key: str, name: str, description: str, token: str) -> None:
    """
    CLI entry point to create a new project in a Bitbucket workspace.
    """
    create_project(workspace, project_key, name, description, token)


if __name__ == "__main__":
    main()
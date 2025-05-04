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
    # Construct the full URL
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

    logging.info(f"Creating project '{name}' in workspace '{workspace}' with key '{project_key}'...")
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
    else:
        logging.error(f"❌ Failed to create project: {response.status_code}")
        logging.error(response.json().get("error", {}).get("message", "Unknown error"))
        raise SystemExit(1)  # Exit with a non-zero status code


@click.command()
@click.option("--project-key", required=True, help="The unique key for the project.")
@click.option("--name", required=True, help="The name of the project.")
@click.option("--description", default="", help="A description for the project.")
def main(project_key: str, name: str, description: str) -> None:
    """
    CLI entry point to create a new project in a Bitbucket workspace.
    """
    # Read the workspace, token, and API URL from environment variables
    workspace = os.getenv("BITBUCKET_WORKSPACE")
    token = os.getenv("BITBUCKET_TOKEN")
    url = os.getenv("BITBUCKET_API_URL")

    if not workspace:
        logging.error("❌ Missing BITBUCKET_WORKSPACE environment variable.")
        raise SystemExit(1)

    if not token:
        logging.error("❌ Missing BITBUCKET_TOKEN environment variable.")
        raise SystemExit(1)

    create_project(url, workspace, project_key, name, description, token)


if __name__ == "__main__":
    main()
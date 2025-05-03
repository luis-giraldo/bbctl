import os
import requests
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
BITBUCKET_API_BASE_URL = "https://api.bitbucket.org/2.0"


def create_repository(
    workspace: str, repo_slug: str, project_key: str, is_private: bool, token: str
) -> None:
    """
    Create a new repository in a Bitbucket workspace.

    Args:
        workspace (str): The Bitbucket workspace ID.
        repo_slug (str): The repository slug (lowercase, no spaces).
        project_key (str): The project key where the repository will be created.
        is_private (bool): Whether the repository is private.
        token (str): The Bitbucket API token.

    Returns:
        None
    """
    url = f"{BITBUCKET_API_BASE_URL}/repositories/{workspace}/{repo_slug}"
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


if __name__ == "__main__":
    # Load values from environment variables
    workspace = os.getenv("BITBUCKET_WORKSPACE", "mmvpyz2p77")
    repo_slug = os.getenv("BITBUCKET_REPO_SLUG", "my-test-repo")
    project_key = os.getenv("BITBUCKET_PROJECT_KEY", "MYPROJ")
    is_private = os.getenv("BITBUCKET_IS_PRIVATE", "true").lower() == "true"
    token = os.getenv("BITBUCKET_TOKEN")

    # Validate required environment variables
    if not token:
        logging.error("Missing BITBUCKET_TOKEN environment variable.")
        exit(1)

    if not project_key:
        logging.error("Missing BITBUCKET_PROJECT_KEY environment variable.")
        exit(1)

    # Call the function
    create_repository(workspace, repo_slug, project_key, is_private, token)

import os
import requests
import logging
from dotenv import load_dotenv
import click
import json

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def exempt_user_from_pull_request(
    workspace: str, repo_slug: str, username: str, api_url: str, auth: requests.auth.HTTPBasicAuth
) -> None:
    """
    Exempt a user from requiring a pull request to push changes to the default branch.

    Args:
        workspace (str): The Bitbucket workspace ID.
        repo_slug (str): The repository slug.
        username (str): The Bitbucket username or email of the user to exempt.
        api_url (str): The Bitbucket API base URL.
        auth (requests.auth.HTTPBasicAuth): Authentication object.

    Returns:
        None
    """
    url = f"{api_url}/repositories/{workspace}/{repo_slug}/branch-restrictions"
    payload = {
        "kind": "push",
        "branch_match_kind": "glob",
        "pattern": "master",
        "users": [{"type": "user", "username": username}],
    }

    logging.info(
        f"Exempting user '{username}' from requiring a pull request to push to the default branch in repository '{repo_slug}'..."
    )
    logging.debug(f"Payload: {json.dumps(payload, indent=4)}")
    try:
        response = requests.post(url, auth=auth, json=payload)
        response.raise_for_status()
        success_message = f"✅ User '{username}' successfully exempted."
        logging.info(success_message)
        click.echo(success_message)  # Add this line for direct output
    except requests.exceptions.RequestException as e:
        error_message = f"❌ Failed to exempt user '{username}': {str(e)}"
        logging.error(error_message)
        click.echo(error_message, err=True)  # Add this line for direct output
        raise SystemExit(error_message)


@click.group()
def cli():
    """
    CLI tool for managing branch restrictions in Bitbucket repositories.
    """
    pass


@cli.command()
@click.option("--repo-slug", required=True, help="The repository slug.")
@click.option(
    "--username", required=True, help="The Bitbucket username or email to exempt."
)
@click.pass_context
def exempt(ctx, repo_slug: str, username: str) -> None:
    """
    Exempt a user from requiring a pull request to push changes to the default branch.
    """
    try:
        exempt_user_from_pull_request(
            ctx.obj["workspace"], repo_slug, username, ctx.obj["api_url"], ctx.obj["auth"]
        )
    except SystemExit as e:
        # Print the error message to stderr
        click.echo(str(e), err=True)
        raise
    except Exception as e:
        # Handle unexpected exceptions
        click.echo(f"❌ An unexpected error occurred: {str(e)}", err=True)
        raise SystemExit(1)


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
        logging.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        raise SystemExit(1)

    # Prepare shared context
    ctx = {
        "api_url": os.getenv("BITBUCKET_API_URL"),
        "workspace": os.getenv("BITBUCKET_WORKSPACE"),
        "auth": requests.auth.HTTPBasicAuth(
            os.getenv("BITBUCKET_USERNAME"), os.getenv("BITBUCKET_APP_PASSWORD")
        ),
    }

    # Run the CLI with the shared context
    cli(obj=ctx)


if __name__ == "__main__":
    main()
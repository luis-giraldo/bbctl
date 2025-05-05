#!/usr/bin/env python3
import os
import click
import logging
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

from bbctl.branches import cli as branches_cli
from bbctl.projects import cli as projects_cli
from bbctl.repositories import cli as repos_cli
from bbctl.users import cli as users_cli

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@click.group()
@click.pass_context
def cli(ctx):
    """Bitbucket command line interface tool."""
    # Initialize context object (ctx.obj) if it doesn't exist
    ctx.ensure_object(dict)
    
    # Check for required environment variables
    required_vars = ["BITBUCKET_API_URL", "BITBUCKET_WORKSPACE"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logging.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        click.echo(f"❌ Missing required environment variables: {', '.join(missing_vars)}", err=True)
        ctx.exit(1)
    
    # Set up common context values
    ctx.obj["api_url"] = os.environ.get("BITBUCKET_API_URL", "https://api.bitbucket.org/2.0")
    ctx.obj["workspace"] = os.environ.get("BITBUCKET_WORKSPACE")
    
    # Set up authentication if credentials are available
    username = os.environ.get("BITBUCKET_USERNAME")
    app_password = os.environ.get("BITBUCKET_APP_PASSWORD")
    if username and app_password:
        ctx.obj["auth"] = HTTPBasicAuth(username, app_password)
    else:
        # For commands that require authentication
        ctx.obj["auth"] = None

# Add command groups
cli.add_command(branches_cli, name="branches")
cli.add_command(projects_cli, name="projects")
cli.add_command(repos_cli, name="repos")
cli.add_command(users_cli, name="users")

def main():
    cli(obj={})

if __name__ == "__main__":
    main()
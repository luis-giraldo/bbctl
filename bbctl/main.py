#!/usr/bin/env python
import click
from bbctl.branches import cli as branches_cli
from bbctl.projects import cli as projects_cli
from bbctl.repositories import cli as repos_cli
from bbctl.users import cli as users_cli

@click.group()
def cli():
    """Bitbucket command line interface tool."""
    pass

# Add all subcommands
cli.add_command(branches_cli, name="branches")
cli.add_command(projects_cli, name="projects")
cli.add_command(repos_cli, name="repos")
cli.add_command(users_cli, name="users")

if __name__ == "__main__":
    cli()
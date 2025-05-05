# bbctl

A CLI tool for interacting with the Bitbucket API.

## Features
- Create projects
- Create repositories
- Manage users
- Configure branch permissions

## Setup
1. Clone the repo:
   ```bash
   git clone https://github.com/youruser/bitbucket-cli.git
   cd bitbucket-cli
1. Install dependencies:
   ```bash
   poetry install

#add users
poetry run python bbctl/users.py add-user --repo-slug my-test-repo --username mmvpyz2p88-admin (read is the default permission level )--permission read (can be read write or admin)
#remove users from repo
poetry run python bbctl/users.py remove-user --repo-slug my-test-repo --username mmvpyz2p88-admin

#create a project

 poetry run python bbctl/projects.py create-project --project-key TEST_PROJ --name "My Project" --description "A sample project"

 #create repo
 poetry run python bbctl/repositories.py create --repo-slug my-second-repo --project-key MYPROJ --is-private

 #exempt user
 poetry run python bbctl/branches.py exempt --repo-slug my-second-repo --username mmvpyz2p88-admin

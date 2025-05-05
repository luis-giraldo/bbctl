# bbctl

A CLI tool for interacting with the Bitbucket API.

## Features
- Create projects
- Create repositories
- Manage users
- Configure branch permissions

## # bbctl

A command-line interface tool for interacting with the Bitbucket API.

## Features
- Create and manage Bitbucket projects
- Create and configure repositories
- Add and remove user permissions
- Configure branch permissions and exemptions

## Installation

### Download the Binary
```bash
# Download the latest binary
curl -LO https://github.com/luis-giraldo/bbctl/releases/latest/download/bbctl


# Make it executable
chmod +x bbctl

# Move to a directory in your PATH
sudo mv bbctl /usr/local/bin/
```

## Configuration

Set the following environment variables before running commands:

```bash
# Required for all commands
export BITBUCKET_API_URL="https://api.bitbucket.org/2.0"
export BITBUCKET_WORKSPACE={your-workspace-id}

# For OAuth authentication
# Bitbucket documentation https://support.atlassian.com/bitbucket-cloud/docs/use-oauth-on-bitbucket-cloud/
# https://bitbucket.org/site/oauth2/authorize?client_id={key}&response_type=token
export BITBUCKET_TOKEN={your-oauth-token}

# For Basic authentication
export BITBUCKET_USERNAME={your-username}
export BITBUCKET_APP_PASSWORD={your-app-password}
```

## Usage

### User Management
```bash
# Add users to a repository (permission levels: read, write, admin)
bbctl users add-user --repo-slug my-repository --username john.doe --permission write

# Remove users from a repository
bbctl users remove-user --repo-slug my-repository --username john.doe
```

### Project Management
```bash
# Create a project
bbctl projects create-project --project-key TEST_PROJ --name "My Project" --description "A sample project"
```

### Repository Management
```bash
# Create a repository
bbctl repos create-repo --repo-slug my-repository --project-key MYPROJ --is-private
```

### Branch Permissions
```bash
# Exempt user from requiring pull requests
bbctl branches exempt --repo-slug my-repository --username john.doe
```

## Troubleshooting

### Authentication Issues
If you receive authentication errors:
1. Verify your environment variables are set correctly
2. Ensure your token or app password has the necessary permissions
3. Check that your workspace name is correct

### Environment Variables Summary

| Variable | Description |
|----------|-------------|
| `BITBUCKET_API_URL` | Bitbucket API URL (default: https://api.bitbucket.org/2.0) |
| `BITBUCKET_WORKSPACE` | Your Bitbucket workspace name |
| `BITBUCKET_TOKEN` | OAuth token for authentication |
| `BITBUCKET_USERNAME` | Your Bitbucket username |
| `BITBUCKET_APP_PASSWORD` | Your Bitbucket app password |

## License

This project is licensed under the MIT License.
1. Clone the repo:
   ```bash
   git clone https://github.com/luis-giraldo/bbctl.git
   cd bbctl/
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

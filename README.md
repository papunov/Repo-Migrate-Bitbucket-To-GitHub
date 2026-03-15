# Repo Migrate Bitbucket To Github

This script automates the migration of Git repositories from Bitbucket to GitHub using the GitHub CLI (`gh`).

## Requirements
- Python 3
- Git
- [GitHub CLI (`gh`)](https://cli.github.com/) installed and authenticated (`gh auth login`)
- SSH access to both Bitbucket and GitHub

## Configuration
Edit the `repo_migrate.py` file and update the configuration variables with your actual base URLs:

```python
# --- CONFIGURATION ---
BITBUCKET_BASE = "<YOUR_BITBUCKET_BASE_URL>" # e.g. git@bitbucket.org:your_workspace
GITHUB_BASE = "<YOUR_GITHUB_BASE_URL>"       # e.g. git@github.com:your_organization
# --------------------
```

## Usage
Run the script with the name of the repository you want to migrate:

```bash
python repo_migrate.py <repository_name>
```

### Options
- `--temp <folder_name>`: Specify a custom temporary folder name (default: `temp_mirror_repo`).
- `--force`: Delete and recreate the GitHub repository if it already exists.

### Example
```bash
python repo_migrate.py my-awesome-repo --force
```

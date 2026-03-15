import argparse
import subprocess
import os
import sys
import shutil

# --- CONFIGURATION ---
# Use your provided SSH addresses
BITBUCKET_BASE = "<YOUR_BITBUCKET_BASE_URL>" # e.g. git@bitbucket.org:your_workspace
GITHUB_BASE = "<YOUR_GITHUB_BASE_URL>"       # e.g. git@github.com:your_organization
# --------------------

def run(cmd, capture_output=False):
    """Executes a shell command. Stops the script on error, unless it's for checking."""
    if not capture_output:
        print(f"[INFO] Running: {cmd}")

    result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)

    if not capture_output and result.returncode != 0:
        print(f"[ERROR] Command failed: {cmd}")
        sys.exit(1)
    return result

def get_github_org():
    """Extracts the organization/user name from GITHUB_BASE."""
    if ":" in GITHUB_BASE:  # SSH format: git@github.com:org
        return GITHUB_BASE.split(":")[-1].rstrip('/')
    else:  # HTTPS format: https://github.com/org
        return GITHUB_BASE.split("/")[-1].rstrip('/')

def ensure_github_repo(repo_name, force=False):
    """Checks if the repo exists in GitHub and creates it. If force is True, recreates it."""
    org = get_github_org()
    full_repo_path = f"{org}/{repo_name}"

    print(f"[INFO] Checking GitHub repository: {full_repo_path}...")

    # Check if the repo exists via GitHub CLI
    check_cmd = f"gh repo view {full_repo_path}"
    result = run(check_cmd, capture_output=True)
    exists = (result.returncode == 0)

    # If recreation is requested and the repo exists
    if exists and force:
        print(f"[WARNING] Force option active. Deleting existing repo {full_repo_path}...")
        # --yes automatically confirms the deletion
        run(f"gh repo delete {full_repo_path} --yes")
        exists = False

    if not exists:
        print(f"[INFO] Creating new repository: {full_repo_path}...")
        # Creates a private repo.
        create_cmd = f"gh repo create {full_repo_path} --private"
        run(create_cmd)
        print(f"[SUCCESS] Created repository: {full_repo_path}")
    else:
        print(f"[INFO] Repository {full_repo_path} already exists. Proceeding with migration...")

def main():
    parser = argparse.ArgumentParser(description="Migrate Bitbucket repo to GitHub")
    parser.add_argument("repo_name", help="Name of the repository to migrate")
    parser.add_argument("--temp", default="temp_mirror_repo", help="Temporary folder name")
    parser.add_argument("--force", action="store_true", help="Delete and recreate the GitHub repo if it already exists")

    args = parser.parse_args()

    repo_name = args.repo_name
    temp_dir = args.temp
    force_mode = args.force

    # Construct the URLs
    bb_base = BITBUCKET_BASE.rstrip('/')
    gh_base = GITHUB_BASE.rstrip('/')

    bitbucket_url = f"{bb_base}/{repo_name}.git"
    github_url = f"{gh_base}/{repo_name}.git"

    print(f"🚀 Starting migration for: {repo_name}")
    if force_mode:
        print("⚠️  FORCE MODE: Existing target repo will be deleted and recreated.")
    print(f"🔗 Source: {bitbucket_url}")
    print(f"🎯 Target: {github_url}\n")

    # 1. Check/create/recreate the repo in GitHub
    ensure_github_repo(repo_name, force=force_mode)

    # 2. Clean up old temporary folder
    if os.path.exists(temp_dir):
        print("[INFO] Removing old temp folder...")
        shutil.rmtree(temp_dir)

    # 3. Clone as mirror
    run(f"git clone --mirror {bitbucket_url} {temp_dir}")

    # 4. Change directory and push
    original_dir = os.getcwd()
    os.chdir(temp_dir)

    try:
        run(f"git remote set-url origin {github_url}")
        run("git push --mirror")
        print(f"\n[SUCCESS] Migration for {repo_name} completed successfully!")
    finally:
        os.chdir(original_dir)
        # By default we leave the temp folder, but you can uncomment the line below:
        # shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
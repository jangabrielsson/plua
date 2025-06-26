#!/usr/bin/env python3
"""
Script to download the latest Windows build artifact from GitHub Actions
"""

import os
import sys
import requests
import zipfile
from pathlib import Path


def download_latest_artifact():
    """Download the latest Windows build artifact"""
    
    # You'll need to set these environment variables or replace with your values
    repo_owner = os.getenv('GITHUB_REPO_OWNER', 'your-username')
    repo_name = os.getenv('GITHUB_REPO_NAME', 'plua')
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable not set")
        print("Please set it with: export GITHUB_TOKEN=your_github_token")
        print("You can create a token at: https://github.com/settings/tokens")
        return False
    
    # GitHub API endpoints
    api_base = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    
    # Get the latest workflow run
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    print("Fetching latest workflow run...")
    runs_response = requests.get(
        f"{api_base}/actions/runs",
        headers=headers,
        params={'workflow_id': 'windows-build.yml', 'status': 'completed', 'conclusion': 'success'}
    )
    
    if runs_response.status_code != 200:
        print(f"Error fetching workflow runs: {runs_response.status_code}")
        print(runs_response.text)
        return False
    
    runs = runs_response.json()
    if not runs['workflow_runs']:
        print("No successful workflow runs found")
        return False
    
    latest_run = runs['workflow_runs'][0]
    run_id = latest_run['id']
    
    print(f"Latest successful run: {run_id}")
    
    # Get artifacts for this run
    artifacts_response = requests.get(
        f"{api_base}/actions/runs/{run_id}/artifacts",
        headers=headers
    )
    
    if artifacts_response.status_code != 200:
        print(f"Error fetching artifacts: {artifacts_response.status_code}")
        return False
    
    artifacts = artifacts_response.json()
    windows_artifact = None
    
    for artifact in artifacts['artifacts']:
        if artifact['name'] == 'plua-windows-exe':
            windows_artifact = artifact
            break
    
    if not windows_artifact:
        print("No plua-windows-exe artifact found")
        return False
    
    # Download the artifact
    download_url = windows_artifact['archive_download_url']
    print(f"Downloading artifact: {windows_artifact['name']}")
    
    download_response = requests.get(download_url, headers=headers)
    if download_response.status_code != 200:
        print(f"Error downloading artifact: {download_response.status_code}")
        return False
    
    # Create dist directory
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    # Save the zip file
    zip_path = dist_dir / "plua-windows.zip"
    with open(zip_path, 'wb') as f:
        f.write(download_response.content)
    
    print(f"Downloaded to: {zip_path}")
    
    # Extract the zip file
    print("Extracting...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dist_dir)
    
    # Clean up the zip file
    zip_path.unlink()
    
    print("✅ Windows executable downloaded and extracted to ./dist/")
    return True


if __name__ == "__main__":
    if not download_latest_artifact():
        sys.exit(1) 
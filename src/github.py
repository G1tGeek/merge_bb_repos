import requests
from src.logger import log_info

def gh_headers(token):
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }

def create_github_repo(org, repo, token):
    r = requests.post(
        f"https://api.github.com/orgs/{org}/repos",
        headers=gh_headers(token),
        json={"name": repo, "private": True},  #make it vars pvt or public
    )
    if r.status_code not in (201, 422):
        r.raise_for_status()
    log_info(f"GitHub repo ensured: {repo}")

def set_default_branch(org, repo, branch, token):
    requests.patch(
        f"https://api.github.com/repos/{org}/{repo}",
        headers=gh_headers(token),
        json={"default_branch": branch},
    )

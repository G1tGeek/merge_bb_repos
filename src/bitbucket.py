import requests
from src.logger import log_info

def bb_auth(email, token):
    return (email, token)

def bb_headers():
    return {"Accept": "application/json"}

def get_all_bitbucket_repos(workspace, email, token):
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}"
    repos = []

    while url:
        r = requests.get(url, headers=bb_headers(), auth=bb_auth(email, token))
        r.raise_for_status()
        data = r.json()
        repos.extend([r["slug"] for r in data.get("values", [])])
        url = data.get("next")

    log_info(f"Discovered {len(repos)} Bitbucket repos")
    return repos

def get_bitbucket_pull_requests(workspace, repo, email, token):
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests"
    params = {"state": "OPEN,MERGED,DECLINED,SUPERSEDED"}
    prs = []

    while url:
        r = requests.get(url, headers=bb_headers(), auth=bb_auth(email, token), params=params)
        r.raise_for_status()
        data = r.json()
        prs.extend(data.get("values", []))
        url = data.get("next")
        params = None

    return prs

import requests
import json
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
        r = requests.get(
            url,
            headers=bb_headers(),
            auth=bb_auth(email, token),
            params=params,
        )
        r.raise_for_status()
        data = r.json()
        prs.extend(data.get("values", []))
        url = data.get("next")
        params = None

    return prs

def export_all_pull_requests(
    workspace: str,
    email: str,
    token: str,
    output_file: str = "bitbucket_prs.json",
):
    """
    Fetch ALL pull requests across ALL repositories
    and export them to a JSON file with rich metadata
    (equivalent to the jq command output).
    """

    log_info("Starting Bitbucket Pull Request inventory")

    repos = get_all_bitbucket_repos(workspace, email, token)
    all_prs = []

    for repo in repos:
        log_info(f"Fetching PRs for repo: {repo}")

        prs = get_bitbucket_pull_requests(
            workspace=workspace,
            repo=repo,
            email=email,
            token=token,
        )

        for pr in prs:
            reviewers = [
                r.get("display_name")
                for r in (pr.get("reviewers") or [])
                if r.get("display_name")
            ]

            approvers = [
                p.get("user", {}).get("display_name")
                for p in (pr.get("participants") or [])
                if p.get("approved") is True
            ]

            all_prs.append({
                # ---------- Identity ----------
                "workspace": workspace,
                "repository": repo,
                "pr_id": pr.get("id"),
                "title": pr.get("title"),
                "state": pr.get("state"),

                # ---------- Author ----------
                "author": pr.get("author", {}).get("display_name"),

                # ---------- Branches ----------
                "source_branch": pr.get("source", {}).get("branch", {}).get("name"),
                "target_branch": pr.get("destination", {}).get("branch", {}).get("name"),

                # ---------- Commits ----------
                "source_commit": pr.get("source", {}).get("commit", {}).get("hash"),
                "destination_commit": pr.get("destination", {}).get("commit", {}).get("hash"),
                "merge_commit": (pr.get("merge_commit") or {}).get("hash"),


                # ---------- Reviews ----------
                "reviewers": reviewers,
                "approvers": approvers,

                # ---------- Lifecycle ----------
                "close_source_branch": pr.get("close_source_branch"),
                "decline_reason": pr.get("reason"),

                # ---------- Dates ----------
                "created_on": pr.get("created_on"),
                "updated_on": pr.get("updated_on"),

                # ---------- Links ----------
                "pr_url": pr.get("links", {}).get("html", {}).get("href"),
            })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_prs, f, indent=2)

    log_info(f"Exported {len(all_prs)} PRs to {output_file}")

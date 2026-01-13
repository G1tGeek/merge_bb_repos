import os
import csv
import subprocess
import shutil
from urllib.parse import quote

from src.git_utils import run
from src.logger import log_info
from src.bitbucket import get_all_bitbucket_repos
from src.github import create_github_repo, set_default_branch

# ================= CONSTANTS =================

BASE_MIRROR_DIR = os.path.expanduser("~/bb_mirrors")
os.makedirs(BASE_MIRROR_DIR, exist_ok=True)

# ================= REPO DISCOVERY =================

def get_repos_from_csv(csv_file):
    repos = set()

    log_info(f"Reading repositories from CSV: {csv_file}")

    with open(csv_file, newline="") as f:
        reader = csv.DictReader(f)
        if "repository" not in reader.fieldnames:
            raise ValueError("CSV must contain 'repository' column")

        for row in reader:
            repo = row.get("repository", "").strip()
            if repo:
                repos.add(repo)

    return list(repos)


def resolve_repo_list(repos_cfg, workspace, email, token):
    """
    Supported formats:
    - "*"                  → all Bitbucket repos
    - ["*"]                → all Bitbucket repos (backward compatible)
    - "repos.csv"          → repos from CSV
    """

    if repos_cfg == "*":
        log_info("Migrating ALL Bitbucket repositories")
        return get_all_bitbucket_repos(workspace, email, token)

    if isinstance(repos_cfg, list) and repos_cfg == ["*"]:
        log_info("Migrating ALL Bitbucket repositories (list format)")
        return get_all_bitbucket_repos(workspace, email, token)

    if isinstance(repos_cfg, str) and repos_cfg.endswith(".csv"):
        log_info(f"Migrating repositories from CSV: {repos_cfg}")
        return get_repos_from_csv(repos_cfg)

    raise ValueError(
        "Invalid repositories config. Use '*', ['*'], or a CSV filename."
    )

# ================= GIT HELPERS =================

def get_default_branch(repo, bb_url):
    try:
        out = subprocess.check_output(
            ["git", "ls-remote", "--symref", bb_url, "HEAD"]
        ).decode()

        for line in out.splitlines():
            if line.startswith("ref: refs/heads/"):
                return line.split("/")[-1].split("\t")[0]
    except Exception:
        pass

    return "main"

# ================= MAIN SYNC =================

def sync_repos(config, secrets):
    BB = secrets["bitbucket"]
    GH = secrets["github"]

    repos = resolve_repo_list(
        config["bitbucket"]["repositories"],
        config["bitbucket"]["workspace"],
        BB["email"],
        BB["access_token"],
    )

    log_info(f"Total repositories to sync: {len(repos)}")

    for repo in repos:
        log_info(f"===== Syncing repository: {repo} =====")

        bb_user = quote(BB["username"], safe="")
        bb_token = quote(BB["access_token"], safe="")

        bb_url = (
            f"https://{bb_user}:{bb_token}"
            f"@bitbucket.org/{config['bitbucket']['workspace']}/{repo}.git"
        )

        gh_url = (
            f"https://{GH['username']}:{GH['access_token']}"
            f"@github.com/{config['github']['organization']}/{repo}.git"
        )

        mirror = os.path.join(BASE_MIRROR_DIR, f"{repo}.git")

        default_branch = get_default_branch(repo, bb_url)

        create_github_repo(
            config["github"]["organization"],
            repo,
            GH["access_token"],
        )

        # ---------- Clone or Update Mirror ----------
        if not os.path.exists(mirror):
            log_info("Cloning mirror repository")
            run(["git", "clone", "--mirror", bb_url, mirror])
        else:
            log_info("Updating existing mirror")
            # Ensure origin always has credentials
            run(["git", "remote", "set-url", "origin", bb_url], cwd=mirror)

            try:
                run(["git", "fetch", "--prune"], cwd=mirror)
            except subprocess.CalledProcessError:
                log_info("Mirror fetch failed, recreating mirror")
                shutil.rmtree(mirror)
                run(["git", "clone", "--mirror", bb_url, mirror])

        # ---------- Configure GitHub Remote ----------
        remotes = subprocess.check_output(
            ["git", "remote"], cwd=mirror
        ).decode()

        if "github" in remotes:
            run(["git", "remote", "set-url", "github", gh_url], cwd=mirror)
        else:
            run(["git", "remote", "add", "github", gh_url], cwd=mirror)

        # ---------- Push to GitHub ----------
        run(["git", "push", "--mirror", "github"], cwd=mirror)

        # ---------- Set Default Branch ----------
        set_default_branch(
            config["github"]["organization"],
            repo,
            default_branch,
            GH["access_token"],
        )

        log_info(f"Completed sync for repository: {repo}")

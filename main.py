from src.logger import setup_logger
from src.config_loader import load_configs
from src.git_utils import git_config_identity
from src.repo_sync import sync_repos
from src.bitbucket import export_all_pull_requests


def main():
    setup_logger()
    config, secrets = load_configs()

    # -------- Configure Git identity --------
    git_config_identity(
        secrets["github"]["username"],
        secrets["github"]["email"],
    )

    # -------- Export Bitbucket PRs --------
    export_all_pull_requests(
        workspace=config["bitbucket"]["workspace"],
        email=secrets["bitbucket"]["email"],
        token=secrets["bitbucket"]["access_token"],
        output_file="bitbucket_prs.json",
    )

    # -------- Migrate Repositories --------
    sync_repos(config, secrets)


if __name__ == "__main__":
    main()

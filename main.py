from src.logger import setup_logger
from src.config_loader import load_configs
from src.git_utils import git_config_identity
from src.repo_sync import sync_repos

def main():
    setup_logger()
    config, secrets = load_configs()

    git_config_identity(
        secrets["github"]["username"],
        secrets["github"]["email"]
    )

    sync_repos(config, secrets)

if __name__ == "__main__":
    main()

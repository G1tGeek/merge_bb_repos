import subprocess
from src.logger import log_info

def _mask_cmd(cmd):
    """
    Masks credentials in URLs like:
    https://user:token@github.com/org/repo.git
    """
    masked = []

    for part in cmd:
        if part.startswith("http") and "@" in part:
            # Replace user:token@ with ***:***@
            prefix, rest = part.split("://", 1)
            if "@" in rest:
                masked.append(f"{prefix}://***:***@{rest.split('@', 1)[1]}")
            else:
                masked.append(part)
        else:
            masked.append(part)

    return masked

def run(cmd, cwd=None):
    safe_cmd = _mask_cmd(cmd)
    log_info(f"Running command: {' '.join(safe_cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)

def git_config_identity(username, email):
    run(["git", "config", "--global", "user.name", username])
    run(["git", "config", "--global", "user.email", email])

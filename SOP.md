# Bitbucket to GitHub Repository Migration Script

## 1. Purpose
This script mirrors repositories from Bitbucket to GitHub while preserving full history, branches, tags, and default branch settings.

Used for:
- Platform migration
- Backup replication
- Dual-hosting strategies

## 2. Scope
- Migrate all repositories
- Migrate selected repositories via CSV
- Safe re-runs (idempotent)

## 3. Preconditions
### System Requirements
- Python 3.9+
- Git 2.30+
- Network access to Bitbucket & GitHub

### Required Permissions
- Bitbucket: Repository read
- GitHub: Repository create & push

## 4. Configuration
### config.yaml (Non-Secret)
```yaml
bitbucket:
  workspace: opstree-pinelabs
  repositories:
    - "*"

github:
  organization: opstree-org
```

### Environment Variables (Secrets)
```bash
export BITBUCKET_USERNAME=bb_user
export BITBUCKET_EMAIL=bb_email
export BITBUCKET_ACCESS_TOKEN=bb_token

export GITHUB_USERNAME=gh_user
export GITHUB_EMAIL=gh_email
export GITHUB_ACCESS_TOKEN=gh_token
```

## 5. Execution Procedure
```bash
python3 main.py
```

### Execution Flow
1. Logger setup
2. Git identity configured
3. Repository list resolved
4. GitHub repo ensured
5. Bitbucket mirror cloned or updated
6. Mirror pushed to GitHub
7. Default branch set

## 6. Data Storage
- Local mirrors: ~/bb_mirrors
- Logs: logs/migration.log

## 7. Error Handling & Recovery
- 403 errors fixed by resetting remote URL
- Corrupt mirrors auto re-cloned
- Existing GitHub repos handled safely

## 8. Security Controls
- No secrets written to disk
- Credentials masked in logs
- CI/CD safe execution

## 9. Best Practices
- Use service accounts
- Migrate in batches
- Validate sample repositories
- Rotate tokens post-migration

## 10. Rollback
- Delete GitHub repos if required
- Bitbucket repos remain unchanged
- Remove mirrors if needed

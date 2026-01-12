import yaml

def load_configs():
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    with open("auto_token.yaml") as f:
        secrets = yaml.safe_load(f)

    return config, secrets

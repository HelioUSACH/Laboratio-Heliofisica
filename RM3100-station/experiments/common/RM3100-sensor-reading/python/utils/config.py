import yaml

def config_load(paths: dict):
    """
    Dictionary with all usage variables
    """
    config_file = paths["config_file"] / "config.yaml"

    with open(config_file, "r") as f:
        cfg = yaml.safe_load(f)

    return cfg
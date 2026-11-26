from pathlib import Path

def path_file():
    """
    Dictionary with the necessary folders for the code.
    """

    base = Path(Path(__file__).resolve().parent.parent.parent)

    project_paths = {
        "raw_file": ("data", "raw"),
        "processed_file": ("data", "processed"),
    }

    paths = {key: base.joinpath(*parts) for key, parts in project_paths.items()}

    paths["config_file"] = base / "config"
    paths["log_file"] = base / "log"
    paths["figures"] = base / "figures"

    for path in paths.values():
        path.mkdir(parents = True, exist_ok = True)

    paths["base_file"] = base

    return paths

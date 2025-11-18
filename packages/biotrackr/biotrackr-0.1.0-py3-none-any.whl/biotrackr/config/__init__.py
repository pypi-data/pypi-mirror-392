from pathlib import Path
import yaml

DEFAULT_CONFIG_PATH = Path(__file__).parent / "base.yaml"

def load_config(config_path: Path | None = None) -> dict:
    """Load configuration, merging defaults, user config, and custom overrides."""
    with open(DEFAULT_CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f) or {}

    if config_path:
        if config_path.exists():
            with open(config_path, "r") as f:
                user_config = yaml.safe_load(f) or {}
            config.update(user_config)

    return config


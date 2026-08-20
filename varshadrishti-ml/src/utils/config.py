import yaml
from pathlib import Path
from typing import Dict, Any

def load_config(config_path: str = "configs/config.yaml") -> Dict[str, Any]:
    """Loads configuration from a YAML file."""
    path = Path(config_path)
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    return config if config is not None else {}

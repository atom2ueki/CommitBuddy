"""
Configuration management for Commit Buddy.
"""
import os
import yaml
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

# Default config paths
DEFAULT_CONFIG_PATH = os.path.expanduser("~/.commitbuddy/config.yaml")
DEFAULT_MODEL_PATH = os.path.expanduser("~/.commitbuddy/models")

@dataclass
class CommitBuddyConfig:
    """Configuration for Commit Buddy."""
    # LLM settings
    model_path: str
    context_length: int = 4096
    temperature: float = 0.2
    max_tokens: int = 1024
    n_gpu_layers: int = 1
    n_batch: int = 512
    n_threads: int = 4

    # Git settings
    git_command: str = "git"
    auto_commit: bool = False

    # LangChain settings
    chain_verbose: bool = False

    # Commit message settings
    commit_types: List[str] = None
    commit_scopes: List[str] = None

    def __post_init__(self):
        """Set default values for commit types and scopes if not provided."""
        if self.commit_types is None:
            self.commit_types = [
                "feat", "fix", "docs", "style", "refactor",
                "perf", "test", "build", "ci", "chore", "revert"
            ]

        if self.commit_scopes is None:
            self.commit_scopes = []

def load_config(config_path: Optional[str] = None) -> CommitBuddyConfig:
    """
    Load configuration from a YAML file.

    Args:
        config_path: Path to the configuration file. If None, uses default.

    Returns:
        CommitBuddyConfig: Loaded configuration.
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH

    # Ensure path is expanded
    config_path = os.path.expanduser(config_path)

    # Create default config if it doesn't exist
    if not os.path.exists(config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        default_config = {
            "model_path": os.path.join(DEFAULT_MODEL_PATH, "ggml-model.bin"),
            "context_length": 4096,
            "temperature": 0.2,
            "max_tokens": 1024,
            "n_gpu_layers": 1,
            "n_batch": 512,
            "n_threads": 4,
            "git_command": "git",
            "auto_commit": False,
            "chain_verbose": False,
            "commit_types": [
                "feat", "fix", "docs", "style", "refactor",
                "perf", "test", "build", "ci", "chore", "revert"
            ],
            "commit_scopes": []
        }

        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            yaml.dump(default_config, f)

    # Load config from file
    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)

    return CommitBuddyConfig(**config_data)

"""Configuration management for GORO."""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class RepoConfig(BaseModel):
    """Configuration for a single repository."""

    name: str
    path: Path
    plugins: List[str] = Field(default_factory=list)
    enabled: bool = True

    class Config:
        json_encoders = {Path: str}
        arbitrary_types_allowed = True

    def __init__(self, **data):
        if "path" in data and not isinstance(data["path"], Path):
            data["path"] = Path(data["path"]).expanduser().resolve()
        super().__init__(**data)
    
    def dict(self, **kwargs):
        """Override dict() to ensure path is serialized as string."""
        d = super().dict(**kwargs)
        d["path"] = str(d["path"])
        return d


class Config(BaseModel):
    """Main configuration class for the application."""

    repos: Dict[str, RepoConfig] = Field(default_factory=dict)
    default_plugins: List[str] = Field(default_factory=list)
    config_path: Optional[Path] = None

    class Config:
        json_encoders = {Path: str}

    @classmethod
    def get_config_path(cls) -> Path:
        """Get the path to the configuration file."""
        config_dir = Path.home() / ".config" / "goro"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from file."""
        config_path = cls.get_config_path()
        if not config_path.exists():
            return cls()

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return cls(**data)
        except (json.JSONDecodeError, OSError) as e:
            # If there's an error loading the config, return a default one
            return cls()

    def save(self) -> None:
        """Save configuration to file."""
        config_path = self.get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            # Convert all Path objects to strings before serialization
            config_dict = self.dict(
                exclude={"config_path"},
                exclude_none=True,
            )
            # Ensure all paths in repos are strings
            if "repos" in config_dict:
                for repo_name, repo_data in config_dict["repos"].items():
                    if isinstance(repo_data, dict) and "path" in repo_data:
                        repo_data["path"] = str(repo_data["path"])
            
            json.dump(
                config_dict,
                f,
                indent=2,
                ensure_ascii=False,
            )

    def add_repo(self, name: str, path: Path) -> None:
        """Add a new repository to the configuration.

        Args:
            name: Short name for the repository
            path: Path to the repository
        """
        self.repos[name] = RepoConfig(name=name, path=path)
        self.save()

    def remove_repo(self, name: str) -> bool:
        """Remove a repository from the configuration.

        Args:
            name: Name of the repository to remove

        Returns:
            bool: True if the repository was removed, False if it didn't exist
        """
        if name in self.repos:
            del self.repos[name]
            self.save()
            return True
        return False

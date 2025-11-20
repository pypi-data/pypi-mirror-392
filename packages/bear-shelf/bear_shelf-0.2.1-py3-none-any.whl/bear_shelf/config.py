"""Configuration management for JSONL Database."""

from dataclasses import dataclass, field

from bear_shelf._internal._info import _ProjectMetadata  # noqa: TC001
from bear_shelf._internal.debug import METADATA

UNIFIED_DATA_VERSION = "0.1.0"
"""The current version of the unified data format."""


@dataclass(slots=True)
class Metadata:
    """Metadata about the application."""

    info_: _ProjectMetadata = field(default_factory=lambda: METADATA)
    unified_data_version: str = UNIFIED_DATA_VERSION

    def __getattr__(self, name: str) -> str:
        """Delegate attribute access to the internal _ProjectMetadata instance."""
        return getattr(self.info_, name)


@dataclass(slots=True)
class AppConfig:
    """Application configuration model."""

    env: str = "prod"
    debug: bool = False
    metadata: Metadata = field(default_factory=Metadata)


app_config = AppConfig()

__all__ = ["AppConfig", "Metadata", "app_config"]

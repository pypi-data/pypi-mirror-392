"""A storage for TOON files using the unified data format."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bear_shelf.datastore.unified_data import UnifiedDataFormat
from codec_cub.config import ToonCodecConfig
from codec_cub.general.helpers import touch
from codec_cub.toon.file_handler import ToonFileHandler

from ._base_storage import Storage

if TYPE_CHECKING:
    from pathlib import Path


class ToonStorage(Storage):
    """A TOON file storage backend using the unified data format."""

    def __init__(self, file: str | Path, **kwargs) -> None:
        """Initialize TOON storage.

        Args:
            file: Path to the TOON file
            file_mode: File mode for opening (default: "r+b" for binary read/write)
        """
        super().__init__()
        self.file: Path = touch(file, mkdir=True, create_file=True)
        self.handler = ToonFileHandler(file=self.file, config=ToonCodecConfig(**kwargs))

    def read(self) -> UnifiedDataFormat | None:
        """Read data from TOON file.

        Returns:
            UnifiedDataFormat instance or empty if file doesn't exist.
        """
        try:
            model: UnifiedDataFormat = UnifiedDataFormat.model_validate(self.handler.read())
            return model
        except Exception:
            return None

    def write(self, data: UnifiedDataFormat) -> None:
        """Write data to TOON file.

        Args:
            data: UnifiedDataFormat instance to write.
        """
        toon_data: dict = data.model_dump(exclude_none=True)
        self.handler.write(toon_data)

    def close(self) -> None:
        """Close the file handle (no-op for TOON handler)."""
        if self.closed:
            return

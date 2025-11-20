"""Dynamic storage backend registry.

THIS FILE IS AUTO-GENERATED - DO NOT EDIT MANUALLY
Run `file_vault sync-storage` to regenerate
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload

from .json import JsonStorage
from .jsonl import JSONLStorage
from .memory import InMemoryStorage
from .msgpack import MsgPackStorage
from .toml import TomlStorage
from .xml import XMLStorage
from .yaml import YamlStorage

if TYPE_CHECKING:
    from ._base_storage import Storage

type StorageChoices = Literal["json", "jsonl", "memory", "msgpack", "toml", "xml", "yaml", "default"]

storage_map: dict[str, type[Storage]] = {
    "json": JsonStorage,
    "jsonl": JSONLStorage,
    "memory": InMemoryStorage,
    "msgpack": MsgPackStorage,
    "toml": TomlStorage,
    "xml": XMLStorage,
    "yaml": YamlStorage,
    "default": JSONLStorage,
}


@overload
def get_storage(storage: Literal["json"]) -> type[JsonStorage]: ...
@overload
def get_storage(storage: Literal["jsonl"]) -> type[JSONLStorage]: ...
@overload
def get_storage(storage: Literal["memory"]) -> type[InMemoryStorage]: ...
@overload
def get_storage(storage: Literal["msgpack"]) -> type[MsgPackStorage]: ...
@overload
def get_storage(storage: Literal["toml"]) -> type[TomlStorage]: ...
@overload
def get_storage(storage: Literal["xml"]) -> type[XMLStorage]: ...
@overload
def get_storage(storage: Literal["yaml"]) -> type[YamlStorage]: ...
@overload
def get_storage(storage: Literal["default"]) -> type[JSONLStorage]: ...
def get_storage(storage: StorageChoices = "default") -> type[Storage]:
    """Factory function to get a storage backend by name.

    Args:
        storage: Storage backend name

    Returns:
        Storage backend class
    """
    storage_type: type[Storage] = storage_map.get(storage, storage_map["default"])
    return storage_type


__all__ = ["StorageChoices", "get_storage", "storage_map"]

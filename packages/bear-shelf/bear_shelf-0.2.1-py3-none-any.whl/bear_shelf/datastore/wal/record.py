"""Write-Ahead Log Record Model."""

from enum import StrEnum
from typing import Any
import zlib

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_serializer, field_validator

from bear_epoch_time import EpochTimestamp


def compute_checksum(data: str) -> str:
    """Compute a checksum for the given data string."""
    return str(zlib.crc32(data.encode("utf-8")) & 0xFFFFFFFF)


class Operation(StrEnum):
    """Enumeration of WAL operations."""

    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    COMMIT = "COMMIT"


class WALRecord(BaseModel):
    """A record in the Write-Ahead Log."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    txid: int
    op: Operation
    data: dict[str, Any] | None = Field(default=None)
    timestamp: EpochTimestamp = Field(default_factory=EpochTimestamp.now)

    @field_validator("timestamp", mode="before")
    @classmethod
    def validate_timestamp(cls, value: Any) -> EpochTimestamp:
        """Validate and convert the timestamp field to EpochTimestamp."""
        if isinstance(value, int):
            return EpochTimestamp(value)
        if isinstance(value, EpochTimestamp):
            return value
        raise TypeError("timestamp must be an int or EpochTimestamp")

    @field_serializer("timestamp")
    def serialize_timestamp(self, value: EpochTimestamp) -> int:
        """Serialize the timestamp field to an integer."""
        return int(value)

    @computed_field
    def checksum(self) -> str:
        """Compute a checksum for the WALRecord."""
        record_json: str = self.model_dump_json(exclude={"checksum"}, exclude_none=True)
        return compute_checksum(record_json)

    def __str__(self) -> str:
        """String representation of the WALRecord."""
        output: str = f"WALRecord(txid={self.txid}, op={self.op}"
        if self.data is not None:
            output += f", data={self.data}"
        output += f", timestamp={int(self.timestamp)})"
        return output

    def __repr__(self) -> str:
        """Official string representation of the WALRecord."""
        return self.__str__()

"""Module holding Vemmio data models."""

from dataclasses import dataclass, field
from typing import Any

from mashumaro import field_options
from mashumaro.config import BaseConfig
from mashumaro.mixins.orjson import DataClassORJSONMixin


class BaseModel(DataClassORJSONMixin):
    """Base model class for Vemmio data models."""

    class Config(BaseConfig):
        """Configuration for Mashumaro serialization."""

        debug = False


@dataclass(kw_only=True)
class Node(BaseModel):
    """Object holding information about a Vemmio node."""

    uuid: str = field(default="0", metadata=field_options(alias="uuid"))
    """Node ID."""

    capabilities: list[str] = field(
        default_factory=list, metadata=field_options(alias="capabilities")
    )
    """Node capabilities."""


@dataclass(kw_only=True)
class Info(BaseModel):
    """Object holding information from Vemmio."""

    type: str = field(default="Unknown", metadata=field_options(alias="type"))
    """"""

    mac: str = field(default="00:00:00:00:00:00", metadata=field_options(alias="mac"))
    """MAC address of the Vemmio device."""

    revision: str = field(default="0.0.0", metadata=field_options(alias="revision"))
    """Vemmio firmware version."""

    nodes: list[Node] = field(
        default_factory=list, metadata=field_options(alias="nodes")
    )
    """List of nodes in Vemmio device."""

    fw: str = field(default="Unknown", metadata=field_options(alias="fw"))
    """Vemmio firmware name."""


@dataclass(kw_only=True)
class DeviceModel(BaseModel):
    """Object holding all common information of Vemmio device."""

    info: Info = field(default_factory=Info, metadata=field_options(alias="info"))

    def create_from_dict(self, data: dict[str, Any]) -> bool:
        """Create DeviceModel object from Vemmio API response.

        Args:
        ----
            data: Data received from a Vemmio device API.

        Returns:
        -------
            True if the DeviceModel object was created successfully, False otherwise.

        """

        if _info := data.get("info"):
            self.info = Info.from_dict(_info)
            return True

        return False

    def update_from_dict(self, data: dict[str, Any]) -> "DeviceModel":
        """Return DeviceModel object from Vemmio API response.

        Args:
        ----
            data: Update the device object with the data received from a
                Vemmio device API.

        Returns:
        -------
            The updated DeviceModel object.

        """

        if _info := data.get("info"):
            self.info = Info.from_dict(_info)

        return self


@dataclass(kw_only=True)
class RelayState(BaseModel):
    """Enum holding relay states."""

    name: str = field(default="Unknown", metadata=field_options(alias="name"))

    state: str = field(default="off", metadata=field_options(alias="state"))

    timestamp: int = field(default=0, metadata=field_options(alias="timestamp"))


@dataclass(kw_only=True)
class InputState(BaseModel):
    """Object holding input states from Implant Vemmio device."""

    name: str = field(default="Unknown", metadata=field_options(alias="name"))

    state: str = field(default="closed", metadata=field_options(alias="state"))

    timestamp: int = field(default=0, metadata=field_options(alias="timestamp"))


@dataclass(kw_only=True)
class ImplantStatusModel(BaseModel):
    """Object holding status information from Implant Vemmio device."""

    relays: list[RelayState] = field(
        default_factory=list, metadata=field_options(alias="relays")
    )

    inputs: list[InputState] = field(
        default_factory=list, metadata=field_options(alias="inputs")
    )

    def update_from_dict(self, data: dict[str, Any]) -> "ImplantStatusModel":
        """Return ImplantStatusModel object from Vemmio API response.

        Args:
        ----
            data: Update the device object with the data received from a
                Vemmio device API.

        Returns:
        -------
            The updated DeviceModel object.

        """

        if _relays := data.get("relays"):
            self.relays = [RelayState.from_dict(relay) for relay in _relays]

        if _inputs := data.get("inputs"):
            self.inputs = [InputState.from_dict(inp) for inp in _inputs]

        return self

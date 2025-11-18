"""Vemmio Device capability classes."""

from typing import Final

CAPABILITY_TYPES: Final = ["switch", "openClose"]


class Capability:
    """Defines a Vemmio device capability."""

    node_uuid = ""
    id = 0
    name = ""

    def __init__(self, name: str, node_uuid: str, id: int) -> None:
        """Initialize the Capability object."""
        self.name = name
        self.node_uuid = node_uuid
        self.id = id

    def __repr__(self) -> str:
        """Return a string representation of the Capability object."""
        return f"Capability(name={self.name}, node_uuid={self.node_uuid}, id={self.id})"

    def get_uuid_with_id(self) -> str:
        """Get a unique identifier for the capability based on node UUID and ID."""
        return f"{self.node_uuid}_{self.id}"


class SwitchCapability(Capability):
    """Defines a Vemmio switch capability."""

    def __init__(self, name: str, node_uuid: str, id: int) -> None:
        """Initialize the SwitchCapability object."""
        super().__init__(name=name, node_uuid=node_uuid, id=id)

    def __repr__(self) -> str:
        """Return a string representation of the SwitchCapability object."""
        return f"SwitchCapability(name={self.name}, node_uuid={self.node_uuid}, id={self.id})"


class OpenCloseCapability(Capability):
    """Defines a Vemmio open/close capability."""

    def __init__(self, name: str, node_uuid: str, id: int) -> None:
        """Initialize the OpenCloseCapability object."""
        super().__init__(name=name, node_uuid=node_uuid, id=id)

    def __repr__(self) -> str:
        """Return a string representation of the OpenCloseCapability object."""
        return f"OpenCloseCapability(name={self.name}, node_uuid={self.node_uuid}, id={self.id})"

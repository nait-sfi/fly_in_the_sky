"""Zone entities and zone types for the simulation."""

from enum import Enum


class ZoneType(Enum):
    """Supported zone categories and their movement properties."""

    NORMAL = (1, False)
    RESTRICTED = (2, False)
    PRIORITY = (1, True)
    BLOCKED = (float('inf'), False)

    @property
    def cost(self) -> int | float:
        """Return the movement cost for the zone type."""
        return self.value[0]

    @property
    def is_priority(self) -> bool:
        """Return whether this type has tie-break priority."""
        return self.value[1]


class Zone:
    """Represents a traversable location in the map."""

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: ZoneType = ZoneType.NORMAL,
        max_capacity: int = 1,
        color: str | None = None,
    ) -> None:
        """
        Initialize a zone.

        Args:
            name: Zone identifier.
            x: Horizontal coordinate.
            y: Vertical coordinate.
            zone_type: Zone category affecting movement behavior.
            max_capacity: Maximum number of drones allowed simultaneously.
            color: Optional display color metadata.
        """
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.max_capacity = max_capacity
        self.neighbors: list[Zone] = []
        self.color = color
        self.current_drones: set[int] = set()
        self.passing_cost: float = 0

    def can_accept_drone(self) -> bool:
        """
        Check if this zone can accept another drone.

        Returns:
            True if there is available capacity, otherwise False.
        """
        return len(self.current_drones) < self.max_capacity

    def add_drone(self, drone_id: int) -> bool:
        """
        Add a drone to this zone

        Args:
            drone_id: The ID of the drone to add

        Returns:
            True if successful, otherwise False.
        """
        if self.can_accept_drone():
            self.current_drones.add(drone_id)
            return True
        return False

    def remove_drone(self, drone_id: int) -> None:
        """
        Remove a drone from this zone

        Args:
            drone_id: The ID of the drone to remove.
        """
        self.current_drones.discard(drone_id)

    def get_movement_priority(self) -> bool:
        """Return whether this zone gets tie-break movement priority."""
        return self.zone_type.is_priority

    def get_movement_cost(self) -> float:
        """
        Get the effective movement cost to enter this zone.

        Returns:
            Base zone type cost plus dynamic passing cost.
        """
        return self.zone_type.cost + self.passing_cost

    def __repr__(self) -> str:
        """Return a debug-friendly string representation."""
        return (
            f"Zone: name={self.name},(x:{self.x}, y:{self.y})" +
            f" capacity={self.max_capacity}")

    def __eq__(self, other: object) -> bool:
        """Return whether two zones share the same name."""
        if not isinstance(other, Zone):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        """Return a hash based on the zone name."""
        return hash(self.name)

"""Connection model between two zones."""

from Zone import Zone


class Connection:
    """Represents a bidirectional edge between two zones."""

    def __init__(self, zone1: Zone, zone2: Zone, max_capacity: int = 1):
        """
        Initialize a connection between two zones.

        Args:
            zone1: First zone.
            zone2: Second zone.
            max_capacity: Number of drones that can traverse per turn.
        """
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_capacity = max_capacity

        self.current_usage = 0

    def can_traverse(self) -> bool:
        """
        Check whether this connection has remaining capacity.

        Returns:
            True if a drone can traverse this turn, else False.
        """
        return self.max_capacity > self.current_usage

    def get_other_zone(self, current_zone: Zone) -> Zone | None:
        """
        Return the opposite endpoint from the given zone.

        Args:
            current_zone: Zone at one end of the connection.

        Returns:
            The other zone if ``current_zone`` belongs to this connection,
            otherwise ``None``.
        """
        if current_zone == self.zone1:
            return self.zone2
        elif current_zone == self.zone2:
            return self.zone1
        else:
            return None

    def __repr__(self) -> str:
        """Return a debug-friendly string representation."""
        return (
            f"Connection({self.zone1.name}↔{self.zone2.name}," +
            f" capacity={self.max_capacity})"
        )

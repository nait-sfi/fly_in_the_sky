from Zone import Zone


class Connection:
    def __init__(self, zone1: Zone, zone2: Zone, max_capacity: int = 1):
        """
        Create a bidirectional connection between two zones

        Args:
            zone1: First zone
            zone2: Second zone
            max_capacity: How many drones can use this path per turn
        """
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_capacity = max_capacity

        self.current_usage = 0

    def can_traverse(self) -> bool:
        """
        Check if this connection has capacity

        Returns:
            True if drones can use it, False if at max capacity
        """
        return self.max_capacity > self.current_usage

    def get_other_zone(self, current_zone: Zone) -> Zone | None:
        """
        Given one end of the connection, get the other end

        Args:
            current_zone: The zone you're currently at

        Returns:
            The zone on the other end
            or None

        Example:
            connection between A and B
            get_other_zone(A) returns B
            get_other_zone(B) returns A
            get_other_zone(X) returns None
        """
        if current_zone == self.zone1:
            return self.zone2
        elif current_zone == self.zone2:
            return self.zone1
        else:
            return None

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"Connection({self.zone1.name}↔{self.zone2.name}," +
            " capacity={self.max_capacity})"
        )

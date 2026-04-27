from enum import Enum


class ZoneType(Enum):
    NORMAL = (1, False)
    RESTRICTED = (2, False)
    PRIORITY = (1, True)
    BLOCKED = (float('inf'), False)

    @property
    def cost(self):
        return self.value[0]

    @property
    def is_priority(self):
        return self.value[1]


class Zone:
    def __init__(
        self, name, x, y, zone_type=ZoneType.NORMAL, max_capacity=1, color=None
         ) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.max_capacity = max_capacity
        self.neighbors = []
        self.color = color
        self.current_drones = set()

    def can_accept_drone(self) -> bool:
        """
        Check if this zone can accept another drone

        Returns:
            True if there's space, False if full
        """
        return len(self.current_drones) < self.max_capacity

    def add_drone(self, drone_id: int) -> bool:
        """
        Add a drone to this zone

        Args:
            drone_id: The ID of the drone to add

        Returns:
            True if successful, False if zone is full
        """
        if self.can_accept_drone():
            self.current_drones.add(drone_id)
            return True
        return False

    def remove_drone(self, drone_id: int) -> None:
        """
        Remove a drone from this zone

        Args:
            drone_id: The ID of the drone to remove
        """
        self.current_drones.discard(drone_id)

    def get_movement_priority(self) -> bool:
        return self.zone_type.is_priority

    def get_movement_cost(self) -> int | float:
        """
        Get the number of turns needed to reach this zone

        Returns:
            1 for normal/priority, 2 for restricted, inf for blocked
        """
        return self.zone_type.cost

    def __repr__(self) -> str:
        """
        String representation for debugging

        Returns:
            ..
        """
        # Make it show useful info!
        return (
            f"Zone: name={self.name},(x:{self.x}, y:{self.y})" +
            f" capacity={self.max_capacity}")

    def __eq__(self, other):
        """Two zones are equal if they have the same name"""
        if not isinstance(other, Zone):
            return False
        return self.name == other.name

    def __hash__(self):
        """Make Zone hashable (needed for sets, dicts)"""
        return hash(self.name)

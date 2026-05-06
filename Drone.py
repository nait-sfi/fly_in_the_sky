"""Drone domain model."""


class Drone:
    """Represents a drone moving through a precomputed path."""

    def __init__(
        self, drone_id: int, start_zone: str, path: list[str]
         ) -> None:
        """
        Initialize a drone.

        Args:
            drone_id: Unique drone identifier.
            start_zone: Initial zone name.
            path: Assigned path as an ordered list of zone names.
        """
        self.id = drone_id
        self.current_zone = start_zone
        self.assigned_path = path
        self.path_index = 0
        self.finished = False
        self.in_transi_to: str | None = None
        self.transit_turns_remaining: int = 0
        self.transit_connection_name: str | None = None
        self.transit_connection_key: tuple[str, str] | None = None

    def get_next_zone(self) -> str | None:
        """
        Get the next zone in the assigned path.

        Returns:
            Next zone name if available, otherwise ``None``.
        """
        if self.path_index < len(self.assigned_path) - 1:
            return self.assigned_path[self.path_index + 1]
        return None

    def move_to(self, zone_name: str) -> None:
        """
        Move the drone to the given zone and advance path state.

        Args:
            zone_name: Destination zone name.
        """
        self.current_zone = zone_name
        self.path_index += 1

        if self.path_index == len(self.assigned_path) - 1:
            self.finished = True

    def __repr__(self) -> str:
        """Return a debug-friendly string representation.

        Returns:
            str: Representation string for debuging
        """
        return (
            f"Drone(D{self.id},"
            + f" at={self.current_zone}, path_idx={self.path_index})"
        )

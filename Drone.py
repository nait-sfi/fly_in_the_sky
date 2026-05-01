from typing import List, Optional


class Drone:
    def __init__(self, drone_id: int, start_zone: str, path: List[str]):
        self.id = drone_id
        self.current_zone = start_zone
        self.assigned_path = path
        self.path_index = 0
        self.finished = False
        self.in_transi_to: Optional[str] = None
        self.transit_turns_remaining: int = 0

    def get_next_zone(self) -> Optional[str]:
        """Get next zone in assigned path"""
        if self.path_index < len(self.assigned_path) - 1:
            return self.assigned_path[self.path_index + 1]
        return None

    def move_to(self, zone_name: str) -> None:
        """Move to next zone"""
        self.current_zone = zone_name
        self.path_index += 1

        if self.path_index == len(self.assigned_path) - 1:
            self.finished = True

    def __repr__(self) -> str:
        return (
            f"Drone(D{self.id},"
            + f" at={self.current_zone}, path_idx={self.path_index})"
        )

    def is_at_goal(self) -> bool:
        """Check if drone reached destination"""
        return self.current_zone == self.assigned_path[-1]

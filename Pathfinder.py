"""Shortest path solver for the zone graph."""

from Graph import Graph
from typing import Dict
from Zone import Zone


class Pathfinder:
    """Compute delivery routes on top of a graph."""

    def __init__(self, graph: Graph) -> None:
        """
        Initialize the pathfinder from a graph.

        Args:
            graph: Graph containing zones and connection metadata.
        """
        self.zones: Dict[str, Zone] = graph.zones
        self.start_zone: str = graph.start_zone
        self.end_zone: str = graph.end_zone

    def solve(self) -> tuple[float, list[str]]:
        """
        Compute the shortest path from start zone to end zone.

        Returns:
            A tuple ``(distance, path)`` where distance is the movement cost
            and path is the ordered list of zone names.
        """
        inf_cost = float("inf")
        distances = {name: inf_cost for name in self.zones.keys()}
        distances[self.start_zone] = 0
        visited = {name: False for name in self.zones.keys()}
        paths = {name: [name] for name in self.zones.keys()}

        for _ in range(len(self.zones)):
            min_distance = inf_cost
            current = None
            for name in self.zones.keys():
                if not visited[name] and distances[name] < min_distance:
                    min_distance = distances[name]
                    current = name

            if current is None:
                break
            visited[current] = True

            for neighbor_zone in self.zones[current].neighbors:
                neighbor_name = neighbor_zone.name
                distance = neighbor_zone.get_movement_cost()

                if distance != inf_cost and not visited[neighbor_name]:
                    new_distance = distances[current] + distance

                    if (new_distance < distances[neighbor_name] or
                        (new_distance == distances[neighbor_name] and
                         neighbor_zone.get_movement_priority())):

                        distances[neighbor_name] = new_distance
                        paths[neighbor_name] = paths[current] + [neighbor_name]

        goal_distance = distances[self.end_zone]
        goal_path = paths.get(self.end_zone, [])

        return goal_distance, goal_path

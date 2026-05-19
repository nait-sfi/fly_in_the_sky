"""Shortest path solver for the zone graph."""

from Graph import Graph
from typing import Dict
from Zone import Zone
import heapq


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

        inf_cost = float('inf')
        distances = {name: inf_cost for name in self.zones}
        visited = set()
        paths = {name: [name] for name in self.zones}

        heap: list[tuple[float, int, str]] = []
        heapq.heappush(heap, (0, 0, self.start_zone))
        distances[self.start_zone] = 0
        while heap:
            _, _, node = heapq.heappop(heap)

            if node in visited:
                continue
            visited.add(node)

            for neighbor in self.zones[node].neighbors:
                if neighbor.name in visited:
                    continue

                neighbor_distance = neighbor.get_movement_cost()
                new_distance = neighbor_distance + distances[node]

                if (new_distance < distances[neighbor.name] or
                    (new_distance == distances[neighbor.name] and
                     neighbor.get_movement_priority())):

                    distances[neighbor.name] = new_distance
                    paths[neighbor.name] = paths[node] + [neighbor.name]
                    heapq.heappush(
                        heap,
                        (
                            distances[neighbor.name],
                            int(not neighbor.zone_type.is_priority),
                            neighbor.name,
                        ),
                    )
        path = paths.get(self.end_zone, [])
        distance = distances[self.end_zone]
        return distance, path

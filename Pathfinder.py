from Graph import Graph
from Zone import Zone
from typing import Optional, Dict, Tuple


class Pathfinder:
    def __init__(self, graph: Graph) -> None:
        self.zones: Dict[str, Zone] = graph.zones
        self.start_zone: str = graph.start_zone
        self.end_zone: str = graph.end_zone

    def get_zone(self, name: str) -> Optional[Zone]:
        return self.zones.get(name)

    def solve(self) -> Tuple[float, str]:
        INF = float('inf')
        distances = {name: INF for name in self.zones.keys()}
        distances[self.start_zone] = 0
        visited = {name: False for name in self.zones.keys()}
        paths = {name: [name] for name in self.zones.keys()}

        for _ in range(len(self.zones)):
            min_distance = INF
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

                if distance != INF and not visited[neighbor_name]:
                    new_distance = distances[current] + distance

                    if (new_distance < distances[neighbor_name] or
                        (new_distance == distances[neighbor_name] and
                         neighbor_zone.get_movement_priority())):

                        distances[neighbor_name] = new_distance
                        paths[neighbor_name] = paths[current] + [neighbor_name]

        goal_path = paths.get(self.end_zone, [])
        path = ' ==> '.join(goal_path)
        goal_distance = distances[self.end_zone]

        # self._print_result(goal_distance, path)

        return goal_distance, path

    def _print_result(self, distance: float, path: str) -> None:
        """Print pathfinding result nicely."""
        print(f"\n{'='*50}")
        print("Pathfinding Result")
        print(f"{'='*50}")
        print(f"From:     {self.start_zone}")
        print(f"To:       {self.end_zone}")
        print(f"Distance: {distance} turns")
        print(f"Path:     {path}")
        print(f"{'='*50}\n")

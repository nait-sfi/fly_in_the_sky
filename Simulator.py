"""Simulation engine for multi-drone delivery."""

from Drone import Drone
from Graph import Graph
from Pathfinder import Pathfinder
from Zone import ZoneType


class Simulator:
    """Simulates multi-drone delivery."""

    def __init__(self, graph: Graph, num_drones: int, pathfinder: Pathfinder) -> None:
        """
        Initialize a simulator.

        Args:
            graph: Graph containing zones and connections.
            num_drones: Number of drones to simulate.
            pathfinder: Pathfinding engine used to assign routes.
        """
        self.graph = graph
        self.num_drones = num_drones
        self.pathfinder = pathfinder
        self.drones: list[Drone] = []
        self.turn = 0
        self.output: list[str] = []

        self._create_drones()
        self._assign_paths()

    def _create_drones(self) -> None:
        """Create all drones at the start position."""
        for drone_id in range(1, self.num_drones + 1):
            self.drones.append(Drone(drone_id, self.graph.start_zone, []))

    def _assign_paths(self) -> None:
        """Assign paths to all drones and update zone passing costs."""
        for drone in self.drones:
            _, path = self.pathfinder.solve()
            for zone_name in path:
                zone = self.graph.zones[zone_name]
                zone.passing_cost += 1 / zone.zone_type.cost
            drone.assigned_path = path

    def can_drone_move(self, drone: Drone, next_zone_name: str) -> bool:
        """
        Check whether a drone can move to the requested zone.

        Args:
            drone: Drone to evaluate.
            next_zone_name: Destination zone name.

        Returns:
            True if both zone and connection constraints allow movement.
        """
        next_zone = self.graph.get_zone(next_zone_name)
        if next_zone is None or not next_zone.can_accept_drone():
            return False

        connection = self.graph.get_connection(drone.current_zone, next_zone_name)
        if connection is None or not connection.can_traverse():
            return False

        return True

    def move_drone(self, drone: Drone, next_zone_name: str) -> bool:
        """
        Move a drone to the next zone when possible.

        Args:
            drone: Drone to move.
            next_zone_name: Destination zone name.

        Returns:
            True if movement happened, otherwise False.
        """
        if not self.can_drone_move(drone, next_zone_name):
            return False

        old_zone_name = drone.current_zone
        old_zone = self.graph.get_zone(old_zone_name)
        next_zone = self.graph.get_zone(next_zone_name)
        connection = self.graph.get_connection(old_zone_name, next_zone_name)

        if old_zone is None or next_zone is None:
            return False

        old_zone.remove_drone(drone.id)
        if next_zone.zone_type == ZoneType.RESTRICTED:
            drone.in_transi_to = next_zone_name
            drone.transit_turns_remaining = 1
            if connection is not None:
                connection.current_usage += 1
            return True

        next_zone.add_drone(drone.id)
        drone.move_to(next_zone_name)
        if connection is not None:
            connection.current_usage += 1
        return True

    def simulate_turn(self) -> None:
        """Execute one simulation turn."""
        for connection in self.graph.connections.values():
            connection.current_usage = 0

        moves: list[str] = []
        for drone in self.drones:
            if drone.finished:
                continue

            if drone.in_transi_to is not None:
                drone.transit_turns_remaining -= 1
                if drone.transit_turns_remaining == 0:
                    destination_zone_name = drone.in_transi_to
                    destination_zone = self.graph.get_zone(destination_zone_name)
                    if destination_zone is None:
                        continue
                    destination_zone.add_drone(drone.id)
                    drone.move_to(destination_zone_name)
                    moves.append(f"D{drone.id}->{drone.current_zone}")
                    drone.in_transi_to = None
                    drone.transit_turns_remaining = 0
                else:
                    moves.append(f"D{drone.id}->{drone.in_transi_to}transit")
                continue

            next_zone = drone.get_next_zone()
            if next_zone is None:
                continue

            if self.move_drone(drone, next_zone):
                moves.append(f"D{drone.id}→{next_zone}")
            else:
                moves.append(f"D{drone.id}(wait)")

        if moves:
            self.output.append(f"Turn {self.turn + 1}: {', '.join(moves)}")

        self.turn += 1

    def run(self, max_turns: int = 1000) -> int:
        """
        Run simulation until all drones finish or max turns is reached.

        Args:
            max_turns: Safety cap to avoid infinite loops.

        Returns:
            Number of simulated turns.
        """
        while not all(drone.finished for drone in self.drones):
            if self.turn >= max_turns:
                print(f"❌ ERROR: Simulation exceeded {max_turns} turns!")
                print(
                    f"Drones finished: {sum(1 for drone in self.drones if drone.finished)}/"
                    f"{len(self.drones)}"
                )
                break
            self.simulate_turn()

        return self.turn

    def print_results(self) -> None:
        """Print simulation results."""
        print(f"\n{'=' * 50}")
        print("Simulation Results")
        print(f"{'=' * 50}")
        for line in self.output:
            print(line)
        print(f"\n All {self.num_drones} drones delivered in {self.turn} turns!")
        print(f"{'=' * 50}\n")

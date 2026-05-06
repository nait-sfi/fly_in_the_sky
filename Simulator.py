"""Simulation engine for multi-drone delivery."""

from Drone import Drone
from Graph import Graph
from Pathfinder import Pathfinder
from Zone import ZoneType


class Simulator:
    """Simulates multi-drone delivery."""

    def __init__(
        self, graph: Graph, num_drones: int, pathfinder: Pathfinder
         ) -> None:
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
        self.transit_reservations: dict[str, int] = {}

        self._create_drones()
        self._assign_paths()

    @staticmethod
    def _connection_key(zone1_name: str, zone2_name: str) -> tuple[str, str]:
        """Create a normalized key for a bidirectional connection."""
        return (
            (zone1_name, zone2_name)
            if zone1_name <= zone2_name
            else (zone2_name, zone1_name)
        )

    def _create_drones(self) -> None:
        """Create all drones at the start position."""
        start_zone = self.graph.get_zone(self.graph.start_zone)
        for drone_id in range(1, self.num_drones + 1):
            drone = Drone(drone_id, self.graph.start_zone, [])
            self.drones.append(drone)
            if start_zone is not None:
                start_zone.current_drones.add(drone.id)

    def _is_special_unbounded_zone(self, zone_name: str) -> bool:
        """Return whether zone has unlimited occupancy per rules."""
        return zone_name in (self.graph.start_zone, self.graph.end_zone)

    def _assign_paths(self) -> None:
        """Assign paths to all drones and update zone passing costs."""
        for drone in self.drones:
            _, path = self.pathfinder.solve()
            pathlen = len(path)
            for zone_name in path:
                self.graph.zones[zone_name].additional_cost += (0.1 / pathlen)
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
        if next_zone is None:
            return False

        connection = self.graph.get_connection(
            drone.current_zone, next_zone_name
            )
        if connection is None or not connection.can_traverse():
            return False

        if self._is_special_unbounded_zone(next_zone_name):
            return True

        projected_occupancy = (
            len(next_zone.current_drones)
            + self.transit_reservations.get(next_zone_name, 0)
        )
        return projected_occupancy < next_zone.max_capacity

    def move_drone(self, drone: Drone, next_zone_name: str) -> str | None:
        """
        Move a drone to the next zone when possible.

        Args:
            drone: Drone to move.
            next_zone_name: Destination zone name.

        Returns:
            Movement token if movement happened, otherwise ``None``.
        """
        if not self.can_drone_move(drone, next_zone_name):
            return None

        old_zone_name = drone.current_zone
        old_zone = self.graph.get_zone(old_zone_name)
        next_zone = self.graph.get_zone(next_zone_name)
        connection = self.graph.get_connection(old_zone_name, next_zone_name)

        if old_zone is None or next_zone is None:
            return None

        old_zone.remove_drone(drone.id)
        if next_zone.zone_type == ZoneType.RESTRICTED:
            drone.in_transi_to = next_zone_name
            drone.transit_turns_remaining = 1
            drone.transit_connection_name = f"{old_zone_name}-{next_zone_name}"
            drone.transit_connection_key = self._connection_key(
                old_zone_name, next_zone_name
            )
            if not self._is_special_unbounded_zone(next_zone_name):
                self.transit_reservations[next_zone_name] = (
                    self.transit_reservations.get(next_zone_name, 0) + 1
                )
            if connection is not None:
                connection.current_usage += 1
            return f"D{drone.id}-{drone.transit_connection_name}"

        next_zone.current_drones.add(drone.id)
        drone.move_to(next_zone_name)
        if connection is not None:
            connection.current_usage += 1
        return f"D{drone.id}-{next_zone_name}"

    def simulate_turn(self) -> None:
        """Execute one simulation turn."""
        for graph_connection in self.graph.connections.values():
            graph_connection.current_usage = 0

        for drone in self.drones:
            dron_is_none = drone.in_transi_to is None
            if dron_is_none or drone.transit_connection_key is None:
                continue
            transit_connection = self.graph.connections.get(
                drone.transit_connection_key
            )
            if transit_connection is not None:
                transit_connection.current_usage += 1

        moves: list[str] = []
        for drone in self.drones:
            if drone.finished:
                continue

            if drone.in_transi_to is not None:
                drone.transit_turns_remaining -= 1
                if drone.transit_turns_remaining == 0:
                    destination_zone_name = drone.in_transi_to
                    destination_zone = self.graph.get_zone(
                        destination_zone_name
                        )
                    if destination_zone is None:
                        raise RuntimeError(
                            f"Drone D{drone.id}" +
                            " has invalid transit destination"
                        )
                    if not self._is_special_unbounded_zone(
                        destination_zone_name
                         ):
                        reservation = self.transit_reservations.get(
                            destination_zone_name, 0
                             )
                        if reservation <= 0:
                            raise RuntimeError(
                                "Missing reservation for restricted transit to"
                                f" {destination_zone_name}"
                            )
                        self.transit_reservations[destination_zone_name] = \
                            reservation - 1
                        if self.transit_reservations[
                            destination_zone_name
                             ] == 0:
                            del self.transit_reservations[
                                destination_zone_name]

                    destination_zone.current_drones.add(drone.id)
                    drone.move_to(destination_zone_name)
                    moves.append(f"D{drone.id}-{drone.current_zone}")
                    drone.in_transi_to = None
                    drone.transit_turns_remaining = 0
                    drone.transit_connection_name = None
                    drone.transit_connection_key = None
                continue

            next_zone = drone.get_next_zone()
            if next_zone is None:
                continue

            movement = self.move_drone(drone, next_zone)
            if movement is not None:
                moves.append(movement)

        if moves:
            self.output.append(" ".join(moves))

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
                    "Drones finished:" +
                    f" {sum(1 for drone in self.drones if drone.finished)}/"
                    f"{len(self.drones)}"
                )
                break
            self.simulate_turn()

        return self.turn

    def print_results(self) -> None:
        """Print simulation results."""
        for line in self.output:
            print(line)

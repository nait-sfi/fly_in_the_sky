from typing import List  # , Optional
from Graph import Graph
from Pathfinder import Pathfinder
from Drone import Drone
from Zone import Zone, ZoneType


class Simulator:
    """Simulates multi-drone delivery"""

    def __init__(self, graph: Graph, num_drones: int, pathfinder: Pathfinder):
        self.graph = graph
        self.num_drones = num_drones
        self.pathfinder = pathfinder
        self.drones: List[Drone] = []
        self.turn = 0
        self.output: List[str] = []

        self._create_drones()
        self._assign_paths()

    def _create_drones(self) -> None:
        """Create all drones at start position"""
        for i in range(1, self.num_drones + 1):
            drone = Drone(i, self.graph.start_zone, [])
            self.drones.append(drone)

    def _assign_paths(self) -> None:
        """Assign path to each drone"""
        # Find optimal path
        _, path = self.pathfinder.solve()

        # Assign to all drones (for now, same path)
        for drone in self.drones:
            drone.assigned_path = path

    def can_drone_move(self, drone: Drone, next_zone_name: str) -> bool:
        """Check if drone can move to next zone"""
        # Check zone capacity
        next_zone = self.graph.get_zone(next_zone_name)
        if next_zone is None or not next_zone.can_accept_drone():
            return False

        # Check connection capacity
        connection = self.graph.get_connection(
            drone.current_zone, next_zone_name
            )
        if connection is None or not connection.can_traverse():
            return False

        return True

    def move_drone(self, drone: Drone, next_zone_name: str) -> bool:
        """Move drone to next zone"""

        if not self.can_drone_move(drone, next_zone_name):
            return False

        # SAVE old position BEFORE moving drone
        old_zone_name = drone.current_zone
        old_zone = self.graph.get_zone(old_zone_name)
        next_zone = self.graph.get_zone(next_zone_name)
        # Update connection BEFORE drone moves (use old position!)
        connection = self.graph.get_connection(old_zone_name, next_zone_name)

        if next_zone.zone_type ==ZoneType.RESTRICTED:
            # Remove from old zone
            old_zone.remove_drone(drone.id)
            drone.in_transi_to = next_zone_name
            drone.transit_turns_remaining = 1

            if connection:
                connection.current_usage += 1
            
            return True
        else:
            old_zone.remove_drone(drone.id)
            next_zone.add_drone(drone.id) 
            drone.move_to(next_zone_name)
            if connection:
                connection.current_usage += 1

            return True




    def simulate_turn(self) -> None:
        """Execute one simulation turn"""

        # IMPORTANT: Reset connection usage each turn!
        for connection in self.graph.connections.values():
            connection.current_usage = 0

        moves = []

        for drone in self.drones:
            if drone.finished:
                continue

            if drone.in_transi_to is not None:
                drone.transit_turns_remaining -= 1

                if drone.transit_turns_remaining == 0:
                    dest_zone = self.graph.get_zone(drone.in_transi_to)
                    dest_zone.add_drone(drone.id)
                    drone.move_to(drone.in_transi_to)

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
        Run simulation until all drones finished

        Args:
            max_turns: Maximum turns to prevent infinite loops

        Returns:
            Total number of turns taken
        """
        while not all(d.finished for d in self.drones):
            # Safety check
            if self.turn >= max_turns:
                print(f"❌ ERROR: Simulation exceeded {max_turns} turns!")
                print(f"Drones finished: {sum(1 for d in self.drones if d.finished)}/{len(self.drones)}")
                break

            self.simulate_turn()

        return self.turn

    def print_results(self) -> None:
        """Print simulation results"""
        print(f"\n{'='*50}")
        print("Simulation Results")
        print(f"{'='*50}")

        for line in self.output:
            print(line)

        print(
            f"\n All {self.num_drones} drones delivered in {self.turn} turns!"
            )
        print(f"{'='*50}\n")

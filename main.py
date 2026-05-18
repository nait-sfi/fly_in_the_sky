"""Entrypoint for running pathfinding on a sample map."""

from Graph import Graph
from Pathfinder import Pathfinder
from parser import MapParser
from Simulator import Simulator
from Path_not_found_error import PathNotFoundError


def main() -> None:
    """
    Parse a sample map and solve the route once.

    Raises:
        RuntimeError: If map parsing fails.
    """
    maps = [
        "maps/challenger/01_the_impossible_dream.txt",
        # "maps/easy/02_simple_fork.txt",
        # "maps/hard/01_maze_nightmare.txt",
        # "maps/hard/03_ultimate_challenge.txt",
        # "maps/medium/02_circular_loop.txt",
        # "maps/easy/01_linear_path.txt",
        # "maps/easy/03_basic_capacity.txt",
        # "maps/hard/02_capacity_hell.txt",
        # "maps/medium/01_dead_end_trap.txt",
        # "maps/medium/03_priority_puzzle.txt",
    ]
    for map in maps:
        try:
            parser = MapParser()
            if not parser.parse_file(map):
                raise RuntimeError("\n".join(parser.get_errors()), map)

            graph = Graph()
            graph.build_from_parser(parser)

            pathfinder = Pathfinder(graph)
            if parser.nb_drones is None:
                raise RuntimeError("nb_drones was not set after parsing")
            try:
                simulation = Simulator(graph, parser.nb_drones, pathfinder)
                simulation.run()
                simulation.print_results()
                print(simulation.get_number_truns())
            except PathNotFoundError as e:
                print(e)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()

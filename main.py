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
    try:
        parser = MapParser()
        if not parser.parse_file("./maps/easy/03_basic_capacity.txt"):
            raise RuntimeError("\n".join(parser.get_errors()))

        graph = Graph()
        graph.build_from_parser(parser)

        pathfinder = Pathfinder(graph)
        if parser.nb_drones is None:
            raise RuntimeError("nb_drones was not set after parsing")
        try:
            simulation = Simulator(graph, parser.nb_drones, pathfinder)
            simulation.run()
            simulation.print_results()
        except PathNotFoundError as e:
            print(e)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()

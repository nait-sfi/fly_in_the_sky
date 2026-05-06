"""Entrypoint for running pathfinding on a sample map."""

from Graph import Graph
from Pathfinder import Pathfinder
from parser import MapParser
from Simulator import Simulator


def main() -> None:
    """
    Parse a sample map and solve the route once.

    Raises:
        RuntimeError: If map parsing fails.
    """
    parser = MapParser()
    if not parser.parse_file("./maps/hard/01_maze_nightmare.txt"):
        raise RuntimeError("\n".join(parser.get_errors()))

    graph = Graph()
    graph.build_from_parser(parser)

    pathfinder = Pathfinder(graph)
    if parser.nb_drones is None:
        raise RuntimeError("nb_drones was not set after parsing")
    simulation = Simulator(graph, parser.nb_drones, pathfinder)
    simulation.run()
    print(len(simulation.output))
    # for input in simulation.output:
    #     print(input)


if __name__ == "__main__":
    main()

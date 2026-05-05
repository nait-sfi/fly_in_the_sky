"""Entrypoint for running pathfinding on a sample map."""

from Graph import Graph
from Pathfinder import Pathfinder
from parser import MapParser


def main() -> None:
    """
    Parse a sample map and solve the route once.

    Raises:
        RuntimeError: If map parsing fails.
    """
    parser = MapParser()
    if not parser.parse_file("./maps/medium/01_dead_end_trap.txt"):
        raise RuntimeError("\n".join(parser.get_errors()))

    graph = Graph()
    graph.build_from_parser(parser)

    pathfinder = Pathfinder(graph)
    pathfinder.solve()


if __name__ == "__main__":
    main()

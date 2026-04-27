from parser import MapParser
from Graph import Graph
from Pathfinder import Pathfinder

# Parse
parser = MapParser()
success = parser.parse_file("./maps/hard/03_ultimate_challenge.txt")

print("=== PARSER DEBUG ===")
print(f"Parse successful: {success}")
print(f"Errors: {parser.get_errors()}")
print(f"nb_drones: {parser.nb_drones}")
print(f"start_hub: {parser.start_hub}")
print(f"end_hub: {parser.end_hub}")
print(f"hubs: {list(parser.hubs.keys())}")
print(f"connections: {len(parser.connections)}")

# Build graph
graph = Graph()
graph.build_from_parser(parser)

print("\n=== GRAPH DEBUG ===")
print(f"Graph: {graph}")
print(f"Graph zones: {list(graph.zones.keys())}")
print(f"Graph start_zone: {graph.start_zone}")
print(f"Graph end_zone: {graph.end_zone}")

# Create pathfinder
print("\n=== PATHFINDER DEBUG ===")
pathfinder = Pathfinder(graph)
print(f"Pathfinder start_zone: {pathfinder.start_zone}")
print(f"Pathfinder end_zone: {pathfinder.end_zone}")
print(f"Pathfinder zones: {list(pathfinder.zones.keys())}")

# Solve
distance, path = pathfinder.solve()
print(f"\nDistance: {distance}")
print(f"Path: {path}")


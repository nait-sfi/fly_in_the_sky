*This project has been created as part of the 42 curriculum by noro66.*

# Fly-in the Sky

## Description

Fly-in the Sky is a Python simulation that routes multiple drones from one start hub to
one end hub on a graph of connected zones. The objective is to deliver all drones in the
fewest turns while respecting movement costs, per-zone capacity, and per-connection
capacity.

The project contains:
- A parser for the subject map format (`nb_drones`, `start_hub`, `end_hub`, `hub`,
  `connection`, metadata).
- A graph model (`Zone`, `Connection`, `Graph`) with zone types
  (`normal`, `priority`, `restricted`, `blocked`).
- A simulator that executes turn-by-turn moves and outputs drone movements.
- A pathfinder used to assign routes to drones.

## Instructions

### Prerequisites
- Python 3.10+ (project currently targets Python 3.13 in `pyproject.toml`)
- `uv` installed

### Install
```bash
make install
```

### Run
```bash
make run
```

### Debug
```bash
make debug
```

### Lint and type-check
```bash
make lint
```

Optional strict mode:
```bash
make lint-strict
```

### Clean caches
```bash
make clean
```

## Algorithm Choices and Implementation Strategy

The current strategy uses weighted shortest-path routing:
- Pathfinding computes a minimum-cost path from start to end based on zone movement
  cost (`normal=1`, `restricted=2`, `priority=1`, `blocked=infinite`).
- To avoid sending all drones on exactly the same path, an additional dynamic cost is
  incremented on zones used by previously assigned routes.
- During simulation, drones move in discrete turns with occupancy and traversal checks:
  - Zone capacity (`max_drones`) is enforced.
  - Connection capacity (`max_link_capacity`) is enforced per turn.
  - Start and end hubs accept any number of drones.
  - Restricted-zone transitions take 2 turns and keep the drone in transit on the
    connection until arrival.

This is a throughput-oriented heuristic approach, designed to stay valid under map
constraints while reducing global turn count.

## Visual Representation

Current visual output is terminal-based and focused on movement logs:
- Each line represents one simulation turn.
- Tokens use the required format (`D<ID>-<zone>` and transit token for restricted moves).

Zone color metadata is parsed and stored but not yet rendered as colored output in the
terminal. The next improvement is to map zone metadata colors to ANSI terminal colors for
a clearer visual simulation state.

## Resources

### Classic references
- Python documentation: https://docs.python.org/3/
- `typing` module: https://docs.python.org/3/library/typing.html
- `mypy` documentation: https://mypy.readthedocs.io/
- `flake8` documentation: https://flake8.pycqa.org/
- Dijkstra shortest path overview:
  https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm

### AI usage disclosure
AI was used as an assistant for:
- lint/type diagnostics and remediation suggestions,
- README structure drafting and wording improvement,
- checking requirement coverage against the project subject.

All generated suggestions were reviewed and adapted before integration.

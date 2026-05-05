"""Graph representation of zones and their connections."""

from typing import Any
from Zone import Zone
from Connection import Connection
from parser import MapParser
from Zone import ZoneType


class Graph:
    """Stores zones, links, and start/end hubs for routing."""

    def __init__(self) -> None:
        """Initialize an empty graph."""
        self.zones: dict[str, Zone] = {}
        self.connections: dict[tuple[str, str], Connection] = {}
        self.start_zone: str = ""
        self.end_zone: str = ""

    def add_zone(self, zone: Zone) -> None:
        """
        Add a zone to the graph.

        Args:
            zone: The zone to add.
        """
        self.zones[zone.name] = zone

    def add_connection(
        self,
        zone1_name: str,
        zone2_name: str,
        max_capacity: int = 1,
    ) -> None:
        """
        Create a bidirectional connection between two zones.

        Args:
            zone1_name: Name of the first zone.
            zone2_name: Name of the second zone.
            max_capacity: Connection traversal capacity per turn.

        Raises:
            ValueError: If either zone name does not exist in the graph.
        """
        zone1: Zone | None = self.zones.get(zone1_name)
        zone2: Zone | None = self.zones.get(zone2_name)

        if zone1 is None:
            raise ValueError(f"Zone '{zone1_name}' not found in graph")
        if zone2 is None:
            raise ValueError(f"Zone '{zone2_name}' not found in graph")

        zone1.neighbors.append(zone2)
        zone2.neighbors.append(zone1)
        conn = Connection(zone1, zone2, max_capacity)
        key = tuple(sorted((zone1_name, zone2_name)))
        self.connections[key] = conn

    def get_neighbors(self, zone_name: str) -> list[Zone]:
        """
        Get all neighboring zones for the given zone.

        Args:
            zone_name: Name of the zone.

        Returns:
            Neighboring zones, or an empty list if the zone does not exist.
        """
        zone = self.zones.get(zone_name)
        if zone:
            return zone.neighbors
        return []

    @staticmethod
    def string_to_zone_type(zone_str: str) -> ZoneType:
        """
        Convert a textual zone type to ``ZoneType``.

        Args:
            zone_str: Zone type string from map metadata.

        Returns:
            Matching zone type, defaulting to ``ZoneType.NORMAL``.
        """
        zone_map = {
            'normal': ZoneType.NORMAL,
            'restricted': ZoneType.RESTRICTED,
            'priority': ZoneType.PRIORITY,
            'blocked': ZoneType.BLOCKED
        }
        return zone_map.get(zone_str.lower(), ZoneType.NORMAL)

    def build_from_parser(self, parser: MapParser) -> None:
        """
        Populate the graph from a parsed map.

        Args:
            parser: Parser containing hubs, connections, and metadata.
        """
        for hub, hub_data in parser.hubs.items():
            typed_hub_data: dict[str, Any] = hub_data
            hub_metadata = typed_hub_data.get('metadata', {})
            zone = Zone(hub, hub_data['x'], hub_data['y'],
                        self.string_to_zone_type(
                            (hub_metadata.get('zone', 'normal')
                             )),
                        hub_metadata.get('max_drones', 1))
            self.zones[hub] = zone

        self.start_zone = parser.start_hub
        self.end_zone = parser.end_hub

        for conn in parser.connections:
            conn_metadata = conn.get('metadata', {})
            max_link_cap = conn_metadata.get('max_link_capacity', 1)
            self.add_connection(conn['zone1'], conn['zone2'], max_link_cap)

    def get_zone(self, zone_name: str) -> Zone | None:
        """
        Get a zone by name.

        Args:
            zone_name: Zone name.

        Returns:
            Zone object if found, otherwise ``None``.
        """
        return self.zones.get(zone_name)

    def has_zone(self, zone_name: str) -> bool:
        """
        Check whether a zone exists.

        Args:
            zone_name: Name to check.

        Returns:
            True if the zone exists, else False.
        """
        return zone_name in self.zones

    def get_start_zone(self) -> Zone | None:
        """
        Get the start zone object.

        Returns:
            The start zone if configured, otherwise ``None``.
        """
        if self.start_zone:
            return self.zones.get(self.start_zone)
        return None

    def get_end_zone(self) -> Zone | None:
        """
        Get the destination zone object.

        Returns:
            The end zone if configured, otherwise ``None``.
        """
        if self.end_zone:
            return self.zones.get(self.end_zone)
        return None

    def get_connection(
        self,
        zone1_name: str,
        zone2_name: str,
    ) -> Connection | None:
        """
        Get the connection between two zones, if present.

        Args:
            zone1_name: First zone name.
            zone2_name: Second zone name.

        Returns:
            The connection object or ``None``.
        """
        key = tuple(sorted((zone1_name, zone2_name)))
        return self.connections.get(key)


    def __repr__(self) -> str:
        """Return a debug-friendly string representation."""
        return (
            f"Graph({len(self.zones)} zones," +
            f" {len(self.connections)} connections)"
            )

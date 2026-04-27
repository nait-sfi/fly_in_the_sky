from typing import Dict, List, Optional
from Zone import Zone, ZoneType
from Connection import Connection
from parser import MapParser


class Graph:
    def __init__(self):
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []  # Store all connections
        self.start_zone: Optional[str] = None  # Store name, not object
        self.end_zone: Optional[str] = None

    def add_zone(self, zone: Zone) -> None:
        """
        Add a zone to the graph

        Args:
            zone: The Zone object to add
        """
        self.zones[zone.name] = zone

    def add_connection(
         self, zone1_name: str, zone2_name: str, max_capacity: int = 1
         ) -> None:
        """
        Create a bidirectional connection between two zones

        Args:
            zone1_name: Name of first zone
            zone2_name: Name of second zone
            max_capacity: Connection capacity
        """
        zone1: Zone = self.zones.get(zone1_name)
        zone2: Zone = self.zones.get(zone2_name)

        if zone1 is None:
            raise ValueError(f"Zone '{zone1_name}' not found in graph")
        if zone2 is None:
            raise ValueError(f"Zone '{zone2_name}' not found in graph")

        zone1.neighbors.append(zone2)
        zone2.neighbors.append(zone1)
        conn = Connection(zone1, zone2, max_capacity)
        self.connections.append(conn)

    def get_neighbors(self, zone_name: str) -> List[Zone]:
        """
        Get all zones connected to this zone

        Args:
            zone_name: Name of the zone

        Returns:
            List of neighboring Zone objects
        """
        zone = self.zones.get(zone_name)
        if zone:
            return zone.neighbors
        return []

    @staticmethod
    def string_to_zone_type(zone_str: str) -> ZoneType:
        """Convert string to ZoneType enum"""
        zone_map = {
            'normal': ZoneType.NORMAL,
            'restricted': ZoneType.RESTRICTED,
            'priority': ZoneType.PRIORITY,
            'blocked': ZoneType.BLOCKED
        }
        return zone_map.get(zone_str.lower(), ZoneType.NORMAL)

    def build_from_parser(self, parser: MapParser) -> None:
        """
        Build the graph from parsed data

        Args:
            parser: The MapParser object with parsed data
        """
        for hub, hub_data in parser.hubs.items():
            hub_metadata = hub_data.get('metadata', {})
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

    def get_zone(self, zone_name: str) -> Optional[Zone]:
        """
        Get a zone by name

        Args:
            zone_name: Name of the zone

        Returns:
            Zone object or None if not found
        """
        return self.zones.get(zone_name)

    def has_zone(self, zone_name: str) -> bool:
        """
        Check if a zone exists

        Args:
            zone_name: Name to check

        Returns:
            True if zone exists, False otherwise
        """
        return zone_name in self.zones

    def get_start_zone(self) -> Optional[Zone]:
        """Get the start zone object"""
        if self.start_zone:
            return self.zones.get(self.start_zone)
        return None

    def get_end_zone(self) -> Optional[Zone]:
        """Get the end zone object"""
        if self.end_zone:
            return self.zones.get(self.end_zone)
        return None

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"Graph({len(self.zones)} zones," +
            f" {len(self.connections)} connections)"
            )

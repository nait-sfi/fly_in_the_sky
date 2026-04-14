from typing import Dict, List, Any, Optional


class MapParser:
    def __init__(self) -> None:
        self.nb_drones: Optional[int] = None
        self.hubs: Dict[str, Dict[str, Any]] = {}
        self.connections: List[Dict[str, Any]] = []
        self.start_hub: str = ''
        self.end_hub: str = ''
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def parse_file(self, filename: str) -> bool:
        try:
            with open(filename, "r") as file:
                line_counter = 0
                for line_num, line in enumerate(file.readlines(), 1):
                    try:
                        self.parse_line(line, line_counter)
                    except Exception as e:
                        self.errors.append(f'Line {line_num}: {e}')
        except FileNotFoundError:
            self.errors.append(f"File not found: {filename}")
            return False

        if not self.errors:
            self.validate()

        return not self.has_errors()

    def parse_line(self, line: str, line_counter: int) -> bool:
        if not line.strip() or line.startswith('#'):
            line_counter = 0
            return False
        elif line.startswith("nb_drones"):
            return self.parse_nb_drones(line, line_counter)
        elif line.startswith(('start_hub:', 'end_hub:', 'hub:')):
            line_counter += 1
            return self.parse_hub(line)
        elif line.startswith('connection'):
            line_counter += 1
            return self.parse_connection(line)
        return False

    def parse_nb_drones(self, line: str, line_counter: int) -> bool:
        """
        Parse the nb_drones line to extract the number of drones.

        Args:
            line (str): The line containing nb_drones definition

        Returns:
            bool: True if parsing succeeded

        Raises:
            ValueError: If the format is invalid
            or value is not a positive integer
        """
        if ':' not in line:
            raise ValueError(f"Invalid hub line (no colon): {line}")

        prefix, content = line.split(':', 1)
        content = content.strip()
        if self.nb_drones is not None:
            self.warnings.append(
                    f"Warning: nb_drones already defined as {self.nb_drones}" +
                    " Ignoring new value."
                )
            return True
        if line_counter != 0:
            raise ValueError(
                    "nb_drones should be at the first line"
                    )
        try:
            value = int(content)
        except ValueError:
            raise ValueError(
                f"Expected number drones to be an int: {content}"
            )
        if value <= 0:
            raise ValueError(
                    f"nb_drones must be a positive integer, got: {value}"
                    )
        self.nb_drones = value
        return True

    def parse_hub(self, line: str) -> bool:
        """
        Parse a hub line with optional metadata

        Example: "hub: warehouse 0 0 [zone=restricted]"
        """
        if ':' not in line:
            raise ValueError(f"Invalid hub line (no colon): {line}")

        prefix, content = line.split(':', 1)
        content = content.strip()

        parts = content.split()

        if len(parts) < 3:
            raise ValueError(f"Hub line needs name, x, y: {line}")

        name = parts[0]
        if '-' in name or ' ' in name:
            raise ValueError(
                f"Zone names cannot contain dashes or spaces: '{name}'"
                )

        if name in self.hubs:
            raise ValueError(f"Duplicate hub name: '{name}' already defined")

        try:
            x = int(parts[1])
            y = int(parts[2])
        except ValueError:
            raise ValueError(f"Coordinates must be integers: {line}")

        metadata = self.extract_metadata(content)
        zone_type = metadata.get('zone', 'normal')
        metadata['color'] = metadata.get('color', None)
        metadata['max_drones'] = metadata.get('max_drones', 1)
        valid_types = ['normal', 'blocked', 'restricted', 'priority']
        if zone_type not in valid_types:
            raise ValueError(
                f"Invalid zone type: '{zone_type}'." +
                f" Must be one of: {', '.join(valid_types)}"
            )
        metadata['zone'] = zone_type
        match prefix.strip():
            case "start_hub":
                self.start_hub = name
            case 'end_hub':
                self.end_hub = name
        self.hubs[name] = {
            'x': x,
            'y': y,
            'metadata': metadata
        }
        return True

    def parse_connection(self, line: str) -> bool:
        """
        Parse a connection line with optional metadata

        Example: "connection: A-B [max_link_capacity=2]"
        """
        if ':' not in line:
            raise ValueError(f"Invalid connection line: {line}")

        prefix, content = line.split(':', 1)
        content = content.strip()

        if '[' in content:
            zones_part = content[:content.index('[')].strip()
        else:
            zones_part = content

        if '-' not in zones_part:
            raise ValueError(f"Connection needs two zones with -: {line}")

        zones = zones_part.split('-')

        if len(zones) != 2:
            raise ValueError(f"Connection needs exactly 2 zones: {line}")

        zone1 = zones[0].strip()
        zone2 = zones[1].strip()

        metadata = self.extract_metadata(content)
        metadata['max_link_capacity'] = metadata.get('max_link_capacity', 1)
        self.connections.append({
            'zone1': zone1,
            'zone2': zone2,
            'metadata': metadata
        })
        return True

    def extract_metadata(self, text: str) -> Dict:
        """
        Extract metadata from [key=value key2=value2] format

        Args:
            text: String that may contain [...] metadata

        Returns:
            Dictionary of metadata, or empty dict if no metadata
        """
        if '[' not in text or ']' not in text:
            return {}

        start = text.index('[')
        end = text.index(']')
        metadata_str = text[start+1:end].strip()

        if not metadata_str:
            return {}

        items = metadata_str.split()
        metadata = {k: v for k, v in (item.split('=') for item in items)}
        if 'max_drones' in metadata:
            try:
                val = int(metadata['max_drones'])
                if val <= 0:
                    raise ValueError(
                        f"max_drones must be positive, got: {val}"
                        )
            except ValueError:
                raise ValueError("max_drones must be an integer," +
                                 f" got: {metadata['max_drones']}")
        if 'max_link_capacity' in metadata:
            try:
                val = int(metadata['max_link_capacity'])
                if val <= 0:
                    raise ValueError(
                        f"max_link_capacity must be positive, got: {val}"
                        )
            except ValueError:
                raise ValueError(
                    "max_link_capacity must be an integer, got:" +
                    f" {metadata['max_link_capacity']}"
                    )
        return metadata

    def validate(self) -> None:
        if self.nb_drones is None:
            self.errors.append("Missing nb_drones")

        if not self.start_hub:
            self.errors.append("Missing start_hub")

        if not self.end_hub:
            self.errors.append("Missing end_hub")

        if self.start_hub and self.start_hub not in self.hubs:
            self.errors.append(f"start_hub '{self.start_hub}' not defined")

        if self.end_hub and self.end_hub not in self.hubs:
            self.errors.append(f"end_hub '{self.end_hub}' not defined")

        seen_connections = set()
        for conn in self.connections:
            z1, z2 = conn['zone1'], conn['zone2']
            if z1 not in self.hubs:
                self.errors.append(
                    f"Connection references unknown zone: {z1}"
                    )
            if z2 not in self.hubs:
                self.errors.append(
                    f"Connection references unknown zone: {z2}"
                    )
            pair = tuple(sorted([z1, z2]))
            if pair in seen_connections:
                self.errors.append(
                    f"Duplicate connection: {z1}-{z2}"
                )
            seen_connections.add(pair)

    def get_errors(self) -> List[str]:
        """Return all errors found"""
        return self.errors

    def has_errors(self) -> bool:
        """Check if any errors occurred"""
        return len(self.errors) > 0

    def get_warnings(self) -> List[str]:
        """Return all warnings found"""
        return self.warnings

    def has_warnings(self) -> bool:
        """Check if any warnings occurred"""
        return len(self.warnings) > 0


parser = MapParser()
result = parser.parse_file("test_warnings.txt")

print(f"Parse successful: {result}")
print(f"Final nb_drones: {parser.nb_drones}")
print(f"\n⚠️ Warnings: {len(parser.get_warnings())}")
for error in parser.get_errors():
    print(f"  - {error}")

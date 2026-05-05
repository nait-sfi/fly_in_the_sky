"""Parser for map definition files used by the simulator."""

from typing import Any


class MapParser:
    """Parses drone routing maps into hubs, links, and metadata."""

    def __init__(self) -> None:
        """Initialize parser state containers."""
        self.nb_drones: int | None = None
        self.hubs: dict[str, dict[str, Any]] = {}
        self.connections: list[dict[str, Any]] = []
        self.start_hub: str = ""
        self.end_hub: str = ""
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def parse_file(self, filename: str) -> bool:
        """
        Parse a map file and validate it.

        Args:
            filename: Path to the map file.

        Returns:
            True when parsing and validation complete without errors.
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                for line_num, line in enumerate(file.readlines(), 1):
                    try:
                        self.parse_line(line)
                    except Exception as exc:
                        self.errors.append(f"Line {line_num}: {exc}")
        except FileNotFoundError:
            self.errors.append(f"File not found: {filename}")
            return False
        except IsADirectoryError:
            self.errors.append(f"[Errno 21] Is a directory: {filename}")
            return False
        except Exception as exc:
            self.errors.append(str(exc))
            return False

        if not self.errors:
            self.validate()
        return not self.has_errors()

    def parse_line(self, line: str) -> bool:
        """
        Parse a single map line.

        Args:
            line: Raw line content.

        Returns:
            True if the line contains parsed content, otherwise False.
        """
        stripped = line.split("#", 1)[0].strip()
        if not stripped or stripped.startswith("#"):
            return False
        if stripped.startswith("nb_drones"):
            return self.parse_nb_drones(stripped)
        if stripped.startswith(("start_hub:", "end_hub:", "hub:")):
            return self.parse_hub(stripped)
        if stripped.startswith("connection"):
            return self.parse_connection(stripped)
        return False

    def parse_nb_drones(self, line: str) -> bool:
        """
        Parse the ``nb_drones`` declaration.

        Args:
            line: Line containing the drones count.

        Returns:
            True if parsing succeeded.

        Raises:
            ValueError: If the declaration format or value is invalid.
        """
        if ":" not in line:
            raise ValueError(f"Invalid hub line (no colon): {line}")

        _, content = line.split(":", 1)
        content = content.strip()

        if self.nb_drones is not None:
            self.warnings.append(
                f"Warning: nb_drones already defined as {self.nb_drones}"
                " Ignoring new value."
            )
            return True

        try:
            value = int(content)
        except ValueError as exc:
            raise ValueError(f"Expected number drones to be an int: {content}") from exc

        if value <= 0:
            raise ValueError(f"nb_drones must be a positive integer, got: {value}")

        self.nb_drones = value
        return True

    def parse_hub(self, line: str) -> bool:
        """
        Parse a hub declaration with optional metadata.

        Args:
            line: Hub definition line.

        Returns:
            True if parsing succeeded.

        Raises:
            ValueError: If syntax, coordinates, or metadata are invalid.
        """
        if ":" not in line:
            raise ValueError(f"Invalid hub line (no colon): {line}")

        prefix, content = line.split(":", 1)
        content = content.strip()
        parts = content.split()

        if len(parts) < 3:
            raise ValueError(f"Hub line needs name, x, y: {line}")

        name = parts[0]
        if "-" in name or " " in name:
            raise ValueError(f"Zone names cannot contain dashes or spaces: '{name}'")
        if name in self.hubs:
            raise ValueError(f"Duplicate hub name: '{name}' already defined")

        try:
            x = int(parts[1])
            y = int(parts[2])
        except ValueError as exc:
            raise ValueError(f"Coordinates must be integers: {line}") from exc

        metadata = self.extract_metadata(content)
        zone_type = metadata.get("zone", "normal")
        metadata["color"] = metadata.get("color", None)
        metadata["max_drones"] = metadata.get("max_drones", 1)

        valid_types = ["normal", "blocked", "restricted", "priority"]
        if zone_type not in valid_types:
            raise ValueError(
                f"Invalid zone type: '{zone_type}'. Must be one of: {', '.join(valid_types)}"
            )

        metadata["zone"] = zone_type
        match prefix.strip():
            case "start_hub":
                if self.start_hub:
                    raise ValueError(
                        f"Duplicate start_hub declaration: '{self.start_hub}' and '{name}'"
                    )
                self.start_hub = name
            case "end_hub":
                if self.end_hub:
                    raise ValueError(
                        f"Duplicate end_hub declaration: '{self.end_hub}' and '{name}'"
                    )
                self.end_hub = name

        self.hubs[name] = {"x": x, "y": y, "metadata": metadata}
        return True

    def parse_connection(self, line: str) -> bool:
        """
        Parse a connection declaration with optional metadata.

        Args:
            line: Connection definition line.

        Returns:
            True if parsing succeeded.

        Raises:
            ValueError: If the connection syntax is invalid.
        """
        if ":" not in line:
            raise ValueError(f"Invalid connection line: {line}")

        _, content = line.split(":", 1)
        content = content.strip()

        zones_part = content[:content.index("[")].strip() if "[" in content else content
        if "-" not in zones_part:
            raise ValueError(f"Connection needs two zones with -: {line}")

        zones = zones_part.split("-")
        if len(zones) != 2:
            raise ValueError(f"Connection needs exactly 2 zones: {line}")

        zone1 = zones[0].strip()
        zone2 = zones[1].strip()

        metadata = self.extract_metadata(content)
        metadata["max_link_capacity"] = metadata.get("max_link_capacity", 1)
        self.connections.append({"zone1": zone1, "zone2": zone2, "metadata": metadata})
        return True

    def extract_metadata(self, text: str) -> dict[str, Any]:
        """
        Extract metadata in ``[key=value key2=value2]`` format.

        Args:
            text: Line segment containing optional metadata.

        Returns:
            Parsed metadata dictionary, or an empty dict.

        Raises:
            ValueError: If numeric metadata values are invalid.
        """
        if "[" not in text or "]" not in text:
            return {}

        start = text.index("[")
        end = text.index("]")
        metadata_str = text[start + 1 : end].strip()
        if not metadata_str:
            return {}

        items = metadata_str.split()
        metadata: dict[str, Any] = {}
        for item in items:
            if "=" not in item:
                raise ValueError(
                    f"Invalid metadata item '{item}'. Expected key=value format"
                )
            key, value = item.split("=", 1)
            if not key or not value:
                raise ValueError(
                    f"Invalid metadata item '{item}'. Expected key=value format"
                )
            metadata[key] = value

        if "max_drones" in metadata:
            try:
                val = int(metadata["max_drones"])
                if val <= 0:
                    raise ValueError(f"max_drones must be positive, got: {val}")
            except ValueError as exc:
                raise ValueError(
                    f"max_drones must be an integer, got: {metadata['max_drones']}"
                ) from exc
            metadata["max_drones"] = val

        if "max_link_capacity" in metadata:
            try:
                val = int(metadata["max_link_capacity"])
                if val <= 0:
                    raise ValueError(f"max_link_capacity must be positive, got: {val}")
            except ValueError as exc:
                raise ValueError(
                    "max_link_capacity must be an integer, got:"
                    f" {metadata['max_link_capacity']}"
                ) from exc
            metadata["max_link_capacity"] = val

        return metadata

    def validate(self) -> None:
        """Validate parsed map data consistency."""
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

        seen_connections: set[tuple[str, str]] = set()
        for conn in self.connections:
            zone1, zone2 = conn["zone1"], conn["zone2"]
            if zone1 not in self.hubs:
                self.errors.append(f"Connection references unknown zone: {zone1}")
            if zone2 not in self.hubs:
                self.errors.append(f"Connection references unknown zone: {zone2}")

            pair = tuple(sorted((zone1, zone2)))
            if pair in seen_connections:
                self.errors.append(f"Duplicate connection: {zone1}-{zone2}")
            seen_connections.add(pair)

    def get_errors(self) -> list[str]:
        """
        Get parse errors.

        Returns:
            Collected parse and validation errors.
        """
        return self.errors

    def has_errors(self) -> bool:
        """
        Check whether any parse errors exist.

        Returns:
            True if errors are present, else False.
        """
        return len(self.errors) > 0

    def get_warnings(self) -> list[str]:
        """
        Get parse warnings.

        Returns:
            Collected non-fatal warnings.
        """
        return self.warnings

    def has_warnings(self) -> bool:
        """
        Check whether any warnings exist.

        Returns:
            True if warnings are present, else False.
        """
        return len(self.warnings) > 0

    def __str__(self) -> str:
        """Return a readable summary of parser state."""
        return (
            f"drones number: {self.nb_drones} "
            f"start: {self.start_hub} "
            f"end: {self.end_hub} "
            f"hubs: {self.hubs} "
            f"connections: {self.connections}"
        )

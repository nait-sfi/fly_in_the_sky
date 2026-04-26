from enum import Enum


class ZoneType(Enum):
    NORMAL = (1, False)
    RESTRICTED = (2, False)
    PRIORITY = (1, True)
    BLOCKER = (float('inf'), False)

    @property
    def cost(self):
        return self.value[0]

    @property
    def is_priority(self):
        return self.value[1]


class Zone:
    def __init__(
        self, name, x, y, zone_type=ZoneType.NORMAL, max_capacity=1, color=None
         ) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.max_capacity = max_capacity
        self.neighbors = []
        self.color = color
        self.current_drones = set()

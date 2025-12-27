from osmposter.layer.base import LayerBase

COLOR_DEFAULT = (1, 0.76, 0)

class LayerStreets(LayerBase):
    def __init__(self, options):
        self.only_main_streets = options.get("only_main_streets", False)
        self.color = tuple(options.get("color", COLOR_DEFAULT))
        self.HIGHWAYS = {
            "motorway": (self.color, 6),
            "motorway_link": (self.color, 6),
            "motorway_junction": (self.color, 6),
            "trunk": (self.color, 6),
            "trunk_link": (self.color, 6),
            "primary": (self.color, 6),
            "primary_link": (self.color, 4),
            "secondary": (self.color, 4),
            "secondary_link": (self.color, 4),
            "tertiary": (self.color, 3),
            "unclassified": (self.color, 3),
            "residential": (self.color, 2),
            "pedestrian": (self.color, 2),
            "living_street": (self.color, 2),
        }
        self.TRACKTYPES = {
            None: (self.color, 1),
            "grade1": (self.color, 1),
            "grade2": (self.color, 1),
            "grade3": (self.color, 1),
            "grade4": (self.color, 1),
        }

    # returns tuple(color, width)
    def get_pencil_for_way(self, way):
        if way.tags.get("area") == "yes":
            return None
        if self.only_main_streets:
            return self.HIGHWAYS.get(way.tags.get("highway"))
        highway = way.tags.get("highway")
        if highway is None:
            return None
        pencil = self.HIGHWAYS.get(highway)
        if pencil is None:
            access = way.tags.get("access")
            if access == "private":
                return None
            if highway == "track":
                return self.TRACKTYPES.get(way.tags.get("tracktype"))
            if highway == "service" \
                and ("service" not in way.tags) \
                and (access is None):
                return (self.color, 1)
        return pencil
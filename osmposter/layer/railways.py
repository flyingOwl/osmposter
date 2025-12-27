from osmposter.layer.base import LayerBase

COLOR_DEFAULT = (1, 0.76, 0)

class LayerRailways(LayerBase):
    def __init__(self, options):
        self.only_main_streets = options.get("only_main_streets", False)
        self.color = tuple(options.get("color", COLOR_DEFAULT))
        self.RAILWAY = {"light_rail", "rail", "subway", "tram", "narrow_gauge"}
        self.MINOR_SERVICE = {"yard", "siding"}
        self.MAIN_USAGE = {"main", "branch"}

    # returns tuple(color, width)
    def get_pencil_for_way(self, way):
        if way.tags.get("area") == "yes":
            return None
        railway = way.tags.get("railway")
        if railway in self.RAILWAY:
            if way.tags.get("service") in self.MINOR_SERVICE:
                return (self.color, 2)
            if railway == "tram":
                return (self.color, 4)
            if way.tags.get("usage") not in self.MAIN_USAGE:
                return (self.color, 2)
            return (self.color, 6)
        return None
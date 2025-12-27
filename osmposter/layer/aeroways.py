from osmposter.layer.base import LayerBase

COLOR_DEFAULT = (1, 0.76, 0)

class LayerAreoways(LayerBase):
    def __init__(self, options):
        self.include_abandoned = options.get("include_abandoned", False)
        self.color = tuple(options.get("color", COLOR_DEFAULT))
        self.AEROWAYS = {
            "taxiway": (self.color, 2),
            "runway": (self.color, 8),
        }
        self.ABANDONED = {
            "taxiway": (self.color, 2),
            "runway": (self.color, 2),
        }

    # returns tuple(color, width)
    def get_pencil_for_way(self, way):
        if way.tags.get("area") == "yes":
            return None
        if self.include_abandoned and "abandoned:aeroway" in way.tags:
            return self.ABANDONED.get(way.tags["abandoned:aeroway"])
        return self.AEROWAYS.get(way.tags.get("aeroway"))
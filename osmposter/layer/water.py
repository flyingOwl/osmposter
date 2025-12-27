from osmposter.layer.base import LayerBase

COLOR_DEFAULT = (0.03, 0.23, 0.72)

class LayerWater(LayerBase):
    def __init__(self, options):
        self.color = options.get("color", COLOR_DEFAULT)
        self.WATERWAYS = {
            "stream": (self.color, 1),
            "ditch": None,
            "drain": None,
            "boatyard": None,
        }
        self.NATURALS = {
            "water",
            "bay",
        }

    # returns tuple(color, width)
    def get_pencil_for_way(self, way):
        if "waterway" in way.tags:
            return self.WATERWAYS.get(way.tags["waterway"], (self.color, 2))
        return None

    # returns color
    def get_color_for_area(self, area):
        if area.tags.get("natural") in self.NATURALS:
            return self.color
        return None
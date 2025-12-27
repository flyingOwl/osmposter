from osmposter.layer.base import LayerBase

COLOR_DEFAULT = (1, 0.76, 0)

class LayerBuildings(LayerBase):
    def __init__(self, options):
        self.color = options.get("color", COLOR_DEFAULT)

    # returns color
    def get_color_for_area(self, area):
        if "building" in area.tags \
            and area.tags["building"] != "construction":
            return self.color
        return None
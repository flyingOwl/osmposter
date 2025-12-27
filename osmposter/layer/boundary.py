from osmposter.layer.base import LayerBase

COLOR_DEFAULT = (1, 1, 1)

class LayerBoundary(LayerBase):
    def __init__(self, options):
        self.id_set = set(options.get("ids", []))
        self.color = options.get("color", COLOR_DEFAULT)

    # returns color
    def get_color_for_area(self, area):
        if area.orig_id() in self.id_set:
            return self.color
        return None
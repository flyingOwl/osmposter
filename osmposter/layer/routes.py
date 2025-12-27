from osmposter.layer.base import LayerBase

COLOR_DEFAULT = (1, 1, 1)
WIDTH_DEFAULT = 2

class LayerRoutes(LayerBase):
    def __init__(self, options):
        self.color = options.get("color", COLOR_DEFAULT)
        self.width = options.get("width", WIDTH_DEFAULT)
        self.way_ids = set()
        self.relation_filter = lambda r: all(r.tags.get(k) == v for k,v in options["tags"].items())

        self.handle_ways = "ways" in options
        if self.handle_ways:
            self.way_width = options["ways"].get("width", WIDTH_DEFAULT)
            self.way_filter = lambda w: all(w.tags.get(k) == v for k,v in options["ways"]["tags"].items())

    # returns tuple(color, width)
    def get_pencil_for_way(self, way):
        if way.id in self.way_ids:
            return (self.color, self.width)
        if self.handle_ways and self.way_filter(way):
            return (self.color, self.way_width)
        return None

    def handle_relation(self, relation):
        if relation.tags.get("type") == "route" and self.relation_filter(relation):
            self.way_ids |= { m.ref for m in relation.members if m.type == "w" and m.role == "" }
    
    def does_handle_relation(self):
        return True
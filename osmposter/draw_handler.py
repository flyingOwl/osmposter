import osmium
import cairo
import os

import osmposter.layer
import osmposter.utils

class Transformator():
    def __init__(self, boundary_rect, scale_m_per_px):
        center_latlon = osmposter.utils.get_center_from_boundary_rect(boundary_rect)
        self.center_lat = center_latlon[0]
        self.zero_lat = boundary_rect[1][0]
        self.zero_lon = boundary_rect[0][1]
        self.base_lat = osmium.osm.Location(self.zero_lon, self.zero_lat)
        self.base_lon = osmium.osm.Location(self.zero_lon, self.center_lat)
        self.scale = scale_m_per_px

    def to_xy(self, lat, lon):
        factor_x = 1 if lon > self.zero_lon else -1
        factor_y = 1 if lat < self.zero_lat else -1
        return (factor_x * osmium.geom.haversine_distance(self.base_lon, osmium.osm.Location(lon, self.center_lat)) / self.scale,
            factor_y * osmium.geom.haversine_distance(self.base_lat, osmium.osm.Location(self.zero_lon, lat)) / self.scale)

class DrawHandler(osmium.SimpleHandler):
    def __init__(self, boundary_rect, scale_factor, canvas_size, config):
        self.bounds = boundary_rect
        self.config = config
        self.width_scale = (self.config["draw"]["baseline_mm"] / 25.4) * self.config["output"]["dpi"]

        self.layers = {}
        self.surface = {}
        self.canvas = {}

        layers_config = self.config["draw"]["layer"]
        for l_name, l in layers_config.items():
            l_obj = osmposter.layer.name2layer[l["type"]](l.get("options") or {})
            self.layers[l_name] = l_obj
            self.surface[l_name] = cairo.ImageSurface(cairo.FORMAT_ARGB32, canvas_size[0], canvas_size[1])
            canvas = cairo.Context(self.surface[l_name])
            canvas.set_line_join(cairo.LINE_JOIN_ROUND)
            canvas.set_line_cap(cairo.LINE_CAP_ROUND)
            canvas.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
            self.canvas[l_name] = canvas

        self.t = Transformator(boundary_rect, scale_factor)

    def needs_relation_pass(self):
        return any(l.does_handle_relation() for l in self.layers.values())

    def save_to_file(self, basedir):
        for l_name in self.layers:
            self.surface[l_name].write_to_png(os.path.join(basedir, f"{l_name}.png"))

    def inside(self, l):
        return any((self.bounds[0][0] < n.lat < self.bounds[1][0]) and (self.bounds[0][1] < n.lon < self.bounds[1][1]) for n in l)

    def draw_raw(self, c, l, close=False):
        is_first = True
        for n in l:
            x, y = self.t.to_xy(n.lat, n.lon)
            if is_first:
                c.move_to(x, y)
                is_first = False
            else:
                c.line_to(x, y)
        if close and not l.is_closed():
            c.close_path()

    def draw_area(self, c, color, area):
        c.set_source_rgb(*color)
        c.set_line_width(0)
        # draw outer rings
        for o in area.outer_rings():
            self.draw_raw(c, o, True)
            # draw inner polygons of this outer ring
            for i in area.inner_rings(o):
                self.draw_raw(c, i, True)
            c.fill()

    def draw_way(self, c, color, width, way):
        c.set_source_rgb(*color)
        c.set_line_width(width)
        self.draw_raw(c, way.nodes)
        c.stroke()

    def way(self, w):
        if not self.inside(w.nodes):
            return
        for l_name, l_obj in self.layers.items():
            pencil = l_obj.get_pencil_for_way(w)
            if pencil is not None:
                self.draw_way(self.canvas[l_name], pencil[0], pencil[1] * self.width_scale, w)
    
    def area(self, a):
        if not any(self.inside(r) for r in a.outer_rings()):
            return
        for l_name, l_obj in self.layers.items():
            color = l_obj.get_color_for_area(a)
            if color is not None:
                self.draw_area(self.canvas[l_name], color, a)

    def relation(self, r):
        for _, l_obj in self.layers.items():
            l_obj.handle_relation(r)

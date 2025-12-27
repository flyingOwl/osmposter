import osmium
import sys
import os
import json

from . import draw_handler
from . import utils

def get_boundary_rect(fp):
    lat_values = []
    lon_values = []
    for w in fp:
        if w.is_way():
            lat_values += [n.lat for n in w.nodes if n.location.valid()]
            lon_values += [n.lon for n in w.nodes if n.location.valid()]
    return ((min(lat_values), min(lon_values)), (max(lat_values), max(lon_values)))

def get_boundary_rect_extended(boundary_rect, extend_factors):
    center_latlon = utils.get_center_from_boundary_rect(boundary_rect)
    new_min_lat = extend_from_center(center_latlon[0], boundary_rect[0][0], extend_factors[2])
    new_min_lon = extend_from_center(center_latlon[1], boundary_rect[0][1], extend_factors[3])
    new_max_lat = extend_from_center(center_latlon[0], boundary_rect[1][0], extend_factors[0])
    new_max_lon = extend_from_center(center_latlon[1], boundary_rect[1][1], extend_factors[1])
    return ((new_min_lat, new_min_lon), (new_max_lat, new_max_lon))

def extend_from_center(center, boundary, factor):
    return center + (boundary - center) * (1 + factor)

def get_distance_in_boundary(boundary_rect):
    center_latlon = utils.get_center_from_boundary_rect(boundary_rect)
    # osmium.osm.Location is (lon, lat) !!
    center_lat_min_lon = osmium.osm.Location(boundary_rect[0][1], center_latlon[0])
    center_lat_max_lon = osmium.osm.Location(boundary_rect[1][1], center_latlon[0])
    min_lat_center_lon = osmium.osm.Location(center_latlon[1], boundary_rect[0][0])
    max_lat_center_lon = osmium.osm.Location(center_latlon[1], boundary_rect[1][0])
    # order: lon distance, lat distance (X, Y)
    return (osmium.geom.haversine_distance(center_lat_min_lon, center_lat_max_lon),
        osmium.geom.haversine_distance(min_lat_center_lon, max_lat_center_lon))

class OsmPosterGenerator:
    def __init__(self, config):
        self.config = config
        self.osm_file = self.config["osmfile"]
        self.relation_id = self.config["relation"]
        extend_raw = self.config["boundary_extension"]
        self.extend = [
            float(extend_raw["north"]),
            float(extend_raw["east"]),
            float(extend_raw["south"]),
            float(extend_raw["west"])
        ]
        canvas_mm = [
            int(config["output"]["w_mm"]),
            int(config["output"]["h_mm"])
        ]
        self.canvas_px = tuple(int((mm / 25.4) * config["output"]["dpi"]) for mm in canvas_mm)
        self.output_dir = os.path.join("output", config["label"])
    
    def generate(self):
        print(f"Getting dimensions and boundary of osm relation #{self.relation_id:d}")
        boundary_ways = []
        for o in osmium.FileProcessor(self.osm_file, osmium.osm.RELATION).with_filter(
            osmium.filter.IdFilter([self.relation_id])):
            boundary_ways = [m.ref for m in o.members if m.role == "outer"]
            break
        boundary_rect = get_boundary_rect(osmium.FileProcessor(self.osm_file).with_filter(osmium.filter.IdFilter(boundary_ways)).with_locations())

        print("Calculating final scale and dimension")
        boundary_rect_extended = get_boundary_rect_extended(boundary_rect, self.extend)

        distances_xy = get_distance_in_boundary(boundary_rect_extended)
        scale_per_px_xy = [dist/px for dist, px in zip(distances_xy, self.canvas_px)]
        aspect_difference = (max(scale_per_px_xy) / min(scale_per_px_xy)) - 1
        if aspect_difference > 0.2:
            print(f"WARN: Canvas and relation aspect ratio differ (by {aspect_difference*100:.0f} %)!")

        scale_final = max(scale_per_px_xy)
        extend_lat = (scale_final / scale_per_px_xy[1]) - 1
        extend_lon = (scale_final / scale_per_px_xy[0]) - 1
        boundary_rect_final = get_boundary_rect_extended(boundary_rect_extended, [extend_lat, extend_lon, extend_lat, extend_lon])

        print("Prepare drawing")
        draw = draw_handler.DrawHandler(boundary_rect_final, scale_final, self.canvas_px, self.config)

        print("Drawing ...")
        if draw.needs_relation_pass():
            osmium.apply(self.osm_file, osmium.filter.EntityFilter(osmium.osm.RELATION), draw)
        draw.apply_file(self.osm_file, locations=True)
        print("Saving files")
        os.makedirs(self.output_dir, exist_ok=True)
        draw.save_to_file(self.output_dir)

def load_json(filename):
    with open(filename, encoding='utf-8') as f_in:
        return json.load(f_in)

generator = OsmPosterGenerator(load_json(sys.argv[1]))
generator.generate()


def get_center_from_boundary_rect(boundary_rect):
    center_lat = sum(p[0] for p in boundary_rect) / 2
    center_lon = sum(p[1] for p in boundary_rect) / 2
    return (center_lat, center_lon)

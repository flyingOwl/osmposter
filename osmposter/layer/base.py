
class LayerBase:
    
    # returns tuple(color, width) or None
    def get_pencil_for_way(self, _):
        return None

    # returns color or None
    def get_color_for_area(self, _):
        return None
    
    # returns nothing
    def handle_relation(self, _):
        pass
    
    def does_handle_relation(self):
        return False
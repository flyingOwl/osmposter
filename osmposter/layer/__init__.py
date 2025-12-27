
from . import aeroways, boundary, buildings, railways, routes, streets, water

name2layer = {
    "aeroways": aeroways.LayerAreoways,
    "boundary": boundary.LayerBoundary,
    "buildings": buildings.LayerBuildings,
    "railways": railways.LayerRailways,
    "routes": routes.LayerRoutes,
    "streets": streets.LayerStreets,
    "water": water.LayerWater,
}
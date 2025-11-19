from ..models import *
from .svg_util import *

__all__ = [
    'svg_actor_locations',
]

MAP_WIDTH = 800
MAP_HEIGHT = 600
ACTOR_WIDTH = 100
ACTOR_HEIGHT = 60

def svg_actor_locations(models: ModelSet, model_id: ModelID) -> str:
    """Create a 'map' of all top-level locations and position all actors that have an explictly specified location"""
   
    #Start with a basic rectangle defining the main map
    map_shape = Shape(MAP_WIDTH//2, MAP_HEIGHT//2, 'box', MAP_WIDTH, MAP_HEIGHT,text = '')

    #Create areas for all top-level locations
    root_locations = []
    for location_id in models.list_locations(model_id):
        if not super_locations(models,model_id,location_id):
            root_locations.append(location_id)
    
    
    location_shapes = []
    location_offsets = {}
    
    if root_locations:
        area_width = MAP_WIDTH // len(root_locations)
        for i, location_id in enumerate(root_locations):
            location = models.get_location_by_id(location_id)
            location_shapes.append(Shape(i*area_width + area_width//2,MAP_HEIGHT//2,'box',area_width,MAP_HEIGHT, text = location.label))
            location_offsets[location_id] = i*area_width + area_width//2

    #Place markers for all actors that have an explicitly specified
    actor_locations: dict[LocationID,list[Actor]] = {}
    actor_shapes = []
    for location_id in root_locations:
        actor_locations[location_id] = []

    for actor_id in models.list_actors(model_id):
        actor = models.get_actor_by_id(actor_id)
        for at_location in actor.at_locations:
            if at_location in actor_locations:
                actor_locations[at_location].append(actor)

    for location_id, actors in actor_locations.items():
        for i, actor in enumerate(actors):
            actor_shapes.append(Shape(location_offsets[location_id], i*(ACTOR_HEIGHT + 20) + ACTOR_HEIGHT//2 + 10,'box',ACTOR_WIDTH,ACTOR_HEIGHT,text=actor.label))

    shapes = [map_shape] + location_shapes + actor_shapes
    return svg_figure(shapes,[])
from ..models import *
from .svg_util import *
from dataclasses import dataclass
__all__ = [
    'svg_actor_information_flow'
]

BOX_WIDTH = 100
BOX_HEIGHT = 60
BOX_MARGIN_VERTICAL = 40
BOX_MARGIN_HORIZONTAL = 20
BOX_PADDING = 5
DIAGRAM_MARGIN = 100

@dataclass
class ActorNode:
    actor: Actor
    shape: Shape
    custom_position: bool

@dataclass
class InfoSpaceNode:
    info_space: InformationSpace
    shape: Shape
    connections: list[tuple[ActorID,bool,bool]]

def svg_actor_information_flow(models: ModelSet, model_id: ModelID, show_info_spaces: bool = True) -> str:
    #Find all information spaces that are accessed by at least two different actors
    ifs_actors: dict[InformationSpaceID,set[ActorID]] = {}
    ifs_directions: dict[tuple[InformationSpaceID,ActorID],tuple[bool,bool]] = {}

    for actor_id in list_individuals(models,model_id):
        actor_tasks = collect_actor_concrete_atomic_tasks(models,model_id,actor_id)
        for task_id in actor_tasks:
            task = models.get_task_by_id(task_id,model_id)
            task_spaces = resolve_info_space_bindings(models,task)
            for (req, ifs) in task_spaces.values():
                if ifs is None:
                    continue
                ifs_id = ifs.node_id
                if ifs_id not in ifs_actors:
                    ifs_actors[ifs_id] = set()
                ifs_actors[ifs_id].add(actor_id)
                if (ifs_id, actor_id) in ifs_directions:
                    read, write = ifs_directions[(ifs_id, actor_id)]
                    ifs_directions[(ifs_id, actor_id)] = (read or req.read, write or req.write)
                else:
                    ifs_directions[(ifs_id, actor_id)] = (req.read,req.write)

    channels = [(ifs_id, [(aid,ifs_directions[(ifs_id, aid)]) for aid in actors]) for ifs_id, actors in ifs_actors.items() if len(actors) >= 2]

    #Position actors in a line
    actor_nodes: list[ActorNode] = []
    default_x = 10 + (BOX_WIDTH // 2)
    default_y = 10 + (BOX_HEIGHT // 2)
    for actor_id in models.list_actors(model_id):
        actor = models.get_actor_by_id(actor_id)

        flow_xy = actor.get_attribute('flow_xy')
        x, y = None, None
        custom_position = False
        if flow_xy is not None:
            xy = flow_xy.split(",")
            if len(xy) == 2 and xy[0].isnumeric() and xy[1].isnumeric():
                x, y = int(xy[0]), int(xy[1])
                custom_position = True
    
        if x is None or y is None:
            x, y = default_x, default_y
            default_x += BOX_WIDTH + 10

        actor_nodes.append(ActorNode(actor,Shape(x,y,'box',BOX_WIDTH,BOX_HEIGHT,text=actor.label,color=actor.color),custom_position))

    indexed_nodes = {n.actor.node_id:n for n in actor_nodes}
    
    #Position channels in a line a row below.
    channel_nodes: list[InfoSpaceNode] = []
    default_x = 10 + (BOX_WIDTH // 2)
    default_y = 50 + (BOX_HEIGHT // 2) + BOX_HEIGHT

    for ifs_id, ifs_actors in channels:
        ifs = models.get_info_space_by_id(ifs_id,model_id)

        custom_actor_placement = False
        for name, directions in ifs_actors:
            if indexed_nodes[name].custom_position:
                custom_actor_placement = True
                break
        
        x, y = None, None
        flow_xy = ifs.get_attribute('flow_xy')
        if flow_xy is not None:
            xy = flow_xy.split(",")
            if len(xy) == 2 and xy[0].isnumeric() and xy[1].isnumeric():
                x, y = int(xy[0]), int(xy[1])
        if (x is None or y is None) and custom_actor_placement:
            xs, ys  = list(zip(*[(indexed_nodes[actor[0]].shape.x,indexed_nodes[actor[0]].shape.y) for actor in ifs_actors]))
            x = int(sum(xs) / len(xs))
            y = int(sum(ys) / len(ys))
        
        if x is None or y is None:
            x, y = default_x, default_y
            default_x += BOX_WIDTH + 10
        
        shape = Shape(x,y,'ellipse',BOX_WIDTH,BOX_HEIGHT,text=ifs.label)
        connections = [(a[0],a[1][0],a[1][1]) for a in ifs_actors]

        node = InfoSpaceNode(ifs,shape,connections)
        channel_nodes.append(node)

    shapes: list[Shape] = []
    connections: list[Connection] = []

    #Draw actors
    for node in actor_nodes:
        shapes.append(node.shape)
    
    #Draw information flows
    for node in channel_nodes:
    
        if show_info_spaces:
            #Node
            shapes.append(node.shape)

            #Connections
            for actor_id, read,write in node.connections:
                actor_node = indexed_nodes[actor_id]
                connections.append(Connection(node.shape,actor_node.shape,write,read))
        else:
            #Don't draw the information spaces, just the connections
            writers = [actor_id for actor_id, _, write in node.connections if write]
            readers = [actor_id for actor_id, read, _ in node.connections if read]

            for writer_id in writers:
                source_shape =  indexed_nodes[writer_id].shape
                for reader_id in readers:
                    destination_shape = indexed_nodes[reader_id].shape
                    connections.append(Connection(source_shape,destination_shape,False,True))

    return svg_figure(shapes,connections)
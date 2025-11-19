from ..models.execution import Scenario, ScenarioEvent, ScenarioInformationEvent, ScenarioTaskInitiateEvent
from ..models.execution import ScenarioChangeGroupsEvent, ScenarioChangeLocationsEvent
from ..models.identifier import ScenarioID

import pathlib
import lark, lark.visitors

__all__ = ['scenario_from_c2e_str','scenario_from_c2e_file',]

c2e_grammar = '''
%import common.INT
%import common.CNAME
%import common.LETTER
%import common.DIGIT
%import common.WS
%import common.NEWLINE
%import common.ESCAPED_STRING

scenario: start_rule event*

start_rule: INT WS "start" WS DOTTED_NAME NEWLINE?
?event: info_event | initiate_event | change_groups_event | change_locations_event

info_event: INT WS "event" WS "info:" NEWLINE info_property+
!info_property: WS? (("actor" WS DOTTED_ID) | ("info-space" WS DOTTED_ID) | ("record" WS record_literal) | ("task" WS DOTTED_ID)) WS? NEWLINE?

initiate_event: INT WS "event" WS "initiate-task:" NEWLINE initiate_property+
!initiate_property: WS? (("actor" WS DOTTED_ID) | ("task-def" WS DOTTED_ID) | ("parameter" WS record_literal) | ("trigger" WS DOTTED_ID) |("for-actor" WS DOTTED_ID)) WS? NEWLINE?

change_groups_event: INT WS "event" WS "change-groups:" NEWLINE change_groups_property+
!change_groups_property: WS? (("actor" WS DOTTED_ID) | ("join-group" WS DOTTED_ID) | ("leave-group" WS DOTTED_ID)) WS? NEWLINE?

change_locations_event: INT WS "event" WS "change-locations:" NEWLINE change_locations_property+
!change_locations_property: WS? (("actor" WS DOTTED_ID) | ("enter-location" WS DOTTED_ID) | ("leave-location" WS DOTTED_ID)) WS? NEWLINE?

record_literal: "{" (CNAME WS? "=" WS? LITERAL ("," WS? CNAME WS? "=" WS? LITERAL)*)? "}"
LITERAL: ESCAPED_STRING | INT

NAME: ("_"|LETTER) ("_"|"-"|LETTER|DIGIT)*
DOTTED_NAME: NAME ("." NAME)*
DOTTED_ID: DOTTED_NAME ("@" DOTTED_NAME)?
'''
c2e_parser = lark.Lark(c2e_grammar, start= 'scenario')

def remove_whitespace(tokens: list[lark.Tree|lark.Token]) -> list[lark.Tree|lark.Token]:
    return [token for token in tokens if not (isinstance(token,lark.Token) and token.type == 'WS')]

class ScenarioBuilder(lark.visitors.Interpreter):
    def __init__(self, scenario_name: str):
        self.scenario_name = scenario_name
        super().__init__()

    def scenario(self, tree: lark.Tree[lark.Token]):
        children = self.visit_children(tree)
        model = children[0]
        events = children[1:]
        return Scenario(self.scenario_name,model,events)
    
    def start_rule(self, tree: lark.Tree[lark.Token]):
        children = remove_whitespace(tree.children)
        return children[1].value
        
    def info_event(self,tree: lark.Tree[lark.Token]):
        time = int(tree.children[0].value)
        actor, info_space, fields, task = None, None, {}, None
        
        for prop_tree in tree.children:
            if not isinstance(prop_tree, lark.Tree):
                continue
            prop_children = remove_whitespace(prop_tree.children)
            match prop_children[0].value:
                case 'actor':
                    actor = prop_children[1].value
                case 'info-space':
                    info_space = prop_children[1].value
                case 'record':
                    fields = self.visit(prop_children[1])
                case 'task':
                    task = prop_children[1].value
    
        return ScenarioInformationEvent(time, actor, info_space, fields,task)
    
    def initiate_event(self, tree: lark.Tree[lark.Token]):
        time = int(tree.children[0].value)
        actor, task_definition, parameter, trigger, for_actor = None, None, {}, None, None

        for prop_tree in tree.children:
            if not isinstance(prop_tree, lark.Tree):
                continue
            prop_children = remove_whitespace(prop_tree.children)
            match prop_children[0].value:
                case 'actor':
                    actor = prop_children[1].value
                case 'task-def':
                    task_definition = prop_children[1].value
                case 'parameter':
                    parameter = self.visit(prop_children[1])
                case 'trigger':
                    trigger = prop_children[1].value
                case 'for-actor':
                    for_actor = prop_children[1].value

        return ScenarioTaskInitiateEvent(time,actor,task_definition,parameter,trigger,for_actor)

    def change_groups_event(self,tree: lark.Tree[lark.Token]):
        time = int(tree.children[0].value)
        actor, leave_groups, join_groups = None, [], []
        for prop_tree in tree.children:
            if not isinstance(prop_tree, lark.Tree):
                continue
            prop_children = remove_whitespace(prop_tree.children)
            match prop_children[0].value:
                case 'actor':
                    actor = prop_children[1].value
                case 'leave-group':
                    leave_groups.append(prop_children[1].value)
                case 'join-group':
                    join_groups.append(prop_children[1].value)
        return ScenarioChangeGroupsEvent(time,actor,leave_groups,join_groups)

    def change_locations_event(self,tree: lark.Tree[lark.Token]):
        time = int(tree.children[0].value)
        actor, leave_locations, enter_locations = None, [], []
        for prop_tree in tree.children:
            if not isinstance(prop_tree, lark.Tree):
                continue
            prop_children = remove_whitespace(prop_tree.children)
            match prop_children[0].value:
                case 'actor':
                    actor = prop_children[1].value
                case 'leave-location':
                    leave_locations.append(prop_children[1].value)
                case 'enter-location':
                    enter_locations.append(prop_children[1].value)
        return ScenarioChangeLocationsEvent(time,actor,leave_locations,enter_locations)
    
    def record_literal(self, tree: lark.Tree[lark.Token]) -> dict[str,int|str]:
        values = {}
        children = remove_whitespace(tree.children)
        for i in range(0,len(children),2):
            values[children[i].value] =  children[i+1].value[1:-1]
        return values
    
def scenario_from_c2e_str(scenario_id: ScenarioID, source: str, allow_syntax_errors: bool = False) -> Scenario:
   
    try:
        tree = c2e_parser.parse(source)
        scenario = ScenarioBuilder(scenario_id).visit(tree)
    except lark.exceptions.UnexpectedToken as e:
        if allow_syntax_errors:
            return Scenario(scenario_id,'',[])
        else:
            raise
    except lark.exceptions.UnexpectedEOF as e:
        if allow_syntax_errors:
            return Scenario(scenario_id,'',[])
        else:
            raise
    return scenario

def scenario_from_c2e_file(scenario_id: ScenarioID, path: str | pathlib.Path, allow_syntax_errors: bool = False) -> Scenario:
    if isinstance(path,str):
        path = pathlib.Path(path)

    return scenario_from_c2e_str(scenario_id, path.read_text(), allow_syntax_errors)
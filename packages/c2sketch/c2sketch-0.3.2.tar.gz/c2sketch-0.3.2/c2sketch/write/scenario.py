from ..models.execution import Scenario, ScenarioInformationEvent, ScenarioTaskInitiateEvent
from ..models.execution import ScenarioChangeGroupsEvent, ScenarioChangeLocationsEvent

from typing import Any

import pathlib
import os

__all__ = [
    'scenario_to_c2e_str',
    'scenario_to_c2e_file',
]

def scenario_to_c2e_str(scenario: Scenario) -> str:
    """Serializes a scenario to c2e format.
    
    Args:
        scenario: The scenario to serialize.
    
    Returns:
        The c2e formatted string representation of the scenario.
    """
    def fields_str(fields: dict[str,Any]) -> str:
        fields_str = [f'{key} = "{value}"' for key, value in fields.items()]
        return f'{{{", ".join(fields_str)}}}'
    
    lines = [f'0 start {scenario.model}']
    
    for event in scenario.events:
        match event:
            case ScenarioInformationEvent():
                lines.append(f'{event.time} event info:')
                lines.append(f'    actor {event.actor}')
                lines.append(f'    info-space {event.information_space}')
                lines.append(f'    record {fields_str(event.fields)}')
                if event.task is not None:
                    lines.append(f'    task {event.task}')
            case ScenarioTaskInitiateEvent():
                lines.append(f'{event.time} event initiate-task:')
                lines.append(f'    actor {event.actor}')
                lines.append(f'    task-def {event.task_definition}')
                lines.append(f'    parameter {fields_str(event.parameter)}')
                if event.trigger is not None:
                    lines.append(f'    trigger {event.trigger}')
                if event.for_actor is not None:
                    lines.append(f'    for-actor {event.for_actor}')
            case ScenarioChangeGroupsEvent():
                lines.append(f'{event.time} event change-groups:')
                lines.append(f'    actor {event.actor}')
                for group in event.leave_groups:
                    lines.append(f'    leave-group {group}')
                for group in event.join_groups:
                    lines.append(f'    join-group {group}')
            case ScenarioChangeLocationsEvent():
                lines.append(f'{event.time} event change-locations:')
                lines.append(f'    actor {event.actor}')
                for location in event.leave_locations:
                    lines.append(f'    leave-location {location}')
                for location in event.enter_locations:
                    lines.append(f'    enter-location {location}')

    return os.linesep.join(lines)

def scenario_to_c2e_file(scenario: Scenario, path: pathlib.Path | str) -> None:
    """Writes a scenario to c2e formatted file.

    Args:
        scenario: The scenario to serialize.
        path: The filename to which the scenario is written.
    """
    if isinstance(path,str):
        path = pathlib.Path(path)

    path.write_text(scenario_to_c2e_str(scenario))

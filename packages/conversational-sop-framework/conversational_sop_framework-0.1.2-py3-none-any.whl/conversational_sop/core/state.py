from typing import Optional, Dict, List, Any, Type

from typing_extensions import TypedDict

from .constants import DataType


def get_state_value(state: Dict[str, Any], key: str, default: Any = None) -> Any:
    return state.get(key, default)

def set_state_value(state: Dict[str, Any], key: str, value: Any) -> None:
    state[key] = value

def create_state_model(data_fields: List[dict]) -> Type[TypedDict]:
    type_mapping = {
        DataType.TEXT.value: Optional[str],
        DataType.NUMBER.value: Optional[int],
        DataType.BOOLEAN.value: Optional[bool],
        DataType.LIST.value: Optional[List[Any]],
        DataType.DICT.value: Optional[Dict[str, Any]],
    }

    fields = {}

    for field_def in data_fields:
        field_name = field_def['name']
        field_type = field_def['type']
        python_type = type_mapping.get(field_type, Optional[str])
        fields[field_name] = python_type

    fields['_step_id'] = Optional[str]
    fields['_status'] = Optional[str]
    fields['_outcome_id'] = Optional[str]
    fields['_messages'] = List[str]
    fields['_conversations'] = Dict[str, List[Dict[str, str]]]
    fields['_state_history'] = List[Dict[str, Any]]
    fields['_collector_nodes'] = Dict[str, str]
    fields['_attempt_counts'] = Dict[str, int]
    fields['_node_execution_order'] = List[str]
    fields['_node_field_map'] = Dict[str, str]
    fields['_computed_fields'] = List[str]

    return TypedDict(
        'WorkflowState',
        fields,
        total=False
    )


def initialize_state(state: Dict[str, Any]) -> Dict[str, Any]:
    fields_to_initialize = {
        '_state_history': [],
        '_collector_nodes': {},
        '_conversations': {},
        '_messages': [],
        '_attempt_counts': {},
        '_node_execution_order': [],
        '_node_field_map': {},
        '_computed_fields': []
    }

    for field_name, default_value in fields_to_initialize.items():
        if not get_state_value(state, field_name):
            set_state_value(state, field_name, default_value.copy() if isinstance(default_value, (list, dict)) else default_value)

    return state
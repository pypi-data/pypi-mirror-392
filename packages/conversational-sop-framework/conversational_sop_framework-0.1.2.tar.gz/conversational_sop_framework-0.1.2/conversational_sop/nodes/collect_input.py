import copy
import logging
from typing import Dict, Any, List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from langgraph.types import interrupt

from .base import ActionStrategy
from ..core.constants import (
    WorkflowKeys,
    DEFAULT_MAX_ATTEMPTS,
    MAX_ATTEMPTS_MESSAGE,
    TransitionPattern
)
from ..core.state import initialize_state
from ..core.rollback_strategies import (
    RollbackStrategy,
    HistoryBasedRollback,
    DependencyBasedRollback
)

logger = logging.getLogger(__name__)

def _wrap_instructions_with_intent_detection(
        instructions: str,
    collector_nodes: Dict[str, str]
) -> str:
    return f"""
{instructions}

You have been configured with the following conversation intents:

{collector_nodes}
Format:
- <node_name>: <intent_description>

CRITICAL INSTRUCTION:
Before responding to the user's message, analyze if their query represents a change in conversation intent compared to the current flow.

IF the user's query matches a DIFFERENT intent from the list above than what you're currently handling:
- Respond ONLY with: INTENT_CHANGE: <node_name>
- Do NOT provide any other response
- Do NOT answer the user's question
- <node_name> should be the exact node name that matches the new intent

IF the user's query continues with the SAME intent or is a natural continuation of the current conversation:
- Proceed with your normal response
- Do NOT mention intent detection
- Answer the user's question as configured
"""


def _restore_from_snapshot(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    return copy.deepcopy(snapshot['state'])


def _create_rollback_strategy(strategy_name: str) -> RollbackStrategy:
    if strategy_name == "dependency_based":
        return DependencyBasedRollback()
    elif strategy_name == "history_based":
        return HistoryBasedRollback()
    else:
        logger.warning(f"Unknown rollback strategy '{strategy_name}', using history_based")
        return HistoryBasedRollback()


class CollectInputStrategy(ActionStrategy):
    def __init__(self, step_config: Dict[str, Any], engine_context: Any):
        super().__init__(step_config, engine_context)
        self.field = step_config.get('field')
        self.agent_config = step_config.get('agent', {})
        self.max_attempts = step_config.get('retry_limit') or engine_context.get_config_value("max_retry_limit", DEFAULT_MAX_ATTEMPTS)
        self.transitions = self._get_transitions()
        self.next_step = self.agent_config.get("next", None)

        rollback_strategy_name = engine_context.get_config_value("rollback_strategy", "history_based")
        self.rollback_strategy = _create_rollback_strategy(rollback_strategy_name)
        logger.info(f"Using rollback strategy: {self.rollback_strategy.get_strategy_name()}")

        if not self.field:
            raise RuntimeError(f"Step '{self.step_id}' missing required 'field' property")

        if not self.agent_config:
            raise RuntimeError(f"Step '{self.step_id}' missing required 'agent' configuration")

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state = initialize_state(state)

        is_self_loop = self._is_self_loop(state)

        if not is_self_loop:
            if self.rollback_strategy.should_save_snapshot():
                self._save_snapshot_before_execution(state)
            self._register_node_execution(state)
            self._register_collector_node(state)

        if self._is_field_pre_populated(state):
            return self._handle_pre_populated_field(state)

        if self._max_attempts_reached(state):
            return self._handle_max_attempts(state)

        conversation = self._get_or_create_conversation(state)

        agent = self._create_agent(state)

        prompt = self._generate_prompt(conversation)

        user_input = interrupt(prompt)

        conversation.append({"role": "user", "content": user_input})

        response = agent.run(conversation)
        agent_response = response.content
        conversation.append({"role": "assistant", "content": agent_response})

        self._update_conversation(state, conversation)

        if agent_response.startswith(TransitionPattern.INTENT_CHANGE):
            return self._handle_intent_change(state, agent_response)

        return self._process_transitions(state, agent_response)

    def _is_self_loop(self, state: Dict[str, Any]) -> bool:
        collecting_status = f'{self.step_id}_collecting'
        status = state.get(WorkflowKeys.STATUS, '')
        if status == collecting_status:
            logger.debug(f"{self.step_id}: In self loop")
            return True

        return False

    def _save_snapshot_before_execution(self, state: Dict[str, Any]):
        state_history = state.get(WorkflowKeys.STATE_HISTORY, [])
        execution_index = len(state_history)
        self.rollback_strategy.save_snapshot(state, self.step_id, execution_index)

    def _register_node_execution(self, state: Dict[str, Any]):
        execution_order = state.get(WorkflowKeys.NODE_EXECUTION_ORDER, [])
        if self.step_id not in execution_order:
            execution_order.append(self.step_id)
        state[WorkflowKeys.NODE_EXECUTION_ORDER] = execution_order

    def _register_collector_node(self, state: Dict[str, Any]):
        description = self.agent_config.get('description', f"Collecting {self.field}")
        state[WorkflowKeys.COLLECTOR_NODES][self.step_id] = description

        node_field_map = state.get(WorkflowKeys.NODE_FIELD_MAP, {})
        node_field_map[self.step_id] = self.field
        state[WorkflowKeys.NODE_FIELD_MAP] = node_field_map

    def _is_field_pre_populated(self, state: Dict[str, Any]) -> bool:
        return state.get(self.field) is not None

    def _handle_pre_populated_field(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Field '{self.field}' is populated, skipping collection")

        if self.transitions:
            first_transition = self.transitions[0]
            next_step = first_transition['next']
            self._set_status(state, next_step)

            if next_step in self.engine_context.outcome_map:
                self._set_outcome(state, next_step)

        if self.next_step:
            self._set_status(state, self.next_step)

            if self.next_step in self.engine_context.outcome_map:
                self._set_outcome(state, self.next_step)

        return state

    def _max_attempts_reached(self, state: Dict[str, Any]) -> bool:
        conv_key = f'{self.field}_conversation'
        conversation = state.get(WorkflowKeys.CONVERSATIONS, {}).get(conv_key, [])
        attempt_count = len([m for m in conversation if m['role'] == 'user'])
        return attempt_count >= self.max_attempts

    def _handle_max_attempts(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.warning(f"Max attempts reached for field '{self.field}'")
        self._set_status(state, 'max_attempts')
        message = MAX_ATTEMPTS_MESSAGE.format(field=self.field)
        state[WorkflowKeys.MESSAGES] = [message]
        return state

    def _get_or_create_conversation(self, state: Dict[str, Any]) -> List[Dict[str, str]]:
        conv_key = f'{self.field}_conversation'
        conversations = state.get(WorkflowKeys.CONVERSATIONS, {})

        if conv_key not in conversations:
            conversations[conv_key] = []
            state[WorkflowKeys.CONVERSATIONS] = conversations

        return conversations[conv_key]

    def _create_agent(self, state: Dict[str, Any]) -> Agent:
        try:
            model_config = self.engine_context.get_config_value('model_config')
            model_id = self.agent_config.get('model', 'gpt-4o-mini') or model_config.get('model')
            base_url = model_config.get('base_url_mapping').get(model_id)

            api_key = model_config.get('api_key')
            if not api_key:
                auth_callback = model_config.get('auth_callback')
                api_key = auth_callback()

            model = OpenAIChat(
                id=model_id,
                base_url=base_url,
                api_key=api_key
            )

            instructions = self.agent_config.get("instructions")
            if collector_nodes := state.get(WorkflowKeys.COLLECTOR_NODES, {}) :
                instructions = _wrap_instructions_with_intent_detection(
                    instructions, collector_nodes
                )

            tools = self.agent_config.get('tools', [])
            agent_tools = []
            if tools:
                for tool_name in tools:
                    agent_tools.append(self.engine_context.tool_repository.load(tool_name))

            return Agent(
                name=self.agent_config.get('name', f'{self.field}Collector'),
                model=model,
                instructions=instructions,
                tools=agent_tools
            )

        except Exception as e:
            raise RuntimeError(f"Failed to create agent for step '{self.step_id}': {e}")

    def _generate_prompt(
        self,
        conversation: List[Dict[str, str]]
    ) -> str:
        if len(conversation) == 0:
            prompt = self.agent_config.get('initial_message')
            conversation.append({"role": "assistant", "content": prompt})
            return prompt

        return conversation[-1]['content']

    def _update_conversation(
        self,
        state: Dict[str, Any],
        conversation: List[Dict[str, str]]
    ):
        conv_key = f'{self.field}_conversation'
        state[WorkflowKeys.CONVERSATIONS][conv_key] = conversation

    def _handle_intent_change(
        self,
        state: Dict[str, Any],
        agent_response: str
    ) -> Dict[str, Any]:
        target_node = agent_response.split(TransitionPattern.INTENT_CHANGE)[1].strip()
        logger.info(f"Intent change detected: {self.step_id} -> {target_node}")

        rollback_state = self._rollback_state_to_node(state, target_node)

        if rollback_state is None:
            logger.error(f"Failed to rollback to node '{target_node}'")
            raise RuntimeError(f"Unable to process intent change to '{target_node}'")

        return rollback_state

    def _rollback_state_to_node(
        self,
        state: Dict[str, Any],
        target_node: str
    ) -> Dict[str, Any]:
        node_execution_order = state.get(WorkflowKeys.NODE_EXECUTION_ORDER, [])
        node_field_map = state.get(WorkflowKeys.NODE_FIELD_MAP, {})
        workflow_steps = self.engine_context.steps

        restored_state = self.rollback_strategy.rollback_to_node(
            state=state,
            target_node=target_node,
            node_execution_order=node_execution_order,
            node_field_map=node_field_map,
            workflow_steps=workflow_steps
        )

        if not restored_state:
            logger.warning(f"Rollback strategy returned empty state for node '{target_node}'")
            return {}

        restored_state[WorkflowKeys.STATUS] = f"{self.step_id}_{target_node}"

        return restored_state

    def _process_transitions(
        self,
        state: Dict[str, Any],
        agent_response: str
    ) -> Dict[str, Any]:
        matched = False

        for transition in self.transitions:
            pattern = transition['pattern']
            if pattern in agent_response:
                matched = True
                next_step = transition['next']

                value = agent_response.split(pattern)[1].strip()

                if value:
                    self._store_field_value(state, value)
                    state[WorkflowKeys.MESSAGES] = [
                        f"✓ {self.field.replace('_', ' ').title()} collected: {value}"
                    ]
                else:
                    state[WorkflowKeys.MESSAGES] = []

                self._set_status(state, next_step)

                if next_step in self.engine_context.outcome_map:
                    self._set_outcome(state, next_step)

                break

        if not matched:
            self._set_status(state, 'collecting')
            state[WorkflowKeys.MESSAGES] = []

        return state

    def _store_field_value(self, state: Dict[str, Any], value: str):
        field_def = next((f for f in self.engine_context.data_fields if f['name'] == self.field), None)
        if not field_def:
            return

        if field_def.get('type') == 'number':
            try:
                state[self.field] = int(value)
            except ValueError:
                state[self.field] = value
        else:
            state[self.field] = value
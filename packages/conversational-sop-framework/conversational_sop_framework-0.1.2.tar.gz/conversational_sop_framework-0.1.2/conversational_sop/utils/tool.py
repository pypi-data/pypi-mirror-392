import importlib
import logging
from typing import Dict, Any

from agno.tools import tool

logger = logging.getLogger(__name__)


class ToolRepository:
    def __init__(self, tool_config):
        self._cache: Dict[str, Any] = {}
        self.tool_config = tool_config

    def load(self, tool_name):
        if tool_name in self._cache:
            logger.info("Tool found in cache")
            return self._cache[tool_name]

        tool_info = next((t for t in self.tool_config.get('tools') if t['name']==tool_name), None)
        if not tool_info:
            raise RuntimeError("The tool is not found in tool config")

        tool_description = tool_info.get("description")
        function_path = tool_info.get("callable")

        module_name, function_name = function_path.rsplit('.', 1)

        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            raise RuntimeError(f"Failed to import module '{module_name}': {e}")

        if not hasattr(module, function_name):
            raise RuntimeError(f"Module '{module_name}' has no function '{function_name}'")

        func = getattr(module, function_name)

        if not callable(func):
            raise RuntimeError(f"'{function_path}' is not callable (type: {type(func).__name__})")

        agno_tool = tool(name=tool_name, description=tool_description)(func)

        self._cache[function_path] = agno_tool
        logger.debug(f"Successfully loaded and cached function: {function_path}")
        return agno_tool

"""
Freeplay middleware for LangGraph agents.

This module provides middleware that integrates Freeplay prompt management
with LangGraph agents, handling dynamic prompt rendering and template message injection.
"""

import logging
from typing import TYPE_CHECKING, Any

from freeplay.resources.prompts import TemplatePrompt
from langchain.agents.middleware import AgentMiddleware

if TYPE_CHECKING:
    from langchain.agents.middleware.types import ModelRequest, ModelResponse
    from langchain_core.tools import BaseTool

    from freeplay_langgraph.client import FreeplayLangGraph

logger = logging.getLogger(__name__)


class FreeplayPromptMiddleware(AgentMiddleware):
    """
    Middleware that renders Freeplay prompts dynamically on each model call.

    This middleware:
    1. Extracts variables from agent state
    2. Calls Freeplay to render the prompt with those variables
    3. Sets the request's system prompt
    4. Injects template messages into the conversation
    5. Validates that provided tools match Freeplay's tool schema (if enabled)

    The middleware is automatically injected by FreeplayLangGraph.create_agent()
    and should not be instantiated directly by users.
    """

    def __init__(
        self,
        freeplay_client: "FreeplayLangGraph",
        template_prompt: TemplatePrompt,
        environment: str,
        validate_tools: bool = True,
    ):
        """
        Initialize Freeplay prompt middleware.

        Args:
            freeplay_client: FreeplayLangGraph client instance
            prompt_name: Name of the prompt in Freeplay
            environment: Environment to use (e.g., "production", "latest")
            validate_tools: Whether to validate tools against Freeplay schema
        """
        super().__init__()
        self._client = freeplay_client
        self._template_prompt = template_prompt
        self._environment = environment
        self._validate_tools = validate_tools
        self._tools_validated = False

    def _prepare_request(self, request: "ModelRequest") -> None:
        """
        Prepare the model request by formatting the prompt and updating request state.

        This method:
        1. Extracts variables from state
        2. Normalizes message history
        3. Formats the prompt using Freeplay
        4. Validates tools (on first call, if enabled)
        5. Updates request with system prompt and template messages

        Args:
            request: Model request to prepare

        Returns:
            FormattedPrompt from Freeplay
        """
        # Extract variables from state
        # State schema is automatically extended to include '__freeplay_variables__' field
        variables = request.state.get("__freeplay_variables__", {})

        formatted_prompt = self._template_prompt.bind(
            variables=variables, history=request.messages
        ).format("openai_chat")

        if self._validate_tools and not self._tools_validated:
            self._validate_tool_schema(request.tools, formatted_prompt.tool_schema)
            self._tools_validated = True

        # Set system prompt dynamically
        request.system_prompt = formatted_prompt.system_content
        request.messages = formatted_prompt.llm_prompt

    def wrap_model_call(self, request: "ModelRequest", handler) -> "ModelResponse":
        """
        Intercept model call to render Freeplay prompt and inject templates.

        Args:
            request: Model request containing state and runtime info
            handler: Callback to execute the model request

        Returns:
            Model response from handler
        """
        self._prepare_request(request)
        return handler(request)

    async def awrap_model_call(
        self, request: "ModelRequest", handler
    ) -> "ModelResponse":
        """
        Async version of wrap_model_call.

        Args:
            request: Model request containing state and runtime info
            handler: Async callback to execute the model request

        Returns:
            Model response from handler
        """
        self._prepare_request(request)
        return await handler(request)

    def _validate_tool_schema(
        self, provided_tools: list["BaseTool | dict"], tool_schema: Any
    ) -> None:
        """
        Validate that provided tools match Freeplay prompt's tool schema.

        Logs warnings if there are mismatches between expected and provided tools.

        Args:
            provided_tools: Tools provided to the agent
            formatted_prompt: Formatted prompt from Freeplay
        """
        # Check if prompt has tool schema
        if not tool_schema:
            return

        # Get expected tool names from Freeplay
        # tool_schema can be a dict or a list
        if isinstance(tool_schema, list):
            # List of tool definitions
            expected_tool_names = set()
            for tool_def in tool_schema:
                if isinstance(tool_def, dict) and "name" in tool_def:
                    expected_tool_names.add(tool_def["name"])
                elif isinstance(tool_def, dict) and "function" in tool_def:
                    expected_tool_names.add(tool_def["function"].get("name", ""))
        else:
            logger.warning(
                f"Couldn't validate tool schema. Skipping tool validation. Received: {tool_schema}"
            )
            return

        # Get provided tool names
        provided_tool_names = set()
        for tool in provided_tools:
            if isinstance(tool, dict):
                if "name" in tool:
                    provided_tool_names.add(tool["name"])
            elif hasattr(tool, "name"):
                provided_tool_names.add(tool.name)

        # Check for missing tools
        missing_tools = expected_tool_names - provided_tool_names
        if missing_tools:
            logger.warning(
                f"Freeplay prompt '{self._template_prompt.prompt_info.template_name}' expects tools {missing_tools} "
                f"but they were not provided to create_agent(). "
                f"The agent may not function as expected."
            )

        # Check for extra tools
        extra_tools = provided_tool_names - expected_tool_names
        if extra_tools:
            logger.warning(
                f"Tools {extra_tools} were provided to create_agent() but are not "
                f"in Freeplay prompt '{self._template_prompt.prompt_info.template_name}' tool schema. "
            )

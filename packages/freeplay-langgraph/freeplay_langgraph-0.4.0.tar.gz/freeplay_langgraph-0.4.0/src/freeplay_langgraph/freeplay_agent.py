"""
FreeplayAgent wrapper for LangGraph agents.

This module provides a wrapper around LangGraph agents using LangChain's official
RunnableBindingBase pattern to automatically inject Freeplay metadata into all
invocations via config_factories.
"""

import json
import logging
from typing import Any, Callable, Optional, TypeVar

from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.runnables.base import RunnableBindingBase

from freeplay_langgraph.otel_attributes import FreeplayOTelAttributes

logger = logging.getLogger(__name__)

# Type variables for generic typing
Input = TypeVar("Input")
Output = TypeVar("Output")


class FreeplayAgent(RunnableBindingBase[Input, Output]):
    """
    Wraps LangGraph agents using LangChain's official RunnableBindingBase pattern.

    This wrapper automatically injects Freeplay metadata into all invocation methods
    (invoke, ainvoke, stream, astream, batch, abatch, astream_events) via LangChain's
    config_factories mechanism.

    Variables are now passed in the input dict and handled by Freeplay middleware.
    All invocation methods work directly. For state management operations, use unwrap().

    Args:
        agent: The underlying LangGraph agent
        metadata_builder: Callable that builds Freeplay metadata dict
        fail_on_metadata_error: If True, raises exceptions when metadata building fails

    Example:
        >>> agent = freeplay.create_agent(prompt_name="assistant", tools=[...])
        >>>
        >>> # Invoke with variables in input dict
        >>> result = agent.invoke({
        ...     "messages": [HumanMessage("Hi")],
        ...     "variables": {"location": "SF"}
        ... })
        >>>
        >>> # Template-only (no messages key)
        >>> result = agent.invoke({"variables": {"location": "NYC"}})
        >>>
        >>> # State management via unwrap()
        >>> state = agent.unwrap().get_state(config)
    """

    def __init__(
        self,
        agent: Runnable[Input, Output],
        metadata_builder: Callable[[], dict[str, Any]],
        fail_on_metadata_error: bool = True,
    ):
        """
        Initialize the FreeplayAgent wrapper.

        Creates a config_factory that injects Freeplay metadata into all invocations.
        This factory is passed to RunnableBindingBase which handles calling it for
        all invocation methods automatically.

        Args:
            agent: The underlying LangGraph agent
            metadata_builder: Callable that builds Freeplay metadata dict
            fail_on_metadata_error: If True, raises exceptions when metadata building fails
        """
        self._fail_on_metadata_error = fail_on_metadata_error

        def inject_freeplay_metadata(config: RunnableConfig) -> RunnableConfig:
            """
            Config factory that injects Freeplay metadata.

            This function is called by RunnableBindingBase for every invocation
            to merge Freeplay metadata into the config.

            Args:
                config: The current RunnableConfig (may be empty dict)

            Returns:
                New RunnableConfig with Freeplay metadata merged in

            Raises:
                Exception: If metadata building fails and fail_on_metadata_error is True
            """
            try:
                freeplay_metadata = metadata_builder()
            except Exception as e:
                if fail_on_metadata_error:
                    raise
                logger.warning(f"Failed to build Freeplay metadata: {e}", exc_info=True)
                return config
            else:
                existing_metadata = config.get("metadata", {})
                if not isinstance(existing_metadata, dict):
                    existing_metadata = {}

                return {
                    **config,
                    "metadata": {**existing_metadata, **freeplay_metadata},
                }

        # Initialize RunnableBindingBase with the agent and config factory
        super().__init__(
            bound=agent,
            config_factories=[inject_freeplay_metadata],
        )

    def _transform_variables_to_state_key(self, input: Input) -> Input:  # noqa: A002
        """
        Transform variables key to __freeplay_variables__ for state schema.

        Users pass {"variables": {...}} but state schema has __freeplay_variables__ field
        to avoid conflicts with custom user schemas.
        """
        if isinstance(input, dict) and "variables" in input:
            return {**input, "__freeplay_variables__": input.pop("variables")}  # type: ignore[assignment]
        return input

    def _inject_variables_metadata(
        self, input: Input, config: Optional[RunnableConfig]  # noqa: A002
    ) -> RunnableConfig:
        """
        Extract variables from input and inject into config metadata.

        This ensures variables are visible in Freeplay observability.
        """
        # Extract variables from input if present
        if isinstance(input, dict) and "__freeplay_variables__" in input:
            variables = input.get("__freeplay_variables__", {})
            if variables:
                config = config or {}
                if "metadata" not in config:
                    config["metadata"] = {}
                config["metadata"][
                    FreeplayOTelAttributes.FREEPLAY_INPUT_VARIABLES.value
                ] = json.dumps(variables)

        return config or {}

    def invoke(
        self,
        input: Input,  # noqa: A002
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Output:
        """Override invoke to inject variables metadata."""
        transformed = self._transform_variables_to_state_key(input)
        config = self._inject_variables_metadata(transformed, config)
        return super().invoke(transformed, config, **kwargs)

    async def ainvoke(
        self,
        input: Input,  # noqa: A002
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Output:
        """Override ainvoke to inject variables metadata."""
        transformed = self._transform_variables_to_state_key(input)
        config = self._inject_variables_metadata(transformed, config)
        return await super().ainvoke(transformed, config, **kwargs)

    def stream(
        self,
        input: Input,  # noqa: A002
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ):
        """Override stream to inject variables metadata."""
        transformed = self._transform_variables_to_state_key(input)
        config = self._inject_variables_metadata(transformed, config)
        yield from super().stream(transformed, config, **kwargs)

    async def astream(
        self,
        input: Input,  # noqa: A002
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ):
        """Override astream to inject variables metadata."""
        transformed = self._transform_variables_to_state_key(input)
        config = self._inject_variables_metadata(transformed, config)
        async for chunk in super().astream(transformed, config, **kwargs):
            yield chunk

    def batch(
        self,
        inputs: list[Input],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> list[Output]:
        """Override batch to inject variables metadata for each input."""
        # Transform all inputs
        transformed_inputs = [
            self._transform_variables_to_state_key(inp) for inp in inputs
        ]

        # Extract variables from first input for metadata
        if transformed_inputs:
            config = self._inject_variables_metadata(transformed_inputs[0], config)

        return super().batch(transformed_inputs, config, **kwargs)

    async def abatch(
        self,
        inputs: list[Input],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> list[Output]:
        """Override abatch to inject variables metadata for each input."""
        # Transform all inputs
        transformed_inputs = [
            self._transform_variables_to_state_key(inp) for inp in inputs
        ]

        # Extract variables from first input for metadata
        if transformed_inputs:
            config = self._inject_variables_metadata(transformed_inputs[0], config)

        return await super().abatch(transformed_inputs, config, **kwargs)

    def unwrap(self) -> Runnable[Input, Output]:
        """
        Access the underlying agent for state management operations.

        Use this method to access CompiledStateGraph-specific methods that are
        not part of the core Runnable interface:

        State Management:
        - get_state(config, *, subgraphs=False) / aget_state(config, *, subgraphs=False)
        - update_state(config, values, as_node=None) / aupdate_state(config, values, as_node=None)
        - get_state_history(config, *, filter=None, before=None, limit=None)
        - aget_state_history(config, *, filter=None, before=None, limit=None)
        - bulk_update_state(config, updates) / abulk_update_state(config, updates)

        Multi-Agent Systems:
        - get_subgraphs(namespace=None, *, recurse=False) / aget_subgraphs(...)

        Cache Management:
        - clear_cache() / aclear_cache()

        Example:
            >>> agent = freeplay.create_agent(
            ...     prompt_name="assistant",
            ...     checkpointer=MemorySaver()
            ... )
            >>>
            >>> # Invoke with variables
            >>> result = agent.invoke({
            ...     "messages": [HumanMessage("Hello")],
            ...     "variables": {"company": "Acme"}
            ... })
            >>>
            >>> # State management via unwrap()
            >>> config = {"configurable": {"thread_id": "thread-123"}}
            >>> state = agent.unwrap().get_state(config)
            >>> print(f"Current messages: {state.values['messages']}")
            >>>
            >>> # Update state for human-in-the-loop workflows
            >>> agent.unwrap().update_state(
            ...     config,
            ...     {"approval": "granted"},
            ...     as_node="human"
            ... )

        For full type safety with state methods, use cast:
            >>> from typing import cast
            >>> from langgraph.graph.state import CompiledStateGraph
            >>> compiled = cast(CompiledStateGraph, agent.unwrap())
            >>> state = compiled.get_state(config)  # Full type hints

        Returns:
            The wrapped LangGraph agent (typically CompiledStateGraph)
        """
        return self.bound

    def __repr__(self) -> str:
        """String representation of the wrapper."""
        return f"FreeplayAgent(bound={self.bound!r})"

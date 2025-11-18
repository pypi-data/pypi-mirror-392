import json
import logging
import os
from collections.abc import Sequence
from typing import Annotated, Any, Callable, ClassVar, Optional, Union

from freeplay.freeplay import Freeplay
from freeplay.model import InputVariables
from freeplay.resources.prompts import PromptInfo, TemplateResolver
from freeplay.support import TemplateChatMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AnyMessage,
    BaseMessage,
)
from langchain_core.tools import BaseTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.message import add_messages
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from typing_extensions import TypedDict

from freeplay_langgraph.freeplay_agent import FreeplayAgent
from freeplay_langgraph.normalized_message import (
    normalize_message_to_openai_message,
)
from freeplay_langgraph.otel_attributes import FreeplayOTelAttributes

logger = logging.getLogger(__name__)


class FreeplayLangGraph:
    """Freeplay LangGraph integration with observability and prompt management."""

    _instance: ClassVar[Optional["FreeplayLangGraph"]] = None

    # Class-level configuration (shared singleton state)
    client: ClassVar[Freeplay]
    project_id: ClassVar[str]

    # Tracer for cleanup
    _tracer_provider: ClassVar[Optional[trace_sdk.TracerProvider]] = None

    def __new__(
        cls,
        freeplay_api_url: Optional[str] = None,  # noqa: ARG004
        freeplay_api_key: Optional[str] = None,  # noqa: ARG004
        project_id: Optional[str] = None,  # noqa: ARG004
        template_resolver: Optional[TemplateResolver] = None,  # noqa: ARG004
    ):
        """
        Create or return the singleton instance.

        This method ensures only one instance of FreeplayLangGraph exists per process.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        freeplay_api_url: Optional[str] = None,
        freeplay_api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        template_resolver: Optional[TemplateResolver] = None,
    ):
        """
        Initialize Freeplay LangGraph client.

        Note: Only the first call to __init__ will configure the client.
        Subsequent calls will return the same instance and ignore new parameters.
        To reinitialize with different config, call uninitialize_instrumentation() first.

        Args:
            freeplay_api_url: Freeplay API URL (defaults to FREEPLAY_API_URL env var)
            freeplay_api_key: Freeplay API key (defaults to FREEPLAY_API_KEY env var)
            project_id: Freeplay project ID (defaults to FREEPLAY_PROJECT_ID env var)
            template_resolver: Optional custom template resolver for prompt management.
                             If not provided, uses the default APITemplateResolver.

        Example:
            # Initialize from environment variables
            freeplay = FreeplayLangGraph()

            # Or with explicit configuration
            freeplay = FreeplayLangGraph(
                freeplay_api_url="https://api.freeplay.ai/api",
                freeplay_api_key="fp_...",
                project_id="proj_123",
            )

            # With filesystem-based prompts (e.g., bundled with your app)
            from pathlib import Path
            from freeplay.resources.prompts import FilesystemTemplateResolver

            freeplay = FreeplayLangGraph(
                template_resolver=FilesystemTemplateResolver(Path("bundled_prompts"))
            )
        """
        # Skip if already initialized
        if hasattr(self.__class__, "client"):
            return

        # Get from environment if not provided
        freeplay_api_url = freeplay_api_url or os.environ.get("FREEPLAY_API_URL", "")
        freeplay_api_key = freeplay_api_key or os.environ.get("FREEPLAY_API_KEY", "")
        self.__class__.project_id = project_id or os.environ.get(
            "FREEPLAY_PROJECT_ID", ""
        )

        # Initialize Freeplay client at class level
        self.__class__.client = Freeplay(
            freeplay_api_key=freeplay_api_key,
            api_base=freeplay_api_url,
            template_resolver=template_resolver,
        )

        # Initialize instrumentation
        self._initialize_instrumentation(
            freeplay_api_url=freeplay_api_url,
            freeplay_api_key=freeplay_api_key,
            project_id=self.__class__.project_id,
        )

    @classmethod
    def _initialize_instrumentation(
        cls,
        freeplay_api_url: str,
        freeplay_api_key: str,
        project_id: str,
    ) -> None:
        """
        Initialize global OpenTelemetry instrumentation (once per process).

        Args:
            freeplay_api_url: Freeplay API URL
            freeplay_api_key: Freeplay API key
            project_id: Freeplay project ID
        """
        # Setup OTEL exporter
        exporter = OTLPSpanExporter(
            endpoint=f"{freeplay_api_url}/v0/otel/v1/traces",
            headers={
                "Authorization": f"Bearer {freeplay_api_key}",
                "X-Freeplay-Project-Id": project_id,
            },
        )

        tracer_provider = trace_sdk.TracerProvider()
        tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))

        # Optional console logging
        if os.environ.get("FREEPLAY_LOG_SPANS_TO_CONSOLE", "false").lower() == "true":
            tracer_provider.add_span_processor(
                SimpleSpanProcessor(ConsoleSpanExporter())
            )

        # Instrument LangChain (idempotent)
        LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

        # Store for cleanup
        cls._tracer_provider = tracer_provider

    @classmethod
    def uninitialize_instrumentation(cls) -> None:
        """
        Uninitialize instrumentation and clean up resources.

        Useful for testing or when switching projects. This will uninstrument
        LangChain and shutdown the tracer provider.
        """
        # Cleanup instrumentation
        LangChainInstrumentor().uninstrument()

        if cls._tracer_provider:
            cls._tracer_provider.shutdown()
            cls._tracer_provider = None

        # Reset singleton
        cls._instance = None
        if hasattr(cls, "client"):
            delattr(cls, "client")
        if hasattr(cls, "project_id"):
            delattr(cls, "project_id")

    @classmethod
    def is_instrumented(cls) -> bool:
        """
        Check if instrumentation is active.

        Returns:
            True if instrumentation is active, False otherwise
        """
        return cls._instance is not None

    def _prepare_model_with_prompt(  # noqa: PLR0913
        self,
        prompt_name: str,
        variables: InputVariables,
        environment: str,
        model: Optional[BaseChatModel],
        history: Optional[Sequence[BaseMessage]],
        tools: Optional[Sequence[Union[dict[str, Any], type, Callable, BaseTool]]],
        test_run_id: Optional[str] = None,
        test_case_id: Optional[str] = None,
    ) -> tuple[Any, Any]:
        """
        Prepare model with formatted prompt and metadata (internal helper).

        This method consolidates the common setup logic used by invoke, ainvoke,
        stream, and astream methods to eliminate code duplication.

        Args:
            prompt_name: Name of the prompt in Freeplay
            variables: Variables to render the prompt template
            environment: Environment to use
            model: Optional pre-instantiated model
            history: Optional conversation history
            tools: Optional tools to bind
            test_run_id: Optional test run ID
            test_case_id: Optional test case ID

        Returns:
            Tuple of (configured_model, formatted_prompt)
        """
        # Normalize history to OpenAI format for Freeplay SDK
        normalized_history = (
            [normalize_message_to_openai_message(msg) for msg in history]
            if history
            else None
        )

        # Get formatted prompt from Freeplay
        template_prompt = self.__class__.client.prompts.get(
            project_id=self.__class__.project_id,
            template_name=prompt_name,
            environment=environment,
        )

        # Auto-create model if not provided
        model_instance = model or FreeplayLangGraph.get_model(
            prompt_info=template_prompt.prompt_info
        )

        # Bind tools if provided
        if tools:
            model_instance = model_instance.bind_tools(tools)

        # Build Freeplay metadata
        freeplay_metadata = self.build_freeplay_metadata(
            variables=variables,
            prompt_info=template_prompt.prompt_info,
            environment=environment,
            test_run_id=test_run_id,
            test_case_id=test_case_id,
        )

        # Configure model with metadata
        configured_model = model_instance.with_config(
            config={"metadata": freeplay_metadata}
        )

        return configured_model, template_prompt.bind(
            variables=variables, history=normalized_history
        ).format("openai_chat")

    def invoke(  # noqa: PLR0913
        self,
        prompt_name: str,
        variables: InputVariables,
        environment: str = "latest",
        model: Optional[BaseChatModel] = None,
        history: Optional[Sequence[BaseMessage]] = None,
        tools: Optional[
            Sequence[Union[dict[str, Any], type, Callable, BaseTool]]
        ] = None,
        test_run_id: Optional[str] = None,
        test_case_id: Optional[str] = None,
        **invoke_kwargs,
    ) -> BaseMessage:
        """
        Invoke a model with a Freeplay-hosted prompt.

        Args:
            prompt_name: Name of the prompt in Freeplay
            variables: Variables to render the prompt template
            environment: Environment to use (e.g., "production", "staging", "latest")
            model: Optional pre-instantiated LangChain model. If not provided,
                   will attempt to auto-create based on Freeplay's model config.
            history: Optional conversation history as LangChain BaseMessage objects
            tools: Optional tools to bind to the model
            test_run_id: Optional test run ID for test execution tracking
            test_case_id: Optional test case ID for test execution tracking
            **invoke_kwargs: Additional arguments to pass to model.invoke()

        Returns:
            The model's response

        Raises:
            ImportError: If required provider package not installed
            ValueError: If provider not supported

        Example:
            freeplay = FreeplayLangGraph()

            # Call a Freeplay-hosted prompt with auto-instantiation
            response = freeplay.invoke(
                prompt_name="weather-assistant",
                variables={"city": "San Francisco"}
            )

            # Call with conversation history (LangGraph MessagesState)
            from langchain_core.messages import HumanMessage
            response = freeplay.invoke(
                prompt_name="weather-assistant",
                variables={"city": "SF"},
                history=[HumanMessage(content="Previous message")]
            )

            # Call with an explicit model
            from langchain_openai import ChatOpenAI
            model = ChatOpenAI(model="gpt-4", temperature=0)
            response = freeplay.invoke(
                prompt_name="weather-assistant",
                variables={"city": "SF"},
                model=model
            )
        """
        configured_model, formatted_prompt = self._prepare_model_with_prompt(
            prompt_name=prompt_name,
            variables=variables,
            environment=environment,
            model=model,
            history=history,
            tools=tools,
            test_run_id=test_run_id,
            test_case_id=test_case_id,
        )

        return configured_model.invoke(formatted_prompt.llm_prompt, **invoke_kwargs)

    async def ainvoke(  # noqa: PLR0913
        self,
        prompt_name: str,
        variables: InputVariables,
        environment: str = "latest",
        model: Optional[BaseChatModel] = None,
        history: Optional[Sequence[BaseMessage]] = None,
        tools: Optional[
            Sequence[Union[dict[str, Any], type, Callable, BaseTool]]
        ] = None,
        test_run_id: Optional[str] = None,
        test_case_id: Optional[str] = None,
        **invoke_kwargs,
    ) -> BaseMessage:
        """
        Async invoke a model with a Freeplay-hosted prompt.

        This is the async version of invoke(). All parameters are identical.

        Args:
            prompt_name: Name of the prompt in Freeplay
            variables: Variables to render the prompt template
            environment: Environment to use (e.g., "production", "staging", "latest")
            model: Optional pre-instantiated LangChain model. If not provided,
                   will attempt to auto-create based on Freeplay's model config.
            history: Optional conversation history as LangChain BaseMessage objects
            tools: Optional tools to bind to the model
            test_run_id: Optional test run ID for test execution tracking
            test_case_id: Optional test case ID for test execution tracking
            **invoke_kwargs: Additional arguments to pass to model.ainvoke()

        Returns:
            The model's response

        Raises:
            ImportError: If required provider package not installed
            ValueError: If provider not supported

        Example:
            freeplay = FreeplayLangGraph()

            # Async invocation
            response = await freeplay.ainvoke(
                prompt_name="weather-assistant",
                variables={"city": "San Francisco"}
            )
        """
        configured_model, formatted_prompt = self._prepare_model_with_prompt(
            prompt_name=prompt_name,
            variables=variables,
            environment=environment,
            model=model,
            history=history,
            tools=tools,
            test_run_id=test_run_id,
            test_case_id=test_case_id,
        )

        return await configured_model.ainvoke(
            formatted_prompt.llm_prompt, **invoke_kwargs
        )

    def stream(  # noqa: PLR0913
        self,
        prompt_name: str,
        variables: InputVariables,
        environment: str = "latest",
        model: Optional[BaseChatModel] = None,
        history: Optional[Sequence[BaseMessage]] = None,
        tools: Optional[
            Sequence[Union[dict[str, Any], type, Callable, BaseTool]]
        ] = None,
        test_run_id: Optional[str] = None,
        test_case_id: Optional[str] = None,
        **stream_kwargs,
    ):
        """
        Stream model responses with a Freeplay-hosted prompt.

        Args:
            prompt_name: Name of the prompt in Freeplay
            variables: Variables to render the prompt template
            environment: Environment to use (e.g., "production", "staging", "latest")
            model: Optional pre-instantiated LangChain model. If not provided,
                   will attempt to auto-create based on Freeplay's model config.
            history: Optional conversation history as LangChain BaseMessage objects
            tools: Optional tools to bind to the model
            test_run_id: Optional test run ID for test execution tracking
            test_case_id: Optional test case ID for test execution tracking
            **stream_kwargs: Additional arguments to pass to model.stream()

        Yields:
            Chunks from the model's streaming response

        Raises:
            ImportError: If required provider package not installed
            ValueError: If provider not supported

        Example:
            freeplay = FreeplayLangGraph()

            # Stream model responses
            for chunk in freeplay.stream(
                prompt_name="weather-assistant",
                variables={"city": "San Francisco"}
            ):
                print(chunk.content, end="", flush=True)
        """
        configured_model, formatted_prompt = self._prepare_model_with_prompt(
            prompt_name=prompt_name,
            variables=variables,
            environment=environment,
            model=model,
            history=history,
            tools=tools,
            test_run_id=test_run_id,
            test_case_id=test_case_id,
        )

        yield from configured_model.stream(formatted_prompt.llm_prompt, **stream_kwargs)

    async def astream(  # noqa: PLR0913
        self,
        prompt_name: str,
        variables: InputVariables,
        environment: str = "latest",
        model: Optional[BaseChatModel] = None,
        history: Optional[Sequence[BaseMessage]] = None,
        tools: Optional[
            Sequence[Union[dict[str, Any], type, Callable, BaseTool]]
        ] = None,
        test_run_id: Optional[str] = None,
        test_case_id: Optional[str] = None,
        **stream_kwargs,
    ):
        """
        Async stream model responses with a Freeplay-hosted prompt.

        Args:
            prompt_name: Name of the prompt in Freeplay
            variables: Variables to render the prompt template
            environment: Environment to use (e.g., "production", "staging", "latest")
            model: Optional pre-instantiated LangChain model. If not provided,
                   will attempt to auto-create based on Freeplay's model config.
            history: Optional conversation history as LangChain BaseMessage objects
            tools: Optional tools to bind to the model
            test_run_id: Optional test run ID for test execution tracking
            test_case_id: Optional test case ID for test execution tracking
            **stream_kwargs: Additional arguments to pass to model.astream()

        Yields:
            Chunks from the model's async streaming response

        Raises:
            ImportError: If required provider package not installed
            ValueError: If provider not supported

        Example:
            freeplay = FreeplayLangGraph()

            # Async stream model responses
            async for chunk in freeplay.astream(
                prompt_name="weather-assistant",
                variables={"city": "San Francisco"}
            ):
                print(chunk.content, end="", flush=True)
        """
        configured_model, formatted_prompt = self._prepare_model_with_prompt(
            prompt_name=prompt_name,
            variables=variables,
            environment=environment,
            model=model,
            history=history,
            tools=tools,
            test_run_id=test_run_id,
            test_case_id=test_case_id,
        )

        async for chunk in configured_model.astream(
            formatted_prompt.llm_prompt, **stream_kwargs
        ):
            yield chunk

    @staticmethod
    def _extend_state_schema_with_freeplay(state_schema: Optional[type]) -> type:
        """
        Extend state schema to include variables field for Freeplay.

        This allows variables to be passed per-invocation and accessed by middleware
        for dynamic prompt rendering. Works with both default schema and custom user schemas.

        Args:
            state_schema: User's state schema (TypedDict) or None for default

        Returns:
            Extended state schema with variables field

        Example:
            # With default schema
            schema = _extend_state_schema_with_freeplay(None)
            # Returns: FreeplayAgentState with messages and variables

            # With custom schema
            class MyState(TypedDict):
                messages: ...
                custom_field: str

            schema = _extend_state_schema_with_freeplay(MyState)
            # Returns: ExtendedState with messages, custom_field, and variables
        """

        if state_schema is None:
            # Create default schema with __freeplay_variables__
            class FreeplayAgentState(TypedDict, total=False):
                """Default agent state with Freeplay variables support."""

                messages: Annotated[list[AnyMessage], add_messages]
                __freeplay_variables__: dict

            # Make messages required
            FreeplayAgentState.__required_keys__ = frozenset(["messages"])

            return FreeplayAgentState

        # Extend user's custom schema with __freeplay_variables__ field
        class ExtendedState(state_schema, total=False):  # type: ignore[misc,valid-type]
            """Extended state schema with Freeplay variables support."""

            __freeplay_variables__: dict

        return ExtendedState

    def create_agent(  # noqa: PLR0913
        self,
        prompt_name: str,
        tools: Optional[
            Sequence[Union[dict[str, Any], type, Callable, BaseTool]]
        ] = None,
        environment: str = "latest",
        model: Optional[BaseChatModel] = None,
        state_schema: Optional[type] = None,
        context_schema: Optional[type] = None,
        middleware: Optional[Sequence[Any]] = None,
        response_format: Optional[Any] = None,
        checkpointer: Optional[BaseCheckpointSaver] = None,
        validate_tools: bool = True,
        **agent_kwargs: Any,
    ) -> FreeplayAgent:
        """
        Create a LangGraph agent with Freeplay-hosted prompt and full observability.

        This method wraps LangGraph's create_agent to provide seamless integration with
        Freeplay's prompt management, automatic model instantiation, and observability.

        Variables are now passed per invocation in the input dict, not at creation time.
        The Freeplay prompt is re-rendered on every model call with the current variables.

        Args:
            prompt_name: Name of the prompt in Freeplay
            tools: Optional tools to bind to the agent
            environment: Environment to use (e.g., "production", "staging", "latest")
            model: Optional pre-instantiated LangChain model. If not provided,
                   will attempt to auto-create based on Freeplay's model config.
            state_schema: Optional custom state schema (TypedDict)
            context_schema: Optional context schema for runtime context (TypedDict)
            middleware: Optional list of middleware to apply (Freeplay middleware prepended automatically)
            response_format: Optional structured output format (ToolStrategy or ProviderStrategy)
            checkpointer: Optional checkpointer for state persistence
            validate_tools: Whether to validate provided tools against Freeplay prompt schema (default: True)
            **agent_kwargs: Additional arguments to pass to LangGraph's create_agent

        Returns:
            FreeplayAgent wrapper around the compiled LangGraph agent

        Raises:
            ImportError: If required provider package not installed
            ValueError: If prompt has no system content

        Example:
            freeplay = FreeplayLangGraph()

            # Create agent (no variables at creation)
            agent = freeplay.create_agent(
                prompt_name="weather-assistant",
                tools=[get_weather_tool]
            )

            # Pass variables in input dict
            result = agent.invoke({
                "messages": [HumanMessage("What's the weather?")],
                "variables": {"location": "San Francisco", "company": "Acme"}
            })

            # Template-only (no messages)
            result = agent.invoke({
                "variables": {"location": "New York", "company": "Acme"}
            })

            # With user middleware
            from langchain.agents.middleware import wrap_model_call

            @wrap_model_call
            def custom_middleware(request, handler):
                # Custom logic
                return handler(request)

            agent = freeplay.create_agent(
                prompt_name="weather-assistant",
                tools=[get_weather_tool],
                middleware=[custom_middleware]  # Prepended after Freeplay middleware
            )
        """
        # Import create_agent from langchain.agents
        try:
            from langchain.agents import (  # noqa: PLC0415
                create_agent as lc_create_agent,
            )
        except ImportError as e:
            raise ImportError(
                "LangChain agents module is required. "
                "Install it with: pip install langchain>=1.0.0"
            ) from e

        # Import Freeplay middleware
        from freeplay_langgraph.middleware import (  # noqa: PLC0415
            FreeplayPromptMiddleware,
        )

        # Fetch formatted prompt once to get model info and validate
        # Use empty variables since actual variables come per invocation
        template_prompt = self.__class__.client.prompts.get(
            project_id=self.__class__.project_id,
            template_name=prompt_name,
            environment=environment,
        )

        # Validate that prompt has system content
        # Validate that prompt has exactly one system message
        system_messages = [
            msg
            for msg in template_prompt.messages
            if isinstance(msg, TemplateChatMessage) and msg.role == "system"
        ]

        if len(system_messages) == 0:
            raise ValueError(
                f"There is no system prompt for the agent. Update prompt: {prompt_name} in Freeplay to include a system prompt."
            )
        if len(system_messages) > 1:
            raise ValueError(
                f"Multiple system prompts found for the agent. Update prompt: {prompt_name} in Freeplay to include exactly one system prompt."
            )

        # If model not provided, auto-create based on provider
        model_instance = model or FreeplayLangGraph.get_model(
            prompt_info=template_prompt.prompt_info
        )

        # Create Freeplay middleware for dynamic prompt rendering
        freeplay_middleware = FreeplayPromptMiddleware(
            freeplay_client=self,
            template_prompt=template_prompt,
            environment=environment,
            validate_tools=validate_tools,
        )

        # Prepend Freeplay middleware to user's middleware
        all_middleware = [freeplay_middleware, *(middleware or [])]

        # Extend state schema to include __freeplay_variables__ field
        # This works with both default schema (None) and custom user schemas
        extended_state_schema = self._extend_state_schema_with_freeplay(state_schema)

        # Create agent using LangGraph's create_agent
        # No system_prompt parameter - middleware handles it dynamically
        agent = lc_create_agent(
            model=model_instance,
            tools=tools or [],
            system_prompt=None,  # Middleware sets this dynamically per call
            state_schema=extended_state_schema,  # Use extended schema with __freeplay_variables__
            context_schema=context_schema,
            middleware=all_middleware,
            response_format=response_format,
            checkpointer=checkpointer,
            **agent_kwargs,
        )

        # Create metadata builder as closure (lazy evaluation)
        def build_metadata() -> dict[str, Any]:
            return self.build_agent_metadata(
                prompt_info=template_prompt.prompt_info,
                environment=environment,
            )

        return FreeplayAgent(
            agent=agent,
            metadata_builder=build_metadata,
            fail_on_metadata_error=True,
        )

    def build_agent_metadata(
        self,
        prompt_info: PromptInfo,
        environment: str,
    ) -> dict[str, Any]:
        """
        Build Freeplay metadata dictionary for agent invocations.

        Agents do not include per-invocation variables or test tracking in base metadata
        since these are handled per-invocation via config overrides.

        Args:
            prompt_info: Prompt information from Freeplay containing template version and model config
            environment: Environment name (e.g., "production", "staging", "latest")

        Returns:
            Dictionary containing Freeplay metadata attributes for OTEL spans
        """
        return {
            FreeplayOTelAttributes.FREEPLAY_PROMPT_TEMPLATE_VERSION_ID.value: prompt_info.prompt_template_version_id,
            FreeplayOTelAttributes.FREEPLAY_ENVIRONMENT.value: environment,
        }

    def build_freeplay_metadata(
        self,
        variables: InputVariables,
        prompt_info: PromptInfo,
        environment: str,
        test_run_id: Optional[str] = None,
        test_case_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Build Freeplay metadata dictionary for OpenTelemetry tracing.

        Used by invoke/ainvoke/stream/astream methods for simple prompt invocations.

        Args:
            variables: Input variables used to render the prompt template
            prompt_info: Prompt information from Freeplay containing template version and model config
            environment: Environment name (e.g., "production", "staging", "latest")
            test_run_id: Optional test run ID for test execution tracking
            test_case_id: Optional test case ID for test execution tracking

        Returns:
            Dictionary containing Freeplay metadata attributes for OTEL spans
        """
        return {
            FreeplayOTelAttributes.FREEPLAY_INPUT_VARIABLES.value: json.dumps(
                variables
            ),
            FreeplayOTelAttributes.FREEPLAY_PROMPT_TEMPLATE_VERSION_ID.value: prompt_info.prompt_template_version_id,
            FreeplayOTelAttributes.FREEPLAY_ENVIRONMENT.value: environment,
            FreeplayOTelAttributes.FREEPLAY_TEST_RUN_ID.value: test_run_id,
            FreeplayOTelAttributes.FREEPLAY_TEST_CASE_ID.value: test_case_id,
        }

    @staticmethod
    def get_model(
        prompt_info: PromptInfo,
    ) -> Any:
        """
        Set a LangChain model for a given prompt info.

        This function checks if the required provider package is installed
        and creates the appropriate model instance.

        Args:
            prompt_info: Prompt info

        Returns:
            Instantiated LangChain model

        Raises:
            ImportError: If provider package not installed
            ValueError: If provider not supported
        """
        # Build model kwargs
        model_kwargs = {
            "model": prompt_info.model,
            **prompt_info.model_parameters,
        }

        # Try to import and instantiate based on provider
        if prompt_info.provider == "openai":
            try:
                from langchain_openai import ChatOpenAI  # noqa: PLC0415

                return ChatOpenAI(**model_kwargs)  # type: ignore[abstract]
            except ImportError as e:
                raise ImportError(
                    f"Provider '{prompt_info.provider}' requires 'langchain-openai' package. "
                    f"Install it with: pip install langchain-openai"
                ) from e

        elif prompt_info.provider == "anthropic":
            try:
                from langchain_anthropic import ChatAnthropic  # noqa: PLC0415

                return ChatAnthropic(**model_kwargs)  # type: ignore[abstract]
            except ImportError as e:
                raise ImportError(
                    f"Provider '{prompt_info.provider}' requires 'langchain-anthropic' package. "
                    f"Install it with: pip install langchain-anthropic"
                ) from e

        elif prompt_info.provider == "vertex":
            try:
                from langchain_google_vertexai import (  # noqa: PLC0415
                    ChatVertexAI,
                )

                return ChatVertexAI(**model_kwargs)  # type: ignore[abstract]
            except ImportError as e:
                raise ImportError(
                    f"Provider '{prompt_info.provider}' requires 'langchain-google-vertexai' package. "
                    f"Install it with: pip install langchain-google-vertexai"
                ) from e

        else:
            raise ValueError(f"Unsupported provider: '{prompt_info.provider}'. ")

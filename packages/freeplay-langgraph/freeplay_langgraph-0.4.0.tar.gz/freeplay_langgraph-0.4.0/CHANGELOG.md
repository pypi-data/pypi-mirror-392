# Changelog

Notable additions, fixes, or breaking changes to the Freeplay LangGraph integration.

## [0.4.0] - 2025-11-12

**Breaking Changes:**

- Variables are now passed in the input dict instead of as a parameter
  - Before: `agent.invoke({"messages": [...]}, variables={...})`
  - After: `agent.invoke({"messages": [...], "variables": {...}})`

- Removed `variables` parameter from `create_agent()` - all variables are now dynamic (passed per invocation)
  - Before: `create_agent(prompt_name="...", variables={"company": "Acme"})`
  - After: `create_agent(prompt_name="...")` (variables in invoke input)

- Template-only invocations use variables-only dict
  - Before: `agent.invoke(variables={...})`
  - After: `agent.invoke({"variables": {...}})`

**New Features:**

- Tool validation - warns when provided tools don't match Freeplay prompt's tool schema (can be disabled with `validate_tools=False`)

- System prompts are now re-rendered on every model call (not just at agent creation)

## [0.3.1] - 2025-11-12

- Add dynamic variables support for agent invocation - pass `variables` parameter to `invoke()`, `ainvoke()`, `stream()`, `astream()`, `batch()`, and `abatch()` to render template messages per call



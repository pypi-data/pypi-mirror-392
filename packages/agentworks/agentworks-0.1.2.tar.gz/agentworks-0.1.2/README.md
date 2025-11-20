# AgentWorks Python SDK

Instrument and observe your multi-agent AI systems with comprehensive tracing, including input/output capture, LLM prompts, and error stack traces.

## Installation

```bash
pip install agentworks
```

## Quick Start

```python
from agentworks import configure, trace_agent, trace_llm, trace_tool

# Configure SDK
configure(
    ingest_endpoint="http://localhost:8080/api",
    org_id="my-org",
    project_id="my-project",
    api_key="aw_...",  # Required for production
)

# Trace your agent with input/output
user_request = {"user_id": "123", "query": "Help me"}

with trace_agent("support-bot", input_data=user_request) as (span_id, capture_output):

    # Trace LLM calls with prompts
    system_prompt = "You are a helpful assistant."
    user_prompt = f"User asks: {user_request['query']}"

    with trace_llm(
        model="gpt-4",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.7
    ) as (llm_span_id, capture_llm):

        # Make your LLM call
        response = openai.chat.completions.create(...)

        # Capture the completion
        capture_llm(
            completion=response.choices[0].message.content,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens
        )

    # Capture agent output
    result = {"response": response, "status": "resolved"}
    capture_output(result)
```

## Features

- **Input/Output Capture**: Automatically capture and visualize agent and tool inputs/outputs
- **LLM Prompt Tracking**: Separate system and user prompts with completions
- **Error Stack Traces**: Full Python stack traces captured automatically
- **Workflow Orchestration**: New `trace_workflow()` for multi-agent coordination
- **Zero-overhead instrumentation**: <5ms latency per span
- **Automatic cost tracking**: Built-in pricing for OpenAI, Anthropic, Google
- **PII detection & redaction**: Protect sensitive data automatically
- **W3C trace propagation**: Compatible with OpenTelemetry
- **Framework agnostic**: Works with any Python agent framework

## API Reference

### Configuration

```python
configure(
    ingest_endpoint="http://localhost:8080/api",  # AgentWorks API endpoint
    api_key="aw_...",                             # API key (required for production)
    org_id="my-org",                              # Organization ID
    project_id="my-project",                      # Project ID
    redact_pii=True,                              # Enable PII redaction
    debug=False,                                  # Enable debug logging
)
```

### Tracing

#### `trace_workflow(name, input_data=None, **attrs)` ✨ NEW

Trace a workflow execution with input/output capture.

**Returns**: `(span_id, capture_output_callback)`

```python
with trace_workflow(
    "Document Pipeline",
    input_data={"doc_id": "123", "action": "process"}
) as (workflow_id, capture_output):

    # Orchestrate multiple agents
    result = run_pipeline()

    # Capture workflow output
    capture_output({"status": "completed", "result": result})
```

#### `trace_agent(agent_id, workflow_id=None, input_data=None, **attrs)` 🔄 UPDATED

Trace an agent execution with input/output capture.

**Returns**: `(span_id, capture_output_callback)`

```python
# NEW: With input/output capture
with trace_agent(
    "support-bot",
    workflow_id="ticket-123",
    input_data={"user_id": "456", "message": "Help"}
) as (span_id, capture_output):

    result = process_request()
    capture_output(result)  # Capture output

# OLD: Still works for backward compatibility
with trace_agent("support-bot", workflow_id="ticket-123") as (span_id, _):
    # No input/output capture
    pass
```

#### `trace_llm(model, system_prompt="", user_prompt="", **attrs)` ✨ NEW

Trace an LLM call with separate system and user prompts.

**Returns**: `(span_id, capture_output_callback)`

**Callback signature**: `capture_output(completion: str, prompt_tokens: int, completion_tokens: int)`

```python
with trace_llm(
    model="gpt-4",
    system_prompt="You are a helpful assistant.",
    user_prompt="What is the weather?",
    temperature=0.7,
    max_tokens=500
) as (llm_span_id, capture_llm):

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the weather?"}
        ]
    )

    # Capture completion and tokens
    capture_llm(
        completion=response.choices[0].message.content,
        prompt_tokens=response.usage.prompt_tokens,
        completion_tokens=response.usage.completion_tokens
    )

# In dashboard, you'll see:
# - System Prompt (collapsible)
# - User Prompt (collapsible)
# - Completion (collapsible)
# - Token usage and cost
```

#### `trace_tool(name, input_data=None, **attrs)` 🔄 UPDATED

Trace a tool execution with input/output capture.

**Returns**: `(span_id, capture_output_callback)`

```python
# NEW: With input/output capture
with trace_tool(
    "stripe_refund",
    input_data={"amount": "50.00", "customer_id": "cus_123"}
) as (span_id, capture_output):

    result = stripe.refund(amount=50.00, customer="cus_123")
    capture_output(result)

# OLD: Still works for backward compatibility
with trace_tool("stripe_refund", amount="50.00") as (span_id, _):
    result = stripe.refund(amount=50.00)
```

#### `trace_decision(policy="default", **attrs)`

Trace a decision point.

```python
with trace_decision(policy="routing-v1", task="classification") as span_id:
    model = select_model(task)
```

#### `llm_call(model, provider, prompt, completion, prompt_tokens, completion_tokens, **attrs)` 📦 LEGACY

**Note**: Consider using `trace_llm()` for better prompt tracking.

Trace an LLM call with automatic cost calculation and PII detection.

```python
result = llm_call(
    model="gpt-4",
    provider="openai",
    prompt="Classify: ...",
    completion="Category: Support",
    prompt_tokens=100,
    completion_tokens=10,
    temperature=0.7,
)
# Returns: {"trace_id": "...", "span_id": "...", "cost_usd": 0.0045, "pii_detected": []}
```

### Utilities

#### `get_current_trace_id()`

Get the current trace ID.

```python
trace_id = get_current_trace_id()
```

#### `get_current_span_id()`

Get the current span ID.

```python
span_id = get_current_span_id()
```

## Error Handling

Errors and stack traces are automatically captured:

```python
with trace_agent("validator", input_data=data) as (span_id, capture):
    try:
        validated = validate_data(data)
        capture(validated)
    except ValueError as e:
        # Error type, message, and full stack trace are captured automatically
        raise  # Re-raise to propagate

# Dashboard will show:
# - Error Type: ValueError
# - Error Message: "..."
# - Stack Trace: Full Python traceback (expandable)
```

## Supported Models

The SDK includes built-in pricing for:

- **OpenAI**: GPT-4, GPT-4 Turbo, GPT-4o, GPT-3.5 Turbo
- **Anthropic**: Claude 3 Opus, Sonnet, Haiku, Claude 3.5 Sonnet
- **Google**: Gemini Pro, Gemini 1.5 Pro/Flash

## PII Detection

Automatically detects and redacts:

- Email addresses
- Phone numbers
- Social Security Numbers
- Credit card numbers
- API keys

Configure PII patterns:

```python
configure(
    redact_pii=True,
    pii_patterns="email,phone,ssn,credit_card,api_key",
)
```

## Examples

### Complete Workflow Example

See `examples/comprehensive_trace_demo.py` for a full demonstration:

```bash
cd packages/sdk-python
python examples/comprehensive_trace_demo.py
```

This example includes:
- ✅ Workflow orchestration with `trace_workflow()`
- ✅ Multiple agents with input/output
- ✅ LLM calls with system/user prompts
- ✅ Tool calls with input/output
- ✅ Error handling with stack traces
- ✅ Cost tracking
- ✅ PII detection

### Multi-Agent System

```python
with trace_workflow("Document Processing", input_data={"doc_id": "123"}) as (wf_id, capture_wf):

    # Agent 1: Extract data
    with trace_agent("extractor", input_data={"doc_id": "123"}) as (id1, capture1):
        extracted = extract_data(doc)
        capture1(extracted)

    # Agent 2: Analyze with LLM
    with trace_agent("analyzer", input_data=extracted) as (id2, capture2):
        system = "You are a data analyst."
        user = f"Analyze: {extracted}"

        with trace_llm("gpt-4", system_prompt=system, user_prompt=user) as (llm_id, capture_llm):
            response = call_openai()
            capture_llm(response.content, response.usage.prompt_tokens, response.usage.completion_tokens)

        capture2({"analysis": response})

    # Agent 3: Generate report
    with trace_agent("reporter", input_data=response) as (id3, capture3):
        report = generate_report(response)
        capture3(report)

    capture_wf({"final_report": report})
```

### Tool Calling

```python
with trace_agent("assistant", input_data=user_query) as (agent_id, capture_agent):

    # Database search tool
    with trace_tool("db_search", input_data={"query": query}) as (tool_id, capture_tool):
        results = database.search(query)
        capture_tool(results)

    # API call tool
    with trace_tool("api_fetch", input_data={"id": results[0].id}) as (tool_id, capture_tool):
        data = api.get(results[0].id)
        capture_tool(data)

    capture_agent({"results": results, "details": data})
```

## What You'll See in the Dashboard

When you click on a span in the dashboard:

### For Agent/Tool Spans:
- **Input section** - The `input_data` you provided (expandable, copy, download)
- **Output section** - The data you captured with `capture_output()` (expandable, copy, download)
- **Timing** - Start time, end time, duration
- **Attributes** - All custom attributes
- **Error details** - If failed, includes type, message, and full stack trace

### For LLM Spans:
- **System Prompt** - Separate collapsible section
- **User Prompt** - Separate collapsible section
- **Completion** - Separate collapsible section
- **Tokens** - Input tokens, output tokens, total tokens
- **Cost** - Calculated cost in USD
- **Model details** - Model name, provider, temperature, etc.

## Migration Guide (v0.1.x → v0.2.x)

### Breaking Changes

The `trace_agent()` and `trace_tool()` now return a tuple instead of just `span_id`:

**Before (v0.1.x)**:
```python
with trace_agent("bot") as span_id:
    result = process()
```

**After (v0.2.x)**:
```python
# Option 1: Use both values
with trace_agent("bot", input_data=request) as (span_id, capture_output):
    result = process()
    capture_output(result)

# Option 2: Ignore capture_output for backward compatibility
with trace_agent("bot") as (span_id, _):
    result = process()  # No input/output capture
```

### New Functions

- `trace_llm()` - For LLM calls with separated prompts
- `trace_workflow()` - For workflow orchestration

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run linter
poetry run ruff check agentworks

# Type check
poetry run mypy agentworks
```

## License

MIT

## Links

- [Getting Started Guide](../../GETTING_STARTED.md)
- [Complete Example](examples/comprehensive_trace_demo.py)
- [Change Log](../../CHANGES_PAYLOAD_FEATURE.md)
- [Main Repository](https://github.com/agentworks/agentworks)

"""Tracing context managers and utilities."""

import hashlib
import json
import time
import traceback
from collections.abc import Callable, Generator
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

from agentworks.config import get_config
from agentworks.cost import calculate_cost
from agentworks.otlp import send_span_to_ingest
from agentworks.pii import redact_pii
from agentworks.utils import generate_span_id, generate_trace_id

# Context variables for trace propagation
_trace_id_var: ContextVar[str | None] = ContextVar("trace_id", default=None)
_span_id_var: ContextVar[str | None] = ContextVar("span_id", default=None)
_parent_span_id_var: ContextVar[str | None] = ContextVar("parent_span_id", default=None)

# Global storage for payloads to be sent with spans
_pending_payloads: list[dict[str, Any]] = []


def _serialize_data(data: Any) -> str:
    """Serialize data to string format."""
    if isinstance(data, str):
        return data
    elif isinstance(data, dict | list):
        return json.dumps(data, ensure_ascii=False, default=str)
    else:
        return str(data)


def _store_payload(trace_id: str, span_id: str, kind: str, data: Any) -> None:
    """Store payload for later transmission."""
    content = _serialize_data(data)
    content_bytes = content.encode("utf-8")

    payload = {
        "trace_id": trace_id,
        "span_id": span_id,
        "kind": kind,
        "content": content,
        "sha256": hashlib.sha256(content_bytes).hexdigest(),
        "size_bytes": len(content_bytes),
        "ts": datetime.now(timezone.utc),
    }

    _pending_payloads.append(payload)


def get_current_trace_id() -> str:
    """Get current trace ID, creating one if needed."""
    trace_id = _trace_id_var.get()
    if trace_id is None:
        trace_id = generate_trace_id()
        _trace_id_var.set(trace_id)
    return trace_id


def get_current_span_id() -> str | None:
    """Get current span ID."""
    return _span_id_var.get()


@contextmanager
def trace_agent(
    agent_id: str,
    workflow_id: str | None = None,
    input_data: Any = None,
    **attrs: str,
) -> Generator[tuple[str, Callable[[Any], None]], None, None]:
    """
    Trace an agent execution.

    Args:
        agent_id: Unique identifier for the agent
        workflow_id: Optional workflow identifier
        input_data: Optional input data to capture
        **attrs: Additional attributes to attach to the span

    Yields:
        Tuple of (span_id, capture_output) where capture_output is a function
        to capture the output data

    Example:
        with trace_agent("support-bot", input_data=request) as (span_id, capture_output):
            result = process_request(request)
            capture_output(result)  # Capture output
            return result
    """
    config = get_config()

    # Generate IDs
    trace_id = get_current_trace_id()
    span_id = generate_span_id()
    parent_span_id = _span_id_var.get()

    # Set current span
    token_span = _span_id_var.set(span_id)
    token_parent = _parent_span_id_var.set(parent_span_id)

    start_time = time.time()
    error_type = ""
    error_msg = ""
    error_stack = ""
    status = "ok"
    has_input = 0
    has_output = 0

    # Store input if provided
    if input_data is not None:
        _store_payload(trace_id, span_id, "input", input_data)
        has_input = 1

    # Create capture_output function
    def capture_output(data: Any) -> None:
        nonlocal has_output
        _store_payload(trace_id, span_id, "output", data)
        has_output = 1

    try:
        yield span_id, capture_output
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        error_stack = traceback.format_exc()
        status = "error"
        raise
    finally:
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        # Build attributes
        span_attrs: dict[str, str] = {
            "aw.agent_id": agent_id,
            "aw.kind": "agent",
            "aw.sdk_name": "agentworks-python",
            "aw.sdk_language": "python",
        }

        if workflow_id:
            span_attrs["aw.workflow_id"] = workflow_id

        # Convert all attr values to strings for validation
        for key, value in attrs.items():
            span_attrs[key] = str(value)

        # Send span
        send_span_to_ingest(
            org_id=config.org_id,
            project_id=config.project_id,
            trace_id=trace_id,
            span_id=span_id,
            parent_id=parent_span_id or "",
            ts=datetime.fromtimestamp(start_time, tz=timezone.utc),
            kind="agent",
            name=agent_id,
            status=status,
            latency_ms=latency_ms,
            attrs=span_attrs,
            error_type=error_type,
            error_msg=error_msg,
            has_input=has_input,
            has_output=has_output,
            error_stack=error_stack,
        )

        # Reset context
        _span_id_var.reset(token_span)
        _parent_span_id_var.reset(token_parent)


@contextmanager
def trace_tool(
    name: str,
    input_data: Any = None,
    **attrs: str,
) -> Generator[tuple[str, Callable[[Any], None]], None, None]:
    """
    Trace a tool execution.

    Args:
        name: Tool name
        input_data: Optional input data to capture
        **attrs: Additional attributes

    Yields:
        Tuple of (span_id, capture_output)

    Example:
        with trace_tool("fetch_user_data", input_data={"user_id": 123}) as (span_id, capture_output):
            user = fetch_user_data(user_id)
            capture_output(user)  # Capture output
    """
    config = get_config()

    trace_id = get_current_trace_id()
    span_id = generate_span_id()
    parent_span_id = _span_id_var.get()

    token_span = _span_id_var.set(span_id)
    token_parent = _parent_span_id_var.set(parent_span_id)

    start_time = time.time()
    error_type = ""
    error_msg = ""
    error_stack = ""
    status = "ok"
    has_input = 0
    has_output = 0

    # Store input if provided
    if input_data is not None:
        _store_payload(trace_id, span_id, "input", input_data)
        has_input = 1

    # Create capture_output function
    def capture_output(data: Any) -> None:
        nonlocal has_output
        _store_payload(trace_id, span_id, "output", data)
        has_output = 1

    try:
        yield span_id, capture_output
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        error_stack = traceback.format_exc()
        status = "error"
        raise
    finally:
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        span_attrs: dict[str, str] = {
            "aw.tool": name,
            "aw.kind": "tool",
            "aw.sdk_name": "agentworks-python",
            "aw.sdk_language": "python",
        }
        # Convert all attr values to strings for validation
        for key, value in attrs.items():
            span_attrs[key] = str(value)

        send_span_to_ingest(
            org_id=config.org_id,
            project_id=config.project_id,
            trace_id=trace_id,
            span_id=span_id,
            parent_id=parent_span_id or "",
            ts=datetime.fromtimestamp(start_time, tz=timezone.utc),
            kind="tool",
            name=name,
            status=status,
            latency_ms=latency_ms,
            attrs=span_attrs,
            error_type=error_type,
            error_msg=error_msg,
            has_input=has_input,
            has_output=has_output,
            error_stack=error_stack,
        )

        _span_id_var.reset(token_span)
        _parent_span_id_var.reset(token_parent)


@contextmanager
def trace_decision(
    policy: str = "default",
    **attrs: str,
) -> Generator[str, None, None]:
    """
    Trace a decision point.

    Args:
        policy: Policy name
        **attrs: Additional attributes

    Yields:
        span_id: The generated span ID
    """
    config = get_config()

    trace_id = get_current_trace_id()
    span_id = generate_span_id()
    parent_span_id = _span_id_var.get()

    token_span = _span_id_var.set(span_id)
    token_parent = _parent_span_id_var.set(parent_span_id)

    start_time = time.time()

    try:
        yield span_id
    finally:
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        span_attrs: dict[str, str] = {
            "aw.policy": policy,
            "aw.kind": "decision",
            "aw.sdk_name": "agentworks-python",
            "aw.sdk_language": "python",
        }
        # Convert all attr values to strings for validation
        for key, value in attrs.items():
            span_attrs[key] = str(value)

        send_span_to_ingest(
            org_id=config.org_id,
            project_id=config.project_id,
            trace_id=trace_id,
            span_id=span_id,
            parent_id=parent_span_id or "",
            ts=datetime.fromtimestamp(start_time, tz=timezone.utc),
            kind="decision",
            name=f"decision:{policy}",
            status="ok",
            latency_ms=latency_ms,
            attrs=span_attrs,
        )

        _span_id_var.reset(token_span)
        _parent_span_id_var.reset(token_parent)


@contextmanager
def trace_llm(
    model: str,
    system_prompt: str = "",
    user_prompt: str = "",
    **attrs: str,
) -> Generator[tuple[str, Callable[[str, int, int], None]], None, None]:
    """
    Trace an LLM call using a context manager.

    Args:
        model: Model name (e.g., "gpt-4", "claude-3-opus")
        system_prompt: System prompt
        user_prompt: User prompt
        **attrs: Additional attributes (provider, temperature, max_tokens, etc.)

    Yields:
        Tuple of (span_id, capture_output) where capture_output is a function
        to capture the completion and token counts

    Example:
        with trace_llm("gpt-4", system_prompt=sys_prompt, user_prompt=usr_prompt) as (span_id, capture_output):
            response = openai_client.chat.completions.create(...)
            capture_output(
                completion=response.choices[0].message.content,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
            )
    """
    config = get_config()

    trace_id = get_current_trace_id()
    span_id = generate_span_id()
    parent_span_id = _span_id_var.get()

    # Set current span
    token_span = _span_id_var.set(span_id)
    token_parent = _parent_span_id_var.set(parent_span_id)

    start_time = time.time()
    error_type = ""
    error_msg = ""
    error_stack = ""
    status = "ok"
    has_prompt = 0
    has_output = 0
    captured_prompt_tokens = 0
    captured_completion_tokens = 0
    completion_text = ""

    # Store prompts as separate payloads
    if system_prompt:
        _store_payload(trace_id, span_id, "system_prompt", system_prompt)
        has_prompt = 1
    if user_prompt:
        _store_payload(trace_id, span_id, "user_prompt", user_prompt)
        has_prompt = 1

    # Capture function that can be called from within the context
    def capture_llm_output(completion: str, prompt_tokens: int, completion_tokens: int) -> None:
        nonlocal has_output, completion_text, captured_prompt_tokens, captured_completion_tokens
        completion_text = completion
        captured_prompt_tokens = prompt_tokens
        captured_completion_tokens = completion_tokens
        _store_payload(trace_id, span_id, "completion", completion)
        has_output = 1

    try:
        yield span_id, capture_llm_output
    except Exception as e:
        status = "error"
        error_type = type(e).__name__
        error_msg = str(e)
        error_stack = traceback.format_exc()
        raise
    finally:
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        # PII detection
        pii_types: list[str] = []
        all_text = f"{system_prompt} {user_prompt} {completion_text}"
        if config.redact_pii:
            _, pii_types = redact_pii(all_text)

        # Calculate cost
        cost_usd = calculate_cost(model, captured_prompt_tokens, captured_completion_tokens)

        # Extract provider from attrs or default
        provider = attrs.get("provider", "openai")

        # Build attributes
        span_attrs: dict[str, str] = {
            "aw.model": model,
            "aw.provider": provider,
            "aw.kind": "llm",
            "aw.sdk_name": "agentworks-python",
            "aw.sdk_language": "python",
        }

        # Add optional attributes
        for key, value in attrs.items():
            span_attrs[f"aw.{key}"] = str(value)

        if pii_types:
            span_attrs["aw.pii_types"] = ",".join(pii_types)

        send_span_to_ingest(
            org_id=config.org_id,
            project_id=config.project_id,
            trace_id=trace_id,
            span_id=span_id,
            parent_id=parent_span_id or "",
            ts=datetime.fromtimestamp(start_time, tz=timezone.utc),
            kind="llm",
            name=f"{provider}:{model}",
            status=status,
            latency_ms=latency_ms,
            attrs=span_attrs,
            error_type=error_type,
            error_msg=error_msg,
            prompt_tokens=captured_prompt_tokens,
            completion_tokens=captured_completion_tokens,
            total_tokens=captured_prompt_tokens + captured_completion_tokens,
            cost_usd=cost_usd,
            pii_flag=1 if pii_types else 0,
            has_prompt=has_prompt,
            has_output=has_output,
            error_stack=error_stack,
        )

        _span_id_var.reset(token_span)
        _parent_span_id_var.reset(token_parent)


@contextmanager
def trace_workflow(
    name: str,
    input_data: Any = None,
    **attrs: str,
) -> Generator[tuple[str, Callable[[Any], None]], None, None]:
    """
    Trace a workflow execution.

    Args:
        name: Workflow name
        input_data: Optional input data to capture
        **attrs: Additional attributes to attach to the span

    Yields:
        Tuple of (span_id, capture_output) where capture_output is a function
        to capture the output data

    Example:
        with trace_workflow("data-pipeline", input_data=config) as (span_id, capture_output):
            result = run_pipeline(config)
            capture_output(result)  # Capture output
            return result
    """
    config = get_config()

    # Generate IDs - workflow starts a new trace
    trace_id = generate_trace_id()
    _trace_id_var.set(trace_id)
    span_id = generate_span_id()
    parent_span_id = _span_id_var.get()

    # Set current span
    token_span = _span_id_var.set(span_id)
    token_parent = _parent_span_id_var.set(parent_span_id)

    start_time = time.time()
    error_type = ""
    error_msg = ""
    error_stack = ""
    status = "ok"
    has_input = 0
    has_output = 0

    # Store input if provided
    if input_data is not None:
        _store_payload(trace_id, span_id, "input", input_data)
        has_input = 1

    def capture_output(data: Any) -> None:
        nonlocal has_output
        _store_payload(trace_id, span_id, "output", data)
        has_output = 1

    try:
        yield span_id, capture_output
    except Exception as e:
        status = "error"
        error_type = type(e).__name__
        error_msg = str(e)
        error_stack = traceback.format_exc()
        raise
    finally:
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        span_attrs: dict[str, str] = {
            "aw.workflow_name": name,
            "aw.kind": "workflow",
        }
        # Convert all attr values to strings for validation
        for key, value in attrs.items():
            span_attrs[key] = str(value)

        send_span_to_ingest(
            org_id=config.org_id,
            project_id=config.project_id,
            trace_id=trace_id,
            span_id=span_id,
            parent_id=parent_span_id or "",
            ts=datetime.fromtimestamp(start_time, tz=timezone.utc),
            kind="workflow",
            name=name,
            status=status,
            latency_ms=latency_ms,
            attrs=span_attrs,
            error_type=error_type,
            error_msg=error_msg,
            has_input=has_input,
            has_output=has_output,
            error_stack=error_stack,
        )

        _span_id_var.reset(token_span)
        _parent_span_id_var.reset(token_parent)


def llm_call(
    model: str,
    provider: str,
    prompt: str = "",
    system_prompt: str = "",
    user_prompt: str = "",
    completion: str = "",
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    **attrs: Any,
) -> dict[str, Any]:
    """
    Trace an LLM call.

    This is a simplified wrapper. In practice, you'd instrument
    the actual LLM client (OpenAI, Anthropic, etc.)

    Args:
        model: Model name
        provider: Provider (openai, anthropic, google)
        prompt: Combined prompt (deprecated, use system_prompt/user_prompt)
        system_prompt: System prompt
        user_prompt: User prompt
        completion: Output completion
        prompt_tokens: Number of input tokens
        completion_tokens: Number of output tokens
        **attrs: Additional attributes

    Returns:
        Dict with span metadata
    """
    config = get_config()

    trace_id = get_current_trace_id()
    span_id = generate_span_id()
    parent_span_id = _span_id_var.get()

    start_time = time.time()

    # Store prompts as separate payloads
    has_prompt = 0
    if system_prompt:
        _store_payload(trace_id, span_id, "system_prompt", system_prompt)
        has_prompt = 1
    if user_prompt:
        _store_payload(trace_id, span_id, "user_prompt", user_prompt)
        has_prompt = 1
    elif prompt:  # Fallback to combined prompt
        _store_payload(trace_id, span_id, "user_prompt", prompt)
        has_prompt = 1

    # Store completion
    if completion:
        _store_payload(trace_id, span_id, "completion", completion)

    # PII detection and redaction
    pii_types: list[str] = []
    all_text = f"{system_prompt} {user_prompt} {prompt} {completion}"

    if config.redact_pii:
        _, pii_types = redact_pii(all_text)

    # Calculate cost
    cost_usd = calculate_cost(model, prompt_tokens, completion_tokens)

    end_time = time.time()
    latency_ms = int((end_time - start_time) * 1000)

    # Build attributes
    span_attrs: dict[str, str] = {
        "aw.model": model,
        "aw.provider": provider,
        "aw.kind": "llm",
        "aw.sdk_name": "agentworks-python",
        "aw.sdk_language": "python",
        "aw.prompt_tokens": str(prompt_tokens),
        "aw.completion_tokens": str(completion_tokens),
        "aw.total_tokens": str(prompt_tokens + completion_tokens),
        "aw.cost_usd": str(cost_usd),
    }

    if pii_types:
        span_attrs["aw.pii_types"] = ",".join(pii_types)

    for key, value in attrs.items():
        span_attrs[f"aw.{key}"] = str(value)

    send_span_to_ingest(
        org_id=config.org_id,
        project_id=config.project_id,
        trace_id=trace_id,
        span_id=span_id,
        parent_id=parent_span_id or "",
        ts=datetime.fromtimestamp(start_time, tz=timezone.utc),
        kind="llm",
        name=f"{provider}:{model}",
        status="ok",
        latency_ms=latency_ms,
        attrs=span_attrs,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        cost_usd=cost_usd,
        pii_flag=1 if pii_types else 0,
        has_prompt=has_prompt,
        has_output=1 if completion else 0,
    )

    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "cost_usd": float(cost_usd),
        "pii_detected": pii_types,
    }


def send_span(
    kind: str,
    name: str,
    latency_ms: int,
    status: str = "ok",
    **attrs: str,
) -> None:
    """
    Send a custom span.

    Args:
        kind: Span kind (agent, tool, llm, decision, custom)
        name: Span name
        latency_ms: Latency in milliseconds
        status: Span status (ok, error, timeout)
        **attrs: Additional attributes
    """
    config = get_config()

    trace_id = get_current_trace_id()
    span_id = generate_span_id()
    parent_span_id = _span_id_var.get()

    span_attrs: dict[str, str] = {"aw.kind": kind}
    # Convert all attr values to strings for validation
    for key, value in attrs.items():
        span_attrs[key] = str(value)

    send_span_to_ingest(
        org_id=config.org_id,
        project_id=config.project_id,
        trace_id=trace_id,
        span_id=span_id,
        parent_id=parent_span_id or "",
        ts=datetime.now(timezone.utc),
        kind=kind,
        name=name,
        status=status,
        latency_ms=latency_ms,
        attrs=span_attrs,
    )


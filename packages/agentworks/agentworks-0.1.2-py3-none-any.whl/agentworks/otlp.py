"""OTLP client for sending spans to ingest API."""

from datetime import datetime
from decimal import Decimal

import httpx

from agentworks.config import get_config


def send_span_to_ingest(
    org_id: str,
    project_id: str,
    trace_id: str,
    span_id: str,
    parent_id: str,
    ts: datetime,
    kind: str,
    name: str,
    status: str,
    latency_ms: int,
    attrs: dict[str, str],
    error_type: str = "",
    error_msg: str = "",
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    total_tokens: int = 0,
    cost_usd: Decimal = Decimal("0"),
    pii_flag: int = 0,
    has_input: int = 0,
    has_output: int = 0,
    has_prompt: int = 0,
    error_stack: str = "",
) -> None:
    """
    Send span to ingest API.

    Args:
        org_id: Organization ID
        project_id: Project ID
        trace_id: Trace ID
        span_id: Span ID
        parent_id: Parent span ID
        ts: Timestamp
        kind: Span kind
        name: Span name
        status: Span status
        latency_ms: Latency in milliseconds
        attrs: Span attributes
        error_type: Error type (if any)
        error_msg: Error message (if any)
        prompt_tokens: Prompt tokens (for LLM spans)
        completion_tokens: Completion tokens (for LLM spans)
        total_tokens: Total tokens (for LLM spans)
        cost_usd: Cost in USD (for LLM spans)
        pii_flag: PII flag (1 if PII detected)
        has_input: Flag indicating input payload exists
        has_output: Flag indicating output payload exists
        has_prompt: Flag indicating prompt payload exists
        error_stack: Full error stack trace
    """
    config = get_config()

    # Import here to avoid circular import
    from agentworks.tracing import _pending_payloads

    # Build span payload
    span_data = {
        "org_id": org_id,
        "project_id": project_id,
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_id": parent_id,
        "ts": ts.isoformat(),
        "kind": kind,
        "name": name,
        "status": status,
        "latency_ms": latency_ms,
        "attrs": attrs,
        "error_type": error_type,
        "error_msg": error_msg,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "cost_usd": str(cost_usd),
        "pii_flag": pii_flag,
        "has_input": has_input,
        "has_output": has_output,
        "has_prompt": has_prompt,
        "error_stack": error_stack,
    }

    # Get payloads for this span
    span_payloads = [p for p in _pending_payloads if p["span_id"] == span_id]

    # Add org_id and project_id to payloads
    for payload in span_payloads:
        payload["org_id"] = org_id
        payload["project_id"] = project_id
        payload["ts"] = payload["ts"].isoformat()

    # Build batch payload
    batch_payload = {
        "org_id": org_id,
        "project_id": project_id,
        "spans": [span_data],
        "payloads": span_payloads,
    }

    # Skip sending if disabled (e.g., in tests)
    if config.disable_send:
        if config.debug:
            print(f"✓ Span captured (send disabled): {span_id} (trace: {trace_id}, payloads: {len(span_payloads)})")
        # Clear payloads even when not sending
        for payload in span_payloads:
            _pending_payloads.remove(payload)
        return

    # Send to ingest API
    endpoint = f"{config.ingest_endpoint}/ingest/json"
    headers = {"Content-Type": "application/json"}

    if config.api_key:
        headers["X-API-Key"] = config.api_key

    # Add debug headers for dev mode
    headers["X-Debug-Org"] = org_id
    headers["X-Debug-Project"] = project_id

    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.post(endpoint, json=batch_payload, headers=headers)
            response.raise_for_status()

            if config.debug:
                print(f"✓ Span sent: {span_id} (trace: {trace_id}, payloads: {len(span_payloads)})")

            # Clear sent payloads
            for payload in span_payloads:
                _pending_payloads.remove(payload)

    except httpx.HTTPError as e:
        if config.debug:
            print(f"✗ Failed to send span: {e}")
        # In production, you'd queue for retry
        # For now, silently fail to not impact application
        pass


def send_batch(spans: list[dict[str, str]]) -> None:
    """
    Send multiple spans in a batch.

    Args:
        spans: List of span dictionaries
    """
    config = get_config()

    if not spans:
        return

    # Assume all spans belong to the same org/project
    org_id = spans[0].get("org_id", config.org_id)
    project_id = spans[0].get("project_id", config.project_id)

    batch_payload = {
        "org_id": org_id,
        "project_id": project_id,
        "spans": spans,
    }

    endpoint = f"{config.ingest_endpoint}/ingest/json"
    headers = {"Content-Type": "application/json"}

    if config.api_key:
        headers["X-API-Key"] = config.api_key

    headers["X-Debug-Org"] = org_id
    headers["X-Debug-Project"] = project_id

    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.post(endpoint, json=batch_payload, headers=headers)
            response.raise_for_status()

            if config.debug:
                print(f"✓ Batch sent: {len(spans)} spans")
    except httpx.HTTPError as e:
        if config.debug:
            print(f"✗ Failed to send batch: {e}")


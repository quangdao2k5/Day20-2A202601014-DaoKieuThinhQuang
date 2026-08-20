"""Tracing hooks.

This file intentionally avoids binding to one provider. Students can plug in LangSmith,
Langfuse, OpenTelemetry, or simple JSON traces.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from time import perf_counter
from typing import Any

from multi_agent_research_lab.core.config import get_settings


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Minimal local span, mirrored to LangSmith when credentials are configured."""

    started = perf_counter()
    span: dict[str, Any] = {"name": name, "attributes": attributes or {}, "duration_seconds": None}
    langsmith_run = None
    try:
        tracer = _langsmith_trace(name, span["attributes"])
        if tracer is None:
            yield span
        else:
            with tracer as run:
                langsmith_run = run
                yield span
    finally:
        span["duration_seconds"] = perf_counter() - started
        if langsmith_run is not None:
            langsmith_run.add_outputs({"duration_seconds": span["duration_seconds"]})


def _langsmith_trace(name: str, attributes: dict[str, Any]) -> Any | None:
    settings = get_settings()
    if not settings.langsmith_api_key:
        return None

    try:
        from langsmith.run_helpers import trace
    except ImportError:
        return None

    return trace(
        name=name,
        run_type="chain",
        inputs={"attributes": attributes},
        project_name=settings.langsmith_project,
        client=_langsmith_client(),
        tags=["multi-agent-research-lab"],
        metadata=attributes,
    )


@lru_cache(maxsize=1)
def _langsmith_client() -> Any:
    from langsmith import Client

    settings = get_settings()
    return Client(api_key=settings.langsmith_api_key)

"""Command-line entrypoint for the lab starter."""

from typing import Annotated

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient
from multi_agent_research_lab.services.storage import LocalArtifactStore

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


def _parse_query(query: str) -> ResearchQuery:
    try:
        return ResearchQuery(query=query)
    except ValidationError as exc:
        console.print(
            Panel.fit(
                f"Invalid query: {exc.errors()[0]['msg']}",
                title="Input Error",
                style="red",
            )
        )
        raise typer.Exit(code=1) from exc


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline."""

    _init()
    state = _run_baseline(query)
    console.print(Panel.fit(state.final_answer or "", title="Single-Agent Baseline"))


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow skeleton."""

    _init()
    state = ResearchState(request=_parse_query(query))
    workflow = MultiAgentWorkflow()
    try:
        result = workflow.run(state)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
    console.print(result.model_dump_json(indent=2))


@app.command("benchmark")
def benchmark(
    query: Annotated[
        str,
        typer.Option(
            "--query",
            "-q",
            help="Research query",
        ),
    ] = "Compare single-agent and multi-agent architectures for complex research tasks",
) -> None:
    """Run baseline and multi-agent benchmark, then write a report."""

    _init()
    _, baseline_metrics = run_benchmark("single-agent-baseline", query, _run_baseline)
    _, multi_metrics = run_benchmark("multi-agent-workflow", query, _run_multi_agent)
    report = render_markdown_report([baseline_metrics, multi_metrics])
    path = LocalArtifactStore().write_text("benchmark_report.md", report)
    console.print(Panel.fit(str(path), title="Benchmark Report Written"))


def _run_baseline(query: str) -> ResearchState:
    request = _parse_query(query)
    state = ResearchState(request=request)
    sources = SearchClient().search(query, request.max_sources)
    state.sources = sources
    source_context = "\n".join(
        f"- [{source.metadata.get('source_id', index)}] {source.title}: {source.snippet}"
        for index, source in enumerate(sources, start=1)
    )
    response = LLMClient().complete(
        "You are a single-agent research assistant. Answer with citations.",
        f"Question: {query}\n\nSources:\n{source_context}",
    )
    state.research_notes = source_context
    state.final_answer = response.content
    state.add_trace_event(
        "baseline.complete",
        {"source_count": len(sources), "output_tokens": response.output_tokens},
    )
    return state


def _run_multi_agent(query: str) -> ResearchState:
    return MultiAgentWorkflow().run(ResearchState(request=_parse_query(query)))


if __name__ == "__main__":
    app()

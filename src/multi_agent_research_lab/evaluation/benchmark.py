"""Benchmark helpers for single-agent vs multi-agent."""

from collections.abc import Callable
from time import perf_counter

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState

Runner = Callable[[str], ResearchState]


def run_benchmark(
    run_name: str, query: str, runner: Runner
) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and derive lightweight quality/process metrics."""

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started
    coverage = compute_citation_coverage(state)
    failed = bool(state.errors) or not state.final_answer
    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        estimated_cost_usd=_sum_cost(state),
        quality_score=_quality_score(state, coverage),
        citation_coverage=coverage,
        failure_rate=1.0 if failed else 0.0,
        notes=(
            f"{len(state.sources)} sources, {len(state.route_history)} routes, "
            f"{len(state.errors)} errors"
        ),
    )
    return state, metrics


def compute_citation_coverage(state: ResearchState) -> float:
    """Return share of retrieved source IDs cited in the final answer."""

    if not state.sources:
        return 0.0
    answer = state.final_answer or ""
    cited_count = sum(
        1
        for source in state.sources
        if _source_id(source.metadata) and _source_id(source.metadata) in answer
    )
    return cited_count / len(state.sources)


def _source_id(metadata: dict[str, object]) -> str:
    return str(metadata.get("source_id", ""))


def _sum_cost(state: ResearchState) -> float:
    total = 0.0
    for result in state.agent_results:
        cost = result.metadata.get("cost_usd")
        if isinstance(cost, int | float):
            total += float(cost)
    return total


def _quality_score(state: ResearchState, citation_coverage: float) -> float:
    score = 4.0
    if state.sources:
        score += 1.5
    if state.research_notes:
        score += 1.0
    if state.analysis_notes:
        score += 1.0
    if state.final_answer:
        score += 1.0
    score += min(1.5, citation_coverage * 1.5)
    score -= min(2.0, len(state.errors) * 0.5)
    return max(0.0, min(10.0, score))

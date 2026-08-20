"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics and a short interpretation to markdown."""

    lines = [
        "# Benchmark Report",
        "",
        "| Run | Latency (s) | Cost (USD) | Quality | Citation cov. | Failure rate | Notes |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for item in metrics:
        cost = "" if item.estimated_cost_usd is None else f"{item.estimated_cost_usd:.4f}"
        quality = "" if item.quality_score is None else f"{item.quality_score:.1f}"
        citation = "" if item.citation_coverage is None else f"{item.citation_coverage:.0%}"
        failure = "" if item.failure_rate is None else f"{item.failure_rate:.0%}"
        lines.append(
            f"| {item.run_name} | {item.latency_seconds:.2f} | {cost} | {quality} "
            f"| {citation} | {failure} | {item.notes} |"
        )

    lines.extend(
        [
            "",
            "## Failure Mode and Fix",
            "",
            "A common failure mode is unsupported synthesis: downstream agents may repeat a "
            "research note without checking whether the cited source supports the claim. This "
            "implementation reduces that risk by keeping source IDs in shared state, requiring "
            "the writer prompt to use those IDs, and computing citation coverage in the benchmark.",
            "",
            "Trace evidence is stored in each `ResearchState.trace` entry. For a hosted tracing "
            "provider, wire the same span names to LangSmith, Langfuse, or OpenTelemetry.",
        ]
    )
    return "\n".join(lines) + "\n"

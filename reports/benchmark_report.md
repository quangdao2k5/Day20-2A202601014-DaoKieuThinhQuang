# Benchmark Report

| Run | Latency (s) | Cost (USD) | Quality | Citation cov. | Failure rate | Notes |
|---|---:|---:|---:|---:|---:|---|
| single-agent-baseline | 6.24 | 0.0000 | 8.1 | 40% | 0% | 5 sources, 0 routes, 0 errors |
| multi-agent-workflow | 17.35 | 0.0000 | 10.0 | 100% | 0% | 5 sources, 4 routes, 0 errors |

## Failure Mode and Fix

A common failure mode is unsupported synthesis: downstream agents may repeat a research note without checking whether the cited source supports the claim. This implementation reduces that risk by keeping source IDs in shared state, requiring the writer prompt to use those IDs, and computing citation coverage in the benchmark.

Trace evidence is stored in each `ResearchState.trace` entry. For a hosted tracing provider, wire the same span names to LangSmith, Langfuse, or OpenTelemetry.

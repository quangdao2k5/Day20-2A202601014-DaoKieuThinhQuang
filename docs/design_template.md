# Design Template

## Problem

Research task: nhận một câu hỏi dài về AI agents, tìm bằng corpus offline, phân tích
trade-off và viết câu trả lời có citation.

## Why multi-agent?

Single-agent baseline đủ cho câu hỏi hẹp, nhưng bài lab cần đánh giá luồng có tách
vai trò để tăng evidence coverage, kiểm tra claim, và trace handoff.

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Chọn route tiếp theo và dừng workflow khi đủ artifact | `ResearchState` hiện tại | Route trong `route_history`, trace event | Lặp vô hạn hoặc route sai nếu state thiếu guardrail |
| Researcher | Tìm nguồn trong corpus offline và tạo research notes có citation | Query, `max_sources` | `sources`, `research_notes`, `AgentResult` | Nguồn trùng/chưa sát query, citation coverage thấp |
| Analyst | Chuyển research notes thành insight, trade-off và weak evidence | Query, `research_notes` | `analysis_notes`, token/cost metadata | Lặp lại nguồn thay vì phân tích, bỏ sót risk |
| Writer | Tổng hợp câu trả lời cuối cho audience, giữ source IDs | Query, notes, sources | `final_answer`, writer metadata | Unsupported synthesis hoặc thiếu citation |

## Shared state

Shared state gồm request, route history, sources, research notes, analysis notes,
final answer, agent results, trace và errors. Các field này giúp debug nguồn, quyết
định routing, output từng agent và guardrail.

## Routing policy

Graph: Supervisor định tuyến đến Researcher khi thiếu nguồn, Analyst khi thiếu phân
tích, Writer khi thiếu câu trả lời cuối, và `done` khi đủ artifact hoặc chạm guardrail.

## Guardrails

- Max iterations: `MAX_ITERATIONS`, mặc định 6, enforced trong `SupervisorAgent`.
- Timeout: `TIMEOUT_SECONDS`, mặc định 60s, enforced trong `MultiAgentWorkflow.run`.
- Retry: provider thật nên đặt retry trong `LLMClient`; bản offline deterministic không cần retry.
- Fallback: nếu không có `OPENAI_API_KEY` hoặc thiếu optional package `openai`, `LLMClient` dùng offline synthesis.
- Validation: Pydantic schema cho query/state/source/result; benchmark kiểm failure, citation coverage và errors.

## Benchmark plan

Benchmark chạy cùng query cho baseline và multi-agent. Metrics gồm latency, estimated
cost, quality score, citation coverage, failure rate và notes về số routes/errors.

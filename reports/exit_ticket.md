# Exit Ticket

## 1. Case nào nên dùng multi-agent? Vì sao?

Nên dùng multi-agent khi research task phức tạp, cần nhiều evidence route độc lập,
cần tách rõ trách nhiệm giữa các bước: tìm nguồn (Researcher), phân tích (Analyst),
và tổng hợp viết bài (Writer). Trong benchmark của repo này, multi-agent workflow
đạt **citation coverage 100%** và **quality 10.0/10**, cao hơn baseline (40% citation
coverage, quality 8.1). Multi-agent phù hợp khi:

- Task cần nhiều tool/source khác nhau.
- Cần independent evidence checking trước khi tổng hợp.
- Cần long-running state và controlled handoff giữa các bước.
- Output cần specialized verification (ví dụ: fact-checking, citation audit).

## 2. Case nào không nên dùng multi-agent? Vì sao?

Không nên dùng multi-agent cho câu hỏi ngắn, nguồn đã rõ, output dễ verify và không
cần independent checking. Khi đó single-agent baseline nhanh hơn (~6s vs ~17s),
ít orchestration overhead hơn, ít nguy cơ duplicated work / context drift hơn,
và chất lượng có thể đủ cho mục tiêu tác vụ. Cụ thể:

- Câu hỏi factual đơn giản (lookup-style).
- Task không benefit từ decomposition.
- Budget giới hạn — single-agent tiết kiệm token hơn.
- Latency yêu cầu thấp — multi-agent tốn thời gian handoff.

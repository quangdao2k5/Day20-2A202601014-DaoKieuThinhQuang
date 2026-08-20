"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass
from os import getenv

from multi_agent_research_lab.core.config import get_settings


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client with deterministic offline fallback."""

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion.

        If `OPENAI_API_KEY` is present and the optional `openai` package is installed,
        the client calls OpenAI. Otherwise it returns a deterministic local synthesis
        so the lab is runnable without paid credentials.
        """

        settings = get_settings()
        if settings.openai_api_key or getenv("OPENAI_API_KEY"):
            try:
                from openai import OpenAI  # type: ignore[import-not-found]
            except ImportError:
                pass
            else:
                client = OpenAI(api_key=settings.openai_api_key)
                response = client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,
                )
                usage = response.usage
                content = response.choices[0].message.content or ""
                return LLMResponse(
                    content=content,
                    input_tokens=getattr(usage, "prompt_tokens", None),
                    output_tokens=getattr(usage, "completion_tokens", None),
                    cost_usd=None,
                )

        content = _offline_completion(system_prompt, user_prompt)
        return LLMResponse(
            content=content,
            input_tokens=max(1, len(user_prompt.split())),
            output_tokens=max(1, len(content.split())),
            cost_usd=0.0,
        )


def _offline_completion(system_prompt: str, user_prompt: str) -> str:
    role = system_prompt.lower()
    lines = [line.strip("- ") for line in user_prompt.splitlines() if line.strip()]
    evidence = [line for line in lines if "[" in line and "]" in line]
    if "analyst" in role:
        bullets = evidence[:5] or lines[:5]
        return "\n".join(f"- Insight: {item[:240]}" for item in bullets)
    if "writer" in role:
        citations = ", ".join(_extract_citations(user_prompt)[:5]) or "offline corpus"
        return (
            "Multi-agent research is most useful when the task benefits from decomposition, "
            "independent evidence gathering, and explicit verification. A single-agent baseline "
            "is cheaper and faster for narrow questions, but it can miss coverage and validation "
            "steps on complex research tasks. The recommended design is a supervised pipeline: "
            "Researcher collects cited evidence, Analyst turns it into claims and trade-offs, "
            "and Writer produces a concise answer with provenance. Main failure modes are "
            "coordination overhead, duplicated retrieval, stale shared state, and unsupported "
            f"claims. Evidence used: {citations}."
        )
    return " ".join(lines[:8])[:1200] or "No local context was provided."


def _extract_citations(text: str) -> list[str]:
    citations: list[str] = []
    for token in text.split("["):
        if "]" not in token:
            continue
        label = token.split("]", 1)[0].strip()
        if label and label not in citations:
            citations.append(f"[{label}]")
    return citations

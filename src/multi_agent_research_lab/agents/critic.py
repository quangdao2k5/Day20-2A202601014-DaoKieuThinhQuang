"""Optional critic agent for final-answer checks."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def run(self, state: ResearchState) -> ResearchState:
        """Validate citation coverage and append findings."""

        answer = state.final_answer or ""
        cited = [
            source.metadata.get("source_id")
            for source in state.sources
            if str(source.metadata.get("source_id")) in answer
        ]
        coverage = len(cited) / len(state.sources) if state.sources else 0.0
        finding = (
            f"Citation coverage: {coverage:.0%}. "
            "Final answer is present." if answer else "Final answer is missing."
        )
        state.agent_results.append(
            AgentResult(
                agent=AgentName.CRITIC,
                content=finding,
                metadata={"citation_coverage": coverage, "cited_sources": cited},
            )
        )
        state.add_trace_event("critic.complete", {"citation_coverage": coverage})
        return state

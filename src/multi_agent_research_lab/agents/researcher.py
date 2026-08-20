"""Researcher agent implementation."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.search_client import SearchClient


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(self, search_client: SearchClient | None = None) -> None:
        self.search_client = search_client or SearchClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""

        sources = self.search_client.search(state.request.query, state.request.max_sources)
        state.sources = sources
        note_lines = []
        for index, source in enumerate(sources, start=1):
            label = source.metadata.get("source_id", f"S{index}")
            note_lines.append(f"{index}. [{label}] {source.title}: {source.snippet}")
        state.research_notes = "\n".join(note_lines)
        state.agent_results.append(
            AgentResult(
                agent=AgentName.RESEARCHER,
                content=state.research_notes,
                metadata={"source_count": len(sources)},
            )
        )
        state.add_trace_event(
            "researcher.complete",
            {
                "source_count": len(sources),
                "source_ids": [source.metadata.get("source_id") for source in sources],
            },
        )
        return state

from multi_agent_research_lab.agents import SupervisorAgent
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow


def test_supervisor_routes_by_missing_artifacts() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))

    SupervisorAgent().run(state)
    assert state.route_history[-1] == "researcher"

    state.sources.append({"title": "source", "snippet": "snippet"})
    state.research_notes = "notes"
    SupervisorAgent().run(state)
    assert state.route_history[-1] == "analyst"

    state.analysis_notes = "analysis"
    SupervisorAgent().run(state)
    assert state.route_history[-1] == "writer"

    state.final_answer = "answer"
    SupervisorAgent().run(state)
    assert state.route_history[-1] == "done"


def test_workflow_runs_end_to_end() -> None:
    state = ResearchState(
        request=ResearchQuery(
            query="Compare single-agent and multi-agent architectures for research tasks"
        )
    )
    result = MultiAgentWorkflow().run(state)

    assert result.sources
    assert result.research_notes
    assert result.analysis_notes
    assert result.final_answer
    assert result.route_history[-1] == "done"
    assert not result.errors

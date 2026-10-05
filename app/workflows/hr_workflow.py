from typing import TypedDict, Any

from langgraph.graph import StateGraph, END

from app.agents.coordinator import coordinator


class HRWorkflowState(TypedDict, total=False):
    employee_id: int
    request: str
    plan: dict
    results: list
    decision: dict
    final_response: dict
    error: str


def coordinate_request(state: HRWorkflowState) -> HRWorkflowState:
    """
    Main coordination node.

    The coordinator creates the workflow plan, executes the
    required specialized agents, and evaluates their results.
    """

    employee_id = state.get("employee_id")
    request = state.get("request")

    if not employee_id:
        return {
            **state,
            "error": "Employee authentication is required."
        }

    if not request:
        return {
            **state,
            "error": "No HR request was provided."
        }

    # Database session will be supplied by the API layer later.
    db = state.get("db")

    if db is None:
        return {
            **state,
            "error": "Database session is not available."
        }

    result = coordinator.process_request(
        db=db,
        employee_id=employee_id,
        request=request
    )

    return {
        **state,
        "plan": result.get("plan", []),
        "results": result.get("results", []),
        "decision": result.get("decision", {}),
        "final_response": result
    }


def build_hr_workflow():
    """
    Construct the enterprise HR multi-agent workflow.
    """

    workflow = StateGraph(HRWorkflowState)

    workflow.add_node(
        "coordinate_request",
        coordinate_request
    )

    workflow.set_entry_point("coordinate_request")

    workflow.add_edge(
        "coordinate_request",
        END
    )

    return workflow.compile()


hr_workflow = build_hr_workflow()
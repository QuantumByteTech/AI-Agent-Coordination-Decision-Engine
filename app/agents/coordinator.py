from app.agents.planning_agent import planning_agent
from app.agents.decision_agent import decision_agent
from app.agents.employee_agent import employee_agent
from app.agents.leave_agent import leave_agent
from app.agents.attendance_agent import attendance_agent
from app.agents.policy_agent import policy_agent
from app.agents.lifecycle_agent import lifecycle_agent


class HRCoordinator:
    """
    Central coordinator responsible for routing enterprise HR
    requests to specialized agents and combining their results.
    """

    name = "AI HR Coordinator"

    def create_plan(self, request: str) -> dict:
        return planning_agent.create_plan(request)

    def execute_agent(
        self,
        agent_name: str,
        db,
        employee_id: int,
        request: str
    ) -> dict:

        if agent_name == "Employee Intelligence Agent":
            return employee_agent.get_employee_profile(
                db,
                employee_id
            )

        if agent_name == "Leave Management Agent":
            return leave_agent.get_leave_history(
                db,
                employee_id
            )

        if agent_name == "Attendance Intelligence Agent":
            return attendance_agent.get_attendance_summary(
                db,
                employee_id
            )

        if agent_name == "HR Policy Agent":
            return policy_agent.search_policy(
                db,
                request
            )

        if agent_name == "Employee Lifecycle Agent":
            return lifecycle_agent.get_employee_lifecycle(
                db,
                employee_id
            )

        return {
            "success": False,
            "agent": self.name,
            "message": (
                f"No execution handler exists for "
                f"'{agent_name}'."
            )
        }

    def process_request(
        self,
        db,
        employee_id: int,
        request: str
    ) -> dict:

        plan_result = self.create_plan(request)

        if not plan_result.get("success"):
            return plan_result

        results = []

        for step in plan_result["plan"]:

            result = self.execute_agent(
                agent_name=step["agent"],
                db=db,
                employee_id=employee_id,
                request=request
            )

            results.append({
                "step": step["step"],
                "agent": step["agent"],
                "task": step["task"],
                "result": result
            })

        decision_input = [
            item["result"]
            for item in results
        ]

        decision = decision_agent.evaluate(
            request=request,
            results=decision_input
        )

        return {
            "success": True,
            "coordinator": self.name,
            "request": request,
            "plan": plan_result["plan"],
            "results": results,
            "decision": decision
        }


coordinator = HRCoordinator()
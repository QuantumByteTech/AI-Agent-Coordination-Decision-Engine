class PlanningAgent:
    """
    Planning Agent responsible for breaking complex enterprise
    HR requests into executable workflow steps.
    """

    name = "Planning Agent"

    description = (
        "Analyzes complex HR requests and creates a sequence "
        "of tasks for specialized agents."
    )

    AGENT_CAPABILITIES = {
        "employee": "Employee information and employee profiles",
        "leave": "Leave balance, leave history and leave requests",
        "policy": "HR policies, benefits, attendance and company rules",
        "attendance": "Attendance records and attendance analysis",
        "lifecycle": "Employee onboarding and offboarding",
    }

    def create_plan(self, request: str) -> dict:
        """
        Create a preliminary workflow plan from an HR request.
        """

        if not request or not request.strip():
            return {
                "success": False,
                "agent": self.name,
                "message": "No request was provided."
            }

        request_lower = request.lower()

        steps = []

        if any(
            word in request_lower
            for word in ["leave", "vacation", "sick", "casual"]
        ):
            steps.append({
                "step": 1,
                "agent": "Leave Management Agent",
                "task": "Check leave information or process the leave request."
            })

        if any(
            word in request_lower
            for word in [
                "attendance",
                "absent",
                "present",
                "late"
            ]
        ):
            steps.append({
                "step": len(steps) + 1,
                "agent": "Attendance Intelligence Agent",
                "task": "Retrieve and analyze attendance information."
            })

        if any(
            word in request_lower
            for word in [
                "policy",
                "wfh",
                "work from home",
                "working hours",
                "benefits",
                "rule"
            ]
        ):
            steps.append({
                "step": len(steps) + 1,
                "agent": "HR Policy Agent",
                "task": "Retrieve the relevant company policy."
            })

        if any(
            word in request_lower
            for word in [
                "onboarding",
                "joining",
                "offboarding",
                "resignation",
                "exit"
            ]
        ):
            steps.append({
                "step": len(steps) + 1,
                "agent": "Employee Lifecycle Agent",
                "task": "Retrieve the employee lifecycle information."
            })

        if any(
            word in request_lower
            for word in [
                "employee",
                "profile",
                "details",
                "information"
            ]
        ):
            steps.append({
                "step": len(steps) + 1,
                "agent": "Employee Intelligence Agent",
                "task": "Retrieve employee information."
            })

        if not steps:
            steps.append({
                "step": 1,
                "agent": "HR Coordinator",
                "task": "Analyze the request and determine the appropriate agent."
            })

        return {
            "success": True,
            "agent": self.name,
            "request": request,
            "step_count": len(steps),
            "plan": steps
        }


planning_agent = PlanningAgent()
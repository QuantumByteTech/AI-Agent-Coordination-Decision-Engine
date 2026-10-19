class PlanningAgent:
    """
    Planning Agent responsible for breaking complex enterprise
    HR requests into executable workflow steps.
    """

    name = "Planning Agent"

    description = (
        "Analyzes enterprise HR requests and creates "
        "a sequence of tasks for specialized agents."
    )

    AGENT_CAPABILITIES = {
        "employee": "Employee information and employee profiles",
        "leave": "Leave balance, leave history and leave requests",
        "policy": "HR policies, benefits and company rules",
        "attendance": "Attendance records and attendance analysis",
        "lifecycle": "Employee onboarding and offboarding",
    }

    def create_plan(self, request: str) -> dict:
        """Create a workflow plan based on the user's HR request."""

        if not request or not request.strip():
            return {
                "success": False,
                "agent": self.name,
                "message": "No request was provided.",
            }

        request_lower = request.lower()
        steps = []

        def add_step(agent_name: str, task: str) -> None:
            steps.append({
                "step": len(steps) + 1,
                "agent": agent_name,
                "task": task,
            })

        # Leave requests and leave-balance/history lookups must
        # still reach the Leave Agent when policy is also mentioned.
        leave_keywords = [
            "leave",
            "vacation",
            "sick",
            "casual",
            "earned leave",
        ]

        if any(word in request_lower for word in leave_keywords):
            if any(word in request_lower for word in [
                "balance",
                "remaining leave",
                "leave left",
            ]):
                leave_task = "Retrieve the employee's current leave balance."
            elif "history" in request_lower:
                leave_task = "Retrieve the employee's leave history."
            elif any(word in request_lower for word in [
                "apply",
                "request",
                "take",
                "book",
            ]):
                leave_task = "Validate the leave request and required details."
            else:
                leave_task = "Retrieve relevant leave information."

            add_step("Leave Management Agent", leave_task)

        # Attendance analysis
        if any(word in request_lower for word in [
            "attendance",
            "absent",
            "present",
            "late",
        ]):
            add_step(
                "Attendance Intelligence Agent",
                "Retrieve and analyze attendance information.",
            )

        # HR policies can be requested alongside leave information.
        if any(word in request_lower for word in [
            "policy",
            "policies",
            "polic",  # preserves the original broad policy matching
            "wfh",
            "work from home",
            "working hours",
            "benefits",
            "rule",
        ]):
            add_step(
                "HR Policy Agent",
                "Retrieve the relevant company policy.",
            )

        # Employee lifecycle
        if any(word in request_lower for word in [
            "onboarding",
            "joining",
            "offboarding",
            "resignation",
            "exit",
        ]):
            add_step(
                "Employee Lifecycle Agent",
                "Retrieve the employee lifecycle information.",
            )

        # Employee profile/details
        if any(word in request_lower for word in [
            "employee",
            "profile",
            "details",
            "information",
        ]):
            add_step(
                "Employee Intelligence Agent",
                "Retrieve employee information.",
            )

        # Fallback for requests that don't match a specialist.
        if not steps:
            add_step(
                "HR Coordinator",
                "Handle the general HR request and provide appropriate assistance.",
            )

        return {
            "success": True,
            "agent": self.name,
            "request": request,
            "step_count": len(steps),
            "plan": steps,
        }


planning_agent = PlanningAgent()
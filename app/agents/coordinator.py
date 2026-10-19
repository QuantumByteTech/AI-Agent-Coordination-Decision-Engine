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
            request_lower = request.lower()

            # Leave balance
            if "balance" in request_lower:
                return leave_agent.get_leave_balance(
                    db,
                    employee_id
                )

            # Leave history
            if "history" in request_lower:
                return leave_agent.get_leave_history(
                    db,
                    employee_id
                )

            # Detect leave application request
            application_words = [
                "apply",
                "request",
                "take",
                "book"
            ]

            is_application = any(
                word in request_lower
                for word in application_words
            )

            if is_application:
                import re
                from datetime import date

                leave_type = None

                leave_type_map = {
                    "casual": "casual",
                    "sick": "sick",
                    "vacation": "vacation",
                    "earned": "earned",
                }

                for keyword, normalized_type in leave_type_map.items():
                    if keyword in request_lower:
                        leave_type = normalized_type
                        break

                # Extract dates in YYYY-MM-DD format
                dates = re.findall(
                    r"\b\d{4}-\d{2}-\d{2}\b",
                    request
                )

                # Check required details
                if not leave_type or len(dates) < 2:
                    missing = []

                    if not leave_type:
                        missing.append("leave type")

                    if len(dates) < 2:
                        missing.append(
                            "start date and end date"
                        )

                    return {
                        "success": False,
                        "agent": leave_agent.name,
                        "employee_id": employee_id,
                        "message": (
                            "Please provide the following details "
                            "to apply for leave: "
                            + ", ".join(missing)
                            + "."
                        ),
                    }

                # Convert strings to date objects
                try:
                    start_date = date.fromisoformat(
                        dates[0]
                    )

                    end_date = date.fromisoformat(
                        dates[1]
                    )

                except ValueError:
                    return {
                        "success": False,
                        "agent": leave_agent.name,
                        "employee_id": employee_id,
                        "message": (
                            "Please provide dates in "
                            "YYYY-MM-DD format."
                        ),
                    }

                # Submit leave request
                return leave_agent.apply_leave(
                    db=db,
                    employee_id=employee_id,
                    leave_type=leave_type,
                    start_date=start_date,
                    end_date=end_date
                )

            # Default leave request behavior
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
            request_lower = request.lower()

            policy_keywords = [
                "work from home",
                "working hours",
                "attendance",
                "casual leave",
                "sick leave",
                "parental leave",
                "conduct",
                "information security",
                "remote access",
                "onboarding",
                "leave",
                "security",
            ]

            keywords = [
                item
                for item in policy_keywords
                if item in request_lower
            ]

            if not keywords:
                return policy_agent.search_policy(
                    db,
                    request
                )

            all_policies = []

            for keyword in keywords:
                result = policy_agent.search_policy(
                    db,
                    keyword
                )

                all_policies.extend(
                    result.get("policies", [])
                )

            unique_policies = []
            seen_ids = set()

            for policy in all_policies:
                policy_id = policy.get("id")

                if policy_id not in seen_ids:
                    seen_ids.add(policy_id)
                    unique_policies.append(policy)

            return {
                "success": True,
                "agent": policy_agent.name,
                "count": len(unique_policies),
                "policies": unique_policies
            }

        if agent_name == "Employee Lifecycle Agent":
            return lifecycle_agent.get_employee_lifecycle(
                db,
                employee_id
            )

        if agent_name == "HR Coordinator":
            return {
                "success": True,
                "agent": self.name,
                "message": (
                    "The request is a general HR matter. "
                    "Please provide more details so the appropriate "
                    "HR service can be identified."
            )
        }

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


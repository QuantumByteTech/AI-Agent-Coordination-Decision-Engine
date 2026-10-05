class DecisionAgent:
    """
    Decision Agent responsible for evaluating workflow results
    and recommending the next enterprise action.
    """

    name = "Decision Intelligence Agent"

    description = (
        "Evaluates information collected by specialized agents "
        "and produces an explainable business recommendation."
    )

    def evaluate(
        self,
        request: str,
        results: list
    ) -> dict:

        if not results:
            return {
                "success": False,
                "agent": self.name,
                "decision": "INSUFFICIENT_INFORMATION",
                "recommendation": (
                    "No supporting information was available "
                    "to make a decision."
                )
            }

        successful_results = [
            result
            for result in results
            if result.get("success", False)
        ]

        if not successful_results:
            return {
                "success": False,
                "agent": self.name,
                "decision": "UNABLE_TO_DECIDE",
                "recommendation": (
                    "The required enterprise information "
                    "could not be retrieved."
                )
            }

        decision = "REVIEW_REQUIRED"
        recommendation = (
            "The request was successfully analyzed. "
            "The HR team should review the available "
            "information before taking final action."
        )

        request_lower = request.lower()

        # Leave-related decision support
        if "leave" in request_lower:

            for result in successful_results:

                if "eligible" in result:

                    if result["eligible"]:
                        decision = "ELIGIBLE"
                        recommendation = (
                            "The employee satisfies the available "
                            "leave eligibility criteria. The request "
                            "can proceed for HR or manager approval."
                        )
                    else:
                        decision = "NOT_ELIGIBLE"
                        recommendation = (
                            "The employee does not satisfy the "
                            "available leave eligibility criteria."
                        )

        # Attendance-related decision support
        elif "attendance" in request_lower:

            for result in successful_results:

                summary = result.get("summary")

                if summary:

                    percentage = summary.get(
                        "attendance_percentage",
                        0
                    )

                    if percentage >= 90:
                        decision = "GOOD_ATTENDANCE"
                        recommendation = (
                            "The employee's attendance is within "
                            "the healthy range."
                        )

                    elif percentage >= 75:
                        decision = "ATTENDANCE_REVIEW"
                        recommendation = (
                            "The employee's attendance requires "
                            "routine HR review."
                        )

                    else:
                        decision = "LOW_ATTENDANCE"
                        recommendation = (
                            "The employee has relatively low "
                            "attendance and may require HR review."
                        )

        # General workflow decision
        else:

            decision = "HR_REVIEW"
            recommendation = (
                "The required information has been collected. "
                "HR can review the results and determine the "
                "appropriate business action."
            )

        return {
            "success": True,
            "agent": self.name,
            "decision": decision,
            "recommendation": recommendation,
            "evidence_count": len(successful_results)
        }


decision_agent = DecisionAgent()
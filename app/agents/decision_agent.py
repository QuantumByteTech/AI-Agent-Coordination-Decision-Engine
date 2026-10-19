class DecisionAgent:
    """Explainable, risk-aware decision support for enterprise HR workflows."""

    name = "Decision Intelligence Agent"

    description = (
        "Evaluates specialist agent results and produces "
        "an explainable, risk-aware business recommendation."
    )

    def evaluate(self, request: str, results: list) -> dict:
        request_lower = (request or "").lower()
        results = results or []

        successful_results = [
            item for item in results
            if isinstance(item, dict) and item.get("success") is True
        ]

        failed_results = [
            item for item in results
            if not isinstance(item, dict) or item.get("success") is not True
        ]

        evidence = []

        # Build readable evidence from successful specialist results.
        for index, result in enumerate(successful_results, start=1):
            details = {
                key: result[key]
                for key in (
                    "employee", "summary", "policies", "eligible",
                    "balance", "leave_balance", "leave_history",
                    "attendance", "message", "count",
                    "requested_days", "available_days",
                )
                if key in result
            }

            if isinstance(result.get("message"), str):
                finding = result["message"]

            elif isinstance(result.get("leave_balance"), dict):
                balance = result["leave_balance"]
                finding = (
                    "Leave balance retrieved: "
                    f"casual={balance.get('casual_leave', 'unknown')}, "
                    f"sick={balance.get('sick_leave', 'unknown')}, "
                    f"earned={balance.get('earned_leave', 'unknown')} day(s)."
                )

            elif isinstance(result.get("summary"), dict):
                summary = result["summary"]
                percentage = summary.get("attendance_percentage")

                if (
                    isinstance(percentage, (int, float))
                    and not isinstance(percentage, bool)
                ):
                    finding = (
                        f"Attendance: {percentage:.1f}%; "
                        f"{summary.get('present', 'unknown')} present, "
                        f"{summary.get('absent', 'unknown')} absent, "
                        f"{summary.get('late', 'unknown')} late, "
                        f"{summary.get('leave', 'unknown')} on leave; "
                        f"{summary.get('total_records', 'unknown')} records."
                    )
                else:
                    finding = "Attendance summary retrieved; percentage unavailable."

            elif isinstance(result.get("employee"), dict):
                employee = result["employee"]
                full_name = " ".join(
                    str(employee.get(key, "")).strip()
                    for key in ("first_name", "last_name")
                    if employee.get(key)
                )
                finding = (
                    f"Employee: {full_name or 'Name unavailable'}; "
                    f"code={employee.get('employee_code', 'unknown')}; "
                    f"status={employee.get('employment_status', 'unknown')}."
                )

            elif isinstance(result.get("policies"), list):
                policies = result["policies"]

                policy_summaries = []
                for policy in policies:
                    if not isinstance(policy, dict):
                        continue

                    name = policy.get("policy_name", "Unnamed policy")
                    description = policy.get("description", "")
                    active = policy.get("active")

                    status = (
                        "active" if active is True
                        else "inactive" if active is False
                        else "status unknown"
                    )

                    summary = f"{name} ({status})"
                    if description:
                        summary += f": {description}"

                    policy_summaries.append(summary)

                finding = (
                    f"Retrieved {len(policies)} policy record(s). "
                    + " | ".join(policy_summaries)
                    if policy_summaries
                    else "Policy query returned no usable policy details."
                )

            else:
                finding = "Specialist result received."

            evidence.append({
                "id": index,
                "source": result.get("agent", "Specialist Agent"),
                "finding": finding,
                "details": details,
            })

        missing_information = []

        if not results:
            missing_information.append(
                "No specialist agent returned any results."
            )

        if failed_results:
            missing_information.append(
                f"{len(failed_results)} specialist result(s) were unsuccessful."
            )

        decision = "REVIEW_REQUIRED"
        recommendation = "Review the available evidence before taking action."
        reasoning = "The available specialist results require human review."
        risk_level = "MEDIUM"

        if not successful_results:
            decision = "INSUFFICIENT_INFORMATION"
            recommendation = (
                "Collect the required information and retry the assessment."
            )
            reasoning = (
                "No successful specialist results were available "
                "to support a reliable recommendation."
            )
            risk_level = "HIGH"

        elif "leave" in request_lower:
            eligibility_results = [
                result for result in successful_results
                if isinstance(result.get("eligible"), bool)
            ]

            if eligibility_results:
                values = {
                    result["eligible"] for result in eligibility_results
                }

                if values == {True}:
                    decision = "ELIGIBLE_FOR_REVIEW"
                    recommendation = (
                        "Forward the request for manager or HR approval. "
                        "This is not final approval."
                    )
                    reasoning = (
                        "The specialist result indicates that the "
                        "available eligibility criteria are met."
                    )
                    risk_level = "LOW"

                elif values == {False}:
                    decision = "ELIGIBILITY_CONCERN"
                    recommendation = (
                        "Ask HR to review the eligibility criteria "
                        "and applicable exceptions before deciding."
                    )
                    reasoning = (
                        "The specialist result indicates that the "
                        "available eligibility criteria are not met."
                    )
                    risk_level = "MEDIUM"

                else:
                    decision = "CONFLICTING_EVIDENCE"
                    recommendation = (
                        "Resolve conflicting eligibility results before acting."
                    )
                    reasoning = (
                        "Specialist agents returned conflicting eligibility values."
                    )
                    risk_level = "HIGH"

            else:
                balance_results = [
                    result for result in successful_results
                    if isinstance(result.get("leave_balance"), dict)
                ]

                balance = (
                    balance_results[0]["leave_balance"]
                    if balance_results else None
                )

                valid_balance = (
                    isinstance(balance, dict)
                    and any(
                        isinstance(balance.get(field), (int, float))
                        and not isinstance(balance.get(field), bool)
                        for field in (
                            "casual_leave", "sick_leave", "earned_leave"
                        )
                    )
                )

                decision = "LEAVE_REVIEW_REQUIRED"
                risk_level = "MEDIUM"

                if valid_balance:
                    balance_parts = []

                    for field, label in (
                        ("casual_leave", "casual"),
                        ("sick_leave", "sick"),
                        ("earned_leave", "earned"),
                    ):
                        value = balance.get(field)
                        if (
                            isinstance(value, (int, float))
                            and not isinstance(value, bool)
                        ):
                            balance_parts.append(f"{label}: {value} day(s)")

                    reasoning = (
                        "Leave balance retrieved successfully: "
                        + "; ".join(balance_parts)
                        + ". Balance information alone does not establish "
                        "eligibility or approve leave."
                    )
                    recommendation = (
                        "The leave balance is available. If an eligibility "
                        "check is needed, confirm the leave type and dates, "
                        "then follow the applicable policy and approval process."
                    )

                else:
                    reasoning = (
                        "No valid leave-balance data was returned. "
                        "Eligibility cannot be established from the available evidence."
                    )
                    recommendation = (
                        "Retrieve the current leave balance and verify "
                        "the applicable policy and approval requirements."
                    )

                    if any(term in request_lower for term in (
                        "balance", "remaining leave", "leave left"
                    )):
                        missing_information.append(
                            "The employee's current leave balance could not be verified."
                        )

                asks_for_eligibility = any(term in request_lower for term in (
                    "eligible", "eligibility", "check eligibility",
                    "can i take", "can this employee take",
                    "can the employee take", "qualify for leave",
                ))

                has_application_phrase = any(phrase in request_lower for phrase in (
                    "apply for leave", "apply leave", "request leave",
                    "take leave", "book leave",
                ))

                is_negated_application = any(phrase in request_lower for phrase in (
                    "do not apply", "don't apply", "do not request",
                    "don't request", "do not take", "don't take",
                    "not applying", "without applying",
                ))

                asks_to_apply = (
                    has_application_phrase and not is_negated_application
                )

                if asks_to_apply or asks_for_eligibility:
                    missing_information.append(
                        "The leave type and start/end dates must be "
                        "confirmed for an eligibility assessment."
                    )

        elif "attendance" in request_lower:
            attendance_summaries = [
                result["summary"]
                for result in successful_results
                if isinstance(result.get("summary"), dict)
                and isinstance(
                    result["summary"].get("attendance_percentage"),
                    (int, float),
                )
                and not isinstance(
                    result["summary"].get("attendance_percentage"), bool
                )
            ]

            if attendance_summaries:
                percentage = attendance_summaries[0]["attendance_percentage"]

                if percentage >= 90:
                    decision = "GOOD_ATTENDANCE"
                    risk_level = "LOW"
                    recommendation = (
                        "Attendance is at least 90% in the available summary. "
                        "Continue routine monitoring."
                    )
                elif percentage >= 75:
                    decision = "ATTENDANCE_REVIEW"
                    risk_level = "MEDIUM"
                    recommendation = (
                        "Review attendance records and relevant circumstances with HR."
                    )
                else:
                    decision = "ATTENDANCE_REVIEW_REQUIRED"
                    risk_level = "HIGH"
                    recommendation = (
                        "Verify attendance records and discuss relevant "
                        "circumstances with the employee before action."
                    )

                reasoning = (
                    f"The available attendance summary reports "
                    f"{percentage:.1f}% attendance. This assessment "
                    "is a review aid, not a disciplinary decision."
                )

            else:
                decision = "ATTENDANCE_DATA_INCOMPLETE"
                recommendation = (
                    "Retrieve a valid attendance summary before assessing attendance."
                )
                reasoning = "No numeric attendance percentage was available."
                missing_information.append(
                    "A numeric attendance summary was not returned."
                )

        else:
            decision = "HR_REVIEW"
            recommendation = (
                "HR should review the findings and determine the appropriate next action."
            )

        if failed_results and successful_results:
            reasoning += (
                " Some specialist results were unsuccessful, "
                "so the assessment may be incomplete."
            )

        return {
            "success": bool(successful_results),
            "agent": self.name,
            "decision": decision,
            "recommendation": recommendation,
            "reasoning": reasoning,
            "risk_level": risk_level,
            "evidence_count": len(evidence),
            "evidence": evidence,
            "missing_information": missing_information,
            "human_review_required": True,
        }


decision_agent = DecisionAgent()
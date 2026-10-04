import re

from tools.hr_policy_tool import search_hr_policy
from tools.leave_management_tool import (
    get_leave_balance,
    get_leave_requests,
    create_leave_request,
)


def _extract_date(query):
    match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", query)

    if match:
        return match.group(0)

    return None


def ask_leave_agent(employee_query, employee_id=None):

    if not employee_query or not employee_query.strip():
        return "Please enter a valid leave-related request."

    if employee_id is None:
        return (
            "I need your employee ID before I can access "
            "your leave information."
        )

    try:
        employee_id = int(employee_id)
    except (TypeError, ValueError):
        return "The employee ID is invalid."

    query_lower = employee_query.lower().strip()

    # =========================================================
    # LEAVE BALANCE
    # =========================================================

    balance_keywords = [
        "leave balance",
        "how many leave",
        "how many leaves",
        "leaves do i have",
        "leave do i have",
        "how much leave",
        "remaining leave",
        "casual leave balance",
        "casual leaves",
        "casual leave",
    ]

    if any(keyword in query_lower for keyword in balance_keywords):

        balance = get_leave_balance(employee_id)

        if not balance.get("success"):
            return (
                "I could not retrieve your leave balance. "
                "Please contact HR."
            )

        return (
            f"You have {balance['remaining']} casual leave day(s) "
            f"remaining out of {balance['total']} for {balance['year']}."
        )

    # =========================================================
    # EXISTING LEAVE REQUESTS
    # =========================================================

    request_keywords = [
        "my leave requests",
        "leave request status",
        "status of my leave",
        "show my leave",
        "pending leave",
        "approved leave",
        "rejected leave",
        "leave history",
    ]

    if any(keyword in query_lower for keyword in request_keywords):

        result = get_leave_requests(employee_id=employee_id)

        if not result.get("success"):
            return (
                "I could not retrieve your leave requests. "
                "Please contact HR."
            )

        requests = result.get("requests", [])

        if not requests:
            return "You currently have no leave requests."

        lines = ["Your recent leave requests:"]

        for request in requests[:5]:
            lines.append(
                f"Request #{request['request_id']}: "
                f"{request['leave_type']} leave, "
                f"{request['start_date']} to {request['end_date']}, "
                f"{request['days']} day(s), "
                f"Status: {request['status']}"
            )

        return "\n".join(lines)

    # =========================================================
    # NEW LEAVE REQUEST
    # =========================================================

    request_phrases = [
        "i want to request leave",
        "i want leave",
        "i need leave",
        "apply for leave",
        "request leave",
        "take leave",
        "need a day off",
    ]

    if any(phrase in query_lower for phrase in request_phrases):

        requested_date = _extract_date(employee_query)

        if not requested_date:
            return (
                "Sure. I can help you request casual leave. "
                "Please provide the leave date in YYYY-MM-DD format."
            )

        result = create_leave_request(
            employee_id=employee_id,
            leave_type="CASUAL",
            start_date=requested_date,
            end_date=requested_date,
            reason="Requested through WorkSphere Assistant"
        )

        if not result.get("success"):
            return result.get(
                "error",
                "Unable to create the leave request."
            )

        return (
            "Your leave request has been submitted successfully.\n\n"
            f"Request ID: {result['request_id']}\n"
            f"Leave type: {result['leave_type']}\n"
            f"Date: {result['start_date']}\n"
            f"Days: {result['days']}\n"
            f"Status: {result['status']}\n"
            f"Manager: {result['manager_name']}\n\n"
            "Your request is now waiting for manager approval."
        )

    # =========================================================
    # LEAVE POLICY
    # No Gemini call here.
    # =========================================================

    policy_data = search_hr_policy(employee_query)

    if (
        not policy_data
        or policy_data.startswith("No matching HR policy")
    ):
        return (
            "I could not find relevant leave policy information. "
            "Please contact the HR department."
        )

    return policy_data
from datetime import date, timedelta

from tools.leave_management_tool import (
    get_employee_context,
    get_leave_balance,
    create_leave_request,
)


def _extract_employee_id(query):
    words = query.split()

    for word in words:
        cleaned = word.strip(".,?!")
        if cleaned.isdigit():
            return int(cleaned)

    # Demo employee for the employee-facing prototype.
    return 1


def _extract_reason(query):
    lower = query.lower()

    markers = [
        "because",
        "for",
        "due to",
        "reason is",
    ]

    for marker in markers:
        if marker in lower:
            index = lower.find(marker)
            reason = query[index + len(marker):].strip(" .,:")
            if reason:
                return reason

    return "Personal work"


def ask_leave_agent(employee_query):
    """
    Leave Management Agent.

    Uses deterministic enterprise tools for leave information
    and leave-request creation. Gemini is not required here.
    """

    if not employee_query or not employee_query.strip():
        return "Please enter a valid leave-related question."

    query = employee_query.strip()
    lower = query.lower()

    employee_id = _extract_employee_id(query)

    # ---------------------------------------------------------
    # 1. Leave balance
    # ---------------------------------------------------------
    if "balance" in lower or (
        "how many" in lower
        and "leave" in lower
    ):
        balance = get_leave_balance(employee_id)

        if not balance["success"]:
            return balance["error"]

        return (
            f"You have {balance['remaining']} casual leave day(s) "
            f"remaining out of {balance['total']} for {balance['year']}."
        )

    # ---------------------------------------------------------
    # 2. Leave request
    # ---------------------------------------------------------
    request_words = [
        "request leave",
        "apply for leave",
        "want to request leave",
        "want to apply for leave",
        "need leave",
        "take leave",
    ]

    if any(word in lower for word in request_words):

        employee = get_employee_context(employee_id)

        if not employee["success"]:
            return employee["error"]

        # Demo interpretation:
        # "tomorrow" = tomorrow's date.
        if "tomorrow" in lower:
            start = date.today() + timedelta(days=1)
            end = start

        elif "today" in lower:
            start = date.today()
            end = start

        else:
            return (
                "Please provide the leave dates. "
                "For example: 'I want to request leave for tomorrow.'"
            )

        reason = _extract_reason(query)

        result = create_leave_request(
            employee_id,
            "CASUAL",
            start.isoformat(),
            end.isoformat(),
            reason,
        )

        if not result["success"]:
            return result["error"]

        return (
            f"Your leave request has been submitted successfully.\n\n"
            f"Request ID: {result['request_id']}\n"
            f"Leave type: {result['leave_type']}\n"
            f"Date: {result['start_date']}\n"
            f"Days: {result['days']}\n"
            f"Status: {result['status']}\n"
            f"Manager: {result['manager_name']}\n\n"
            f"Your request is now waiting for manager approval."
        )

    # ---------------------------------------------------------
    # 3. General leave information
    # ---------------------------------------------------------
    return (
        "Employees receive 12 casual leaves per calendar year. "
        "Planned leave should be requested at least 2 working days "
        "in advance, and leave requests require manager approval."
    )
def select_tool(query):
    """
    Select the most appropriate tool based on the employee query.
    """

    if not query or not query.strip():
        return {
            "success": False,
            "error": "Query is required."
        }

    query_lower = query.lower()

    # Employee information queries
    employee_keywords = [
    "employee information",
    "information for employee",
    "employee details",
    "details for employee",
    "employee record",
    "employee profile",
    "employee id",
    "department of employee",
    "email of employee"
    ]

    if any(keyword in query_lower for keyword in employee_keywords):
        return {
            "success": True,
            "tool": "get_employee_info",
            "reason": "The query requests employee-specific information."
        }

    # HR policy queries
    policy_keywords = [
        "policy",
        "rules",
        "leave",
        "casual leave",
        "sick leave",
        "work from home",
        "wfh",
        "attendance",
        "working hours"
    ]

    if any(keyword in query_lower for keyword in policy_keywords):
        return {
            "success": True,
            "tool": "search_hr_policy",
            "reason": "The query requests information from company HR policies."
        }

    return {
        "success": False,
        "error": "No suitable tool was found for this query."
    }
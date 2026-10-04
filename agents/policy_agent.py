from tools.rag_tool import search_hr_policy_rag


def ask_policy_agent(employee_query):
    """
    Enterprise HR Policy Agent.

    Retrieves company policy directly from the HR policy
    knowledge base without requiring an LLM API call.
    """

    if not employee_query or not employee_query.strip():
        return "Please enter a valid HR policy question."

    try:
        result = search_hr_policy_rag(employee_query.strip())

        if not result:
            return (
                "I could not find relevant company policy information. "
                "Please contact the HR department."
            )

        return str(result)

    except Exception as e:
        print("POLICY ERROR:", repr(e))

        return (
            "I could not retrieve the requested HR policy. "
            "Please contact the HR department."
        )
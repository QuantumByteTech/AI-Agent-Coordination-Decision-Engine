from tools.tool_selector import select_tool
from tools.tool_executor import execute_tool


def execute_agent_action(query):
    """
    Select and execute the appropriate tool for an HR query.
    """

    # Step 1: Select the appropriate tool
    selection = select_tool(query)

    if not selection["success"]:
        return {
            "success": False,
            "stage": "tool_selection",
            "error": selection["error"]
        }

    selected_tool = selection["tool"]

    # Step 2: Extract employee ID if employee tool is selected
    if selected_tool == "get_employee_info":

        words = query.split()
        employee_id = None

        for word in words:
            cleaned = word.strip(".,?!")

            if cleaned.isdigit():
                employee_id = cleaned
                break

        if not employee_id:
            return {
                "success": False,
                "stage": "validation",
                "error": "A valid employee ID is required."
            }

        tool_input = employee_id

    else:
        # Policy tools receive the complete employee question
        tool_input = query

    # Step 3: Execute selected tool
    result = execute_tool(selected_tool, tool_input)

    # Step 4: Return complete pipeline result
    return {
        "success": result["success"],
        "stage": "tool_execution",
        "selected_tool": selected_tool,
        "selection_reason": selection["reason"],
        "tool_result": result
    }
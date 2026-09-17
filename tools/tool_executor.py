from tools.hr_policy_tool import search_hr_policy
from tools.employee_api_tool import get_employee_info


def execute_tool(tool_name, tool_input):
    """
    Execute the selected enterprise tool and return its result.
    """

    try:
        if tool_name == "search_hr_policy":
            result = search_hr_policy(tool_input)

        elif tool_name == "get_employee_info":
            result = get_employee_info(tool_input)

        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }

        return {
            "success": True,
            "tool": tool_name,
            "result": result
        }

    except Exception as e:
        return {
            "success": False,
            "tool": tool_name,
            "error": str(e)
        }
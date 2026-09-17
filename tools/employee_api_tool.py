import requests


def get_employee_info(employee_id: str):
    """
    Retrieve employee information from an external API
    with input validation and exception handling.
    """

    # Input validation
    if not employee_id:
        return {
            "success": False,
            "error": "Employee ID is required."
        }

    employee_id = str(employee_id).strip()

    if not employee_id.isdigit():
        return {
            "success": False,
            "error": "Employee ID must contain only numbers."
        }

    url = f"https://jsonplaceholder.typicode.com/users/{employee_id}"

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 404:
            return {
                "success": False,
                "error": f"Employee ID {employee_id} was not found."
            }

        response.raise_for_status()

        data = response.json()

        return {
            "success": True,
            "employee_id": employee_id,
            "name": data.get("name"),
            "email": data.get("email"),
            "department": data.get("company", {}).get("name")
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "The employee service request timed out."
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Employee service request failed: {str(e)}"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }
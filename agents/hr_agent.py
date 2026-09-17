from google import genai
from dotenv import load_dotenv
import os

from tools.hr_policy_tool import search_hr_policy
from tools.employee_api_tool import get_employee_info

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)


def ask_hr_agent(employee_query):

    if not employee_query or not employee_query.strip():
        return "Please enter a valid HR question."

    try:

        # Handle employee information requests
        if "employee" in employee_query.lower() and (
            "information" in employee_query.lower()
            or "details" in employee_query.lower()
        ):

            words = employee_query.split()

            employee_id = None

            for word in words:
                cleaned = word.strip(".,?!")
                if cleaned.isdigit():
                    employee_id = cleaned
                    break

            if not employee_id:
                return "Please provide a valid employee ID."

            employee_data = get_employee_info(employee_id)

            if not employee_data.get("success", False):
                return f"Employee lookup failed: {employee_data.get('error', 'Unknown error.')}"

            employee_text = f"""
Employee Information:

Employee ID: {employee_data['employee_id']}
Name: {employee_data['name']}
Department: {employee_data['department']}
Email: {employee_data['email']}
"""

            return employee_text.strip()

        # Otherwise search HR policies
        policy_data = search_hr_policy(employee_query)

        if not policy_data or policy_data.startswith(
            "No matching HR policy"
        ):
            return (
                "I could not find relevant information in the available "
                "HR policies. Please contact the HR department."
            )

        prompt = f"""
You are an AI HR Assistant for an enterprise organization.

Answer the employee's question using ONLY the retrieved
company information below.

RETRIEVED INFORMATION:
{policy_data}

Rules:
1. Use the retrieved information as the source of truth.
2. Do not invent company-specific policies.
3. If the information does not answer the question,
   tell the employee to contact HR.
4. Give a clear and professional answer.
5. Keep the response concise and easy to understand.

Employee Question:
{employee_query}
"""

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:

        return (
            "Sorry, I was unable to process your HR request. "
            "Please try again or contact the HR department.\n\n"
            f"System error: {str(e)}"
        )
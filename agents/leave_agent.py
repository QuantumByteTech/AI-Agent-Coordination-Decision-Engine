from google import genai
from dotenv import load_dotenv
import os

from tools.hr_policy_tool import search_hr_policy
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)


def ask_leave_agent(employee_query):

    policy_data = search_hr_policy(employee_query)

    prompt = f"""
You are an AI Leave Management Agent for an enterprise HR system.

Answer the employee's question using the official company leave
policy information provided below.

COMPANY LEAVE POLICY:
{policy_data}

Important rules:
1. Use the provided policy information as the source of truth.
2. Do not invent leave rules or entitlements.
3. If the employee asks something that is not covered by the
   provided policy, clearly say that the HR department should
   be contacted.
4. Give a clear and professional answer.
5. Keep the answer easy for an employee to understand.

Employee Question:
{employee_query}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text
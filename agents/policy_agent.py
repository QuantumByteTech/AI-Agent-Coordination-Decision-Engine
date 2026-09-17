from google import genai
from dotenv import load_dotenv
import os

from tools.rag_tool import search_hr_policy_rag

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)


def ask_policy_agent(employee_query):
    """
    Policy Agent using RAG-based intelligent tool calling.

    Gemini decides when the HR policy search tool is required.
    The tool retrieves relevant policies from the vector database.
    """

    tools = [search_hr_policy_rag]

    prompt = f"""
You are an AI HR Policy Agent for an enterprise organization.

Your job is to answer employee questions about company HR policies.

You have access to an HR policy search tool called
search_hr_policy_rag.

Rules:
1. Use the search_hr_policy_rag tool whenever the employee asks
   about a company-specific HR policy.
2. Use the information returned by the tool as the source of truth.
3. Do not invent company-specific policies.
4. If the tool does not return relevant information,
   tell the employee to contact the HR department.
5. Give a clear and professional answer.
6. Keep the answer easy for an employee to understand.

Employee Question:
{employee_query}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config={
            "tools": tools
        }
    )

    return response.text
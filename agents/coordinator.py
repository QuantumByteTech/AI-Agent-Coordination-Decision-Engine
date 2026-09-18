from google import genai
from dotenv import load_dotenv
import os

from agents.hr_agent import ask_hr_agent
from agents.policy_agent import ask_policy_agent
from agents.leave_agent import ask_leave_agent

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)


def classify_query(employee_query):
    prompt = f"""
You are an HR Coordinator Agent.

Classify the employee's question into exactly ONE category.

Categories:

POLICY
- HR policies
- Attendance rules
- Work-from-home rules
- Working hours
- Benefits
- Company rules

LEAVE
- Applying for leave
- Leave types
- Leave approval
- Leave balance
- Sick leave
- Casual leave
- Vacation leave

GENERAL
- Onboarding
- Recruitment
- Employee records
- General HR support
- Other HR questions

IRRELEVANT
- Questions unrelated to HR
- General knowledge
- Mathematics
- Programming or coding questions
- Entertainment
- Personal advice unrelated to employment
- Weather, news, sports, etc.

Employee Question:
{employee_query}

Return ONLY ONE word:
POLICY
LEAVE
GENERAL
IRRELEVANT
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text.strip().upper()


def ask_coordinator(employee_query):
    category = classify_query(employee_query)

    if "LEAVE" in category:
        print("[Coordinator] Routing to Leave Agent...")
        return ask_leave_agent(employee_query)

    elif "POLICY" in category:
        print("[Coordinator] Routing to Policy Agent...")
        return ask_policy_agent(employee_query)

    elif "GENERAL" in category:
        print("[Coordinator] Routing to HR Agent...")
        return ask_hr_agent(employee_query)

    elif "IRRELEVANT" in category:
        return "I can only assist with HR-related questions such as company policies, leave, attendance, work-from-home guidelines, and employee information."

    else:
        return "I can only assist with HR-related questions."
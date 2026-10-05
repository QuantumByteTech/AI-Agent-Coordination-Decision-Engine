from google import genai
from dotenv import load_dotenv
import os
import re

from tools.employee_db_tool import get_employee_info
from agents.hr_agent import ask_hr_agent
from agents.policy_agent import ask_policy_agent
from agents.leave_agent import ask_leave_agent

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)


# =========================================================
# EMPLOYEE ID EXTRACTION
# =========================================================

def extract_employee_id(text):
    # Remove dates such as 2026-10-10 before searching for IDs
    text_without_dates = re.sub(
        r"\b\d{4}-\d{2}-\d{2}\b",
        "",
        text
    )

    match = re.search(
        r"\b(?:employee\s*(?:id)?\s*)?(\d+)\b",
        text_without_dates,
        re.IGNORECASE
    )

    return int(match.group(1)) if match else None


# =========================================================
# GEMINI CLASSIFICATION
# =========================================================

def classify_query(employee_query):

    prompt = f"""
You are an HR Coordinator Agent for an enterprise HR system.

Classify the employee request into exactly ONE category.

POLICY:
- HR policies
- Work from home
- Attendance
- Working hours
- Benefits
- Company rules

LEAVE:
- Leave balance
- Apply for leave
- Leave request
- Leave approval
- Leave rejection
- Sick leave
- Casual leave
- Vacation leave
- Leave history

GENERAL:
- Employee information
- Onboarding
- Recruitment
- General HR support

IRRELEVANT:
- Programming
- Mathematics
- Entertainment
- Sports
- Weather
- General knowledge
- Personal advice
- Any non-HR request

Employee request:
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


# =========================================================
# MAIN COORDINATOR
# =========================================================

def ask_coordinator(employee_query, employee_id=None):

    if not employee_query or not employee_query.strip():
        return {
            "success": False,
            "category": "ERROR",
            "agent": "Coordinator",
            "message": "Please enter an HR-related request."
        }

    employee_query = employee_query.strip()
    query_lower = employee_query.lower()
    if employee_id is None:
        return {
        "success": False,
        "category": "AUTHENTICATION",
        "agent": "Coordinator",
        "message": "Your session has expired. Please sign in again."
        }


    # =====================================================
    # EMPLOYEE INFORMATION
    # =====================================================

    employee_info_keywords = [
        "employee information",
        "employee info",
        "employee details",
        "employee profile",
        "employee record",
        "employee data",
        "show me information",
        "show information",
        "show details",
        "details for employee",
        "information for employee",
        "profile for employee"
    ]

    if any(keyword in query_lower for keyword in employee_info_keywords):

        # IMPORTANT:
        # Always use the logged-in employee.
        # Do not allow the user to retrieve another employee's
        # information simply by typing another employee ID.

        result = get_employee_info(employee_id)

        if not result.get("success"):
            return {
                "success": False,
                "category": "EMPLOYEE",
                "agent": "Employee Service",
                "message": result.get(
                    "error",
                    "Employee information could not be retrieved."
                )
            }

        return {
            "success": True,
            "category": "EMPLOYEE",
            "agent": "Employee Service",
            "message": (
                f"Employee Profile\n\n"
                f"Name: {result['name']}\n"
                f"Employee ID: {result['employee_id']}\n"
                f"Department: {result['department']}\n"
                f"Designation: {result['designation']}\n"
                f"Email: {result['email']}\n"
                f"Joining Date: {result['joining_date']}"
            ),
            "employee": result
        }


    # =====================================================
    # LEAVE REQUESTS
    # =====================================================

    leave_keywords = [
        "leave",
        "casual leave",
        "sick leave",
        "vacation leave",
        "day off",
        "leave balance",
        "leave request",
        "leave history",
        "leave approval",
        "leave rejection"
    ]

    if any(keyword in query_lower for keyword in leave_keywords):

        # IMPORTANT:
        # Use the employee ID from the authenticated session.
        # There is NO fallback to employee 1.

        return {
            "success": True,
            "category": "LEAVE",
            "agent": "Leave Agent",
            "message": str(
                ask_leave_agent(
                    employee_query,
                    employee_id=employee_id
                )
            ).strip()
        }


    # =====================================================
    # POLICY REQUESTS
    # =====================================================

    policy_keywords = [
        "work from home",
        "wfh",
        "attendance policy",
        "attendance",
        "working hours",
        "company policy",
        "company rule",
        "benefits",
        "hr policy"
    ]

    if any(keyword in query_lower for keyword in policy_keywords):

        return {
            "success": True,
            "category": "POLICY",
            "agent": "Policy Agent",
            "message": str(
                ask_policy_agent(employee_query)
            ).strip()
        }


    # =====================================================
    # IRRELEVANT REQUESTS
    # Handle obvious non-HR requests locally so they do not
    # consume Gemini API quota.
    # =====================================================

    irrelevant_keywords = [
        "tell me a joke",
        "joke",
        "make me laugh",
        "funny story",
        "movie",
        "movies",
        "song",
        "songs",
        "music",
        "weather",
        "cricket",
        "football",
        "soccer",
        "basketball",
        "sports",
        "math",
        "mathematics",
        "calculate",
        "programming",
        "python code",
        "java code",
        "write code",
        "code for",
        "recipe",
        "cooking",
        "relationship advice",
        "love advice"
    ]

    if any(keyword in query_lower for keyword in irrelevant_keywords):

        return {
            "success": False,
            "category": "IRRELEVANT",
            "agent": "Coordinator",
            "message": (
                "I can assist with HR-related services such as "
                "company policies, leave, attendance, work-from-home "
                "guidelines, employee information, and onboarding."
            )
        }


    # =====================================================
    # GEMINI ROUTING
    # Used only when local routing cannot determine the request.
    # =====================================================

    category = classify_query(employee_query)


    # =====================================================
    # GEMINI → POLICY
    # =====================================================

    if category == "POLICY":

        return {
            "success": True,
            "category": "POLICY",
            "agent": "Policy Agent",
            "message": str(
                ask_policy_agent(employee_query)
            ).strip()
        }


    # =====================================================
    # GEMINI → LEAVE
    # =====================================================

    if category == "LEAVE":

        return {
            "success": True,
            "category": "LEAVE",
            "agent": "Leave Agent",
            "message": str(
                ask_leave_agent(
                    employee_query,
                    employee_id=employee_id
                )
            ).strip()
        }


    # =====================================================
    # GEMINI → GENERAL
    # =====================================================

    if category == "GENERAL":

        return {
            "success": True,
            "category": "GENERAL",
            "agent": "HR Assistant",
            "message": str(
                ask_hr_agent(employee_query)
            ).strip()
        }


    # =====================================================
    # GEMINI → IRRELEVANT
    # =====================================================

    if category == "IRRELEVANT":

        return {
            "success": False,
            "category": "IRRELEVANT",
            "agent": "Coordinator",
            "message": (
                "I can assist with HR-related services such as "
                "company policies, leave, attendance, work-from-home "
                "guidelines, employee information, and onboarding."
            )
        }


    # =====================================================
    # FALLBACK
    # =====================================================

    return {
        "success": False,
        "category": "ERROR",
        "agent": "Coordinator",
        "message": (
            "I could not determine the type of HR request. "
            "Please try asking about policies, leave, employee "
            "information, onboarding, or other HR services."
        )
    }
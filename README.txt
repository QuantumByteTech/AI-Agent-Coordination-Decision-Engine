AI Agent Coordination & Decision Engine — role-access correction

FILES
- frontend/index.html
- frontend/app.js
- frontend/style.css
- frontend/server.py (unchanged static frontend server)
- backend/app/main.py (backend access-control patch; merge into your existing app/api/main.py)

ROLE DESIGN
HR:
- Enterprise overview and analytics
- Ask/execute existing HR workflows
- Operations and workflow architecture
- Employee Context
- Department management

EMPLOYEE:
- My Information (overview with their own profile and leave balance)
- Ask HR (policy questions, own information requests, and leave requests)
- No operations, architecture, employee directory, department management, or enterprise analytics

SESSION SAFETY
- Logout clears stored authentication and role-specific state.
- The UI resets chat/trace when a session is initialized so a new account does not inherit the previous user's conversation.
- Frontend role hiding is convenience, not the security boundary. The backend must enforce the same permissions.

INSTALL
1. Back up your current frontend/index.html, frontend/app.js, and frontend/style.css.
2. Replace those three files with the matching files in this package's frontend folder.
3. Back up your current backend app/api/main.py.
4. Merge backend/app/main.py into your existing app/api/main.py (do not create a new package path named backend/app inside the project). The patched route permits only employee-owned leave requests, own-information requests, and policy questions through the existing workflow service/policy agent; HR retains the existing workflow path.
5. Restart Uvicorn and the frontend server. Hard-refresh the browser (Ctrl+Shift+R).

IMPORTANT TESTS BEFORE PRESENTING
- HR login: verify overview, OPS, FLOW, Employee Context, and Departments all work.
- Employee login: verify only CORE and ASK navigation are visible; direct attempts to open HR-only views should be blocked.
- Employee overview should show only their own profile/leave data, not enterprise analytics.
- Employee asks: "What is the leave policy?", "Show my employee information", and a leave request containing leave type, start date, end date, and reason.
- Try an employee request for another person's data and HR approval/admin actions; those should not be allowed.

NOTE
The backend patch routes permitted leave requests through the existing workflow_service.execute implementation. Verify in your running database that the existing leave agent actually persists a submitted request and returns the expected result; this package cannot run against your local database here.

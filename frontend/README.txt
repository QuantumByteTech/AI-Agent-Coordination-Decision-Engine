Department dashboard update

Copy these four files into your project's frontend folder, replacing the existing files:
- index.html
- app.js
- style.css
- server.py

Keep a backup of your existing frontend folder first. This patch does not touch the database or backend.

Restart frontend/server.py after replacing files. Keep the FastAPI backend running. Open http://127.0.0.1:5500, sign in as HR, and choose DEPARTMENTS.

The Department page calls GET /api/departments/, PUT /api/departments/{department_id}/target, and PUT /api/departments/assignments/{employee_id}. Only HR should be able to use these backend endpoints. Saving a target or assigning an employee changes the database only after the corresponding action is submitted.

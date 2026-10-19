/* ============================================================
   AI AGENT COORDINATION & DECISION ENGINE
   Role-aware frontend controller
   ============================================================ */

const auth = {
  token: localStorage.getItem("hr_auth_token"),
  role: localStorage.getItem("hr_auth_role"),
  employeeId: Number(localStorage.getItem("hr_employee_id") || 0)
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const state = {
  employeeId: auth.employeeId || 0,
  contextEmployeeId: 0,
  lastWorkflow: null,
  employees: [],
  overviewLoaded: false,
  dashboardOverview: null,
  workflowData: null,
  activityData: null,
  pendingLeaveRequests: []
};

/* -------------------- API CLIENT -------------------- */

async function api(path, options = {}) {
  const normalizedPath = path.startsWith("/api")
    ? path
    : `/api${path.startsWith("/") ? path : `/${path}`}`;

  const headers = {
    Accept: "application/json",
    ...(auth.token ? { Authorization: `Bearer ${auth.token}` } : {}),
    ...(options.headers || {})
  };

  if (options.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const API_BASE_URL = "http://127.0.0.1:8000";

const response = await fetch(`${API_BASE_URL}${normalizedPath}`, {
    ...options,
    headers
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail || data.message || `Request failed (${response.status})`
    );
  }

  return data;
}

/* -------------------- AUTHENTICATION -------------------- */

async function login(username, password) {
  const response = await fetch("http://127.0.0.1:8000/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || data.message || "Authentication failed.");
  }

  const token = data.token;
  const role = data.user?.role;
  const employeeId = Number(data.user?.employee_id || 0);

  if (!token || !["HR", "EMPLOYEE"].includes(role)) {
    throw new Error("Invalid login response from the backend.");
  }

  if (role === "EMPLOYEE" && employeeId <= 0) {
    throw new Error(
      "This employee account is not linked to an employee record."
    );
  }

  auth.token = token;
  auth.role = role;
  auth.employeeId = employeeId;

  localStorage.setItem("hr_auth_token", token);
  localStorage.setItem("hr_auth_role", role);
  localStorage.setItem("hr_employee_id", String(employeeId));

  state.employeeId = role === "EMPLOYEE" ? employeeId : 0;
  state.contextEmployeeId = 0;
  state.lastWorkflow = null;
  state.overviewLoaded = false;
  state.dashboardOverview = null;
  state.workflowData = null;
  state.activityData = null;
}

function clearSession() {
  auth.token = null;
  auth.role = null;
  auth.employeeId = 0;

  state.employeeId = 0;
  state.contextEmployeeId = 0;
  state.lastWorkflow = null;
  state.employees = [];
  state.overviewLoaded = false;
  state.dashboardOverview = null;
  state.workflowData = null;
  state.activityData = null;

  localStorage.removeItem("hr_auth_token");
  localStorage.removeItem("hr_auth_role");
  localStorage.removeItem("hr_employee_id");
}

function logout() {
  clearSession();
  updateSessionUI();

  if ($("#loginPassword")) $("#loginPassword").value = "";
  if ($("#loginUsername")) $("#loginUsername").value = "";
  if ($("#loginError")) $("#loginError").textContent = "";
  if ($("#question")) $("#question").value = "";
  if ($("#loginScreen")) $("#loginScreen").style.display = "";
  if ($(".app-layout")) $(".app-layout").style.display = "none";
  if ($(".topbar")) $(".topbar").style.display = "none";
  $("#loginUsername")?.focus();
  toast("You have been logged out.");
}

$("#sidebarLogout")?.addEventListener("click", logout);
$("#logoutBtn")?.addEventListener("click", logout);

/* -------------------- SHARED UI HELPERS -------------------- */

function toast(message) {
  const element = $("#toast");
  if (!element) return;

  element.textContent = message;
  element.classList.add("show");

  clearTimeout(toast.timer);

  toast.timer = setTimeout(() => {
    element.classList.remove("show");
  }, 3000);
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, character => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  })[character]);
}

function setText(selector, value) {
  const element = $(selector);
  if (element) element.textContent = value ?? "—";
}

function setDisplay(selector, visible, displayValue = "") {
  const element = $(selector);
  if (element) {
    element.style.display = visible ? displayValue : "none";
  }
}

function setMetric(labelId, valueId, subtitleId, label, value, subtitle) {
  setText(`#${labelId}`, label);
  setText(`#${valueId}`, value);
  setText(`#${subtitleId}`, subtitle);
}

function normalizeArray(data, keys = []) {
  if (Array.isArray(data)) return data;

  for (const key of keys) {
    if (Array.isArray(data?.[key])) return data[key];
  }

  return [];
}

function formatTime(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value).slice(0, 19);
  }

  return date.toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  });
}

function showEmpty(containerSelector, message) {
  const container = $(containerSelector);
  if (!container) return;

  container.innerHTML =
    `<div class="empty-state">${escapeHtml(message)}</div>`;
}

function requireLogin() {
  if (!auth.token || !["HR", "EMPLOYEE"].includes(auth.role)) {
    toast("Please sign in first.");
    return false;
  }

  return true;
}

function getEmployeeName(employee) {
  return employee?.name ||
    [employee?.first_name, employee?.last_name].filter(Boolean).join(" ") ||
    employee?.employee_code ||
    `Employee ${employee?.id ?? ""}`;
}

function getLeaveBalance(response) {
  return response?.leave_balance || response?.balance || {};
}

function hasLeaveBalance(balance) {
  return [
    balance.casual_leave,
    balance.sick_leave,
    balance.earned_leave
  ].some(value => value !== undefined && value !== null);
}

function getTotalLeave(balance) {
  return Number(balance.casual_leave || 0) +
    Number(balance.sick_leave || 0) +
    Number(balance.earned_leave || 0);
}

/* -------------------- ROLE-BASED NAVIGATION -------------------- */

function updateSessionUI() {
  const loggedIn = Boolean(auth.token && ["HR", "EMPLOYEE"].includes(auth.role));
  const isHR = loggedIn && auth.role === "HR";

  const loginScreen = $("#loginScreen");
  if (loginScreen) loginScreen.style.display = loggedIn ? "none" : "";
  const appLayout = $(".app-layout");
  if (appLayout) appLayout.style.display = loggedIn ? "" : "none";
  const topbar = $(".topbar");
  if (topbar) topbar.style.display = loggedIn ? "" : "none";
  const logoutButton = $("#logoutBtn");
  if (logoutButton) logoutButton.hidden = !loggedIn;

  setText("#currentRole", loggedIn ? auth.role : "GUEST");

  // Apply role access to every marked navigation item, view and dashboard section.
  $$('[data-hr-only]').forEach(element => {
    element.hidden = !isHR;
    element.style.display = isHR ? "" : "none";
  });

  // Employees get exactly two destinations: their own overview and Ask HR.
  $$('[data-view="overview"], [data-view="assistant"]').forEach(button => {
    button.hidden = !loggedIn;
    button.style.display = loggedIn ? "" : "none";
  });
  $$(".rail-btn").forEach(button => {
    if (button.id === "sidebarLogout") {
      button.hidden = !loggedIn;
      button.style.display = loggedIn ? "" : "none";
    }
  });

  if (!loggedIn) {
    $$(".view").forEach(view => {
      view.classList.remove("active");
      view.style.display = "none";
    });
    $$(".rail-btn").forEach(button => button.classList.remove("active"));
    if ($("#question")) $("#question").value = "";
    if ($("#messages")) {
      $("#messages").innerHTML = '<div class="chat-intro"><div class="intro-orb">AI</div><strong>What can I help you with?</strong><p>Sign in to ask a question or request leave.</p></div>';
    }
    return;
  }

  // Reset all views to a predictable role-safe state after login/account switching.
  $$(".view").forEach(view => {
    const hrOnly = view.hasAttribute("data-hr-only");
    view.style.display = hrOnly && !isHR ? "none" : "";
    view.classList.remove("active");
  });
  const landing = $("#overview");
  if (landing) {
    landing.style.display = "";
    landing.classList.add("active");
  }
  $$(".rail-btn").forEach(button => button.classList.remove("active"));
  $('[data-view="overview"]')?.classList.add("active");

  // Employee overview must not display enterprise-wide information or analytics.
  setDisplay(".agent-radar", isHR);
  setDisplay(".mini-metrics", isHR);
  setDisplay(".analytics-heading", isHR);
  setDisplay("#analyticsGrid", isHR);
  const pipeline = $$("#overview .lower-grid > .panel")[1];
  if (pipeline) pipeline.style.display = isHR ? "" : "none";
  setDisplay("#activityViewBtn", isHR);

  setText("#pulseDescription", isHR
    ? "A unified view of employee operations, policy intelligence, workflow coordination, and decision activity."
    : "View your own employee information and leave balance, or ask HR questions and request leave.");
  setText("#assistantDescription", isHR
    ? "Submit an HR request and inspect its execution trace."
    : "Ask HR questions or submit a leave request for your own employee record.");
  setText("#chatIntroText", isHR
    ? "Ask an HR-related question or select an example below."
    : "Ask about HR policies or request leave. Only your own employee record is used.");

  // Do not carry a previous user's chat or trace into a new session.
  if ($("#messages")) {
    $("#messages").innerHTML = `<div class="chat-intro"><div class="intro-orb">AI</div><strong>${isHR ? "What can I help you coordinate?" : "What can I help you with?"}</strong><p>${isHR ? "Ask an HR-related question or select an example below." : "Ask HR policy questions or request leave for your own record."}</p></div>`;
  }
  setText("#requestId", "WAITING FOR REQUEST");
  setText("#traceBadge", "WAITING");
  setText("#radarStatus", "IDLE");
}

function switchView(name) {
  if (!requireLogin()) return;

  const hrOnlyViews = ["operations", "flow", "employee-context", "departments"];

  if (auth.role !== "HR" && (hrOnlyViews.includes(name) || !["overview", "assistant"].includes(name))) {
    toast("This section is available to HR users only.");
    return;
  }

  const target = $(`#${CSS.escape(name)}`);

  if (!target || !target.classList.contains("view")) {
    toast("That section is not available.");
    return;
  }

  $$(".view").forEach(view => {
    view.classList.toggle("active", view.id === name);
  });

  $$(".rail-btn").forEach(button => {
    button.classList.toggle("active", button.dataset.view === name);
  });

  if (name === "overview") loadOverview();
  if (name === "operations") loadOperations();
  if (name === "departments") loadDepartments();
  if (name === "leave-requests") loadLeaveRequests();
  if (name === "employee-context") {
    if (state.contextEmployeeId > 0) {
      loadEmployeeContext(state.contextEmployeeId);
    }
  }
}

/* -------------------- NAVIGATION EVENTS -------------------- */

$$(".rail-btn").forEach(button => {
  button.addEventListener("click", () => {
    switchView(button.dataset.view);
  });
});

$$("[data-view-jump]").forEach(button => {
  button.addEventListener("click", () => {
    switchView(button.dataset.viewJump);
  });
});

/* -------------------- HR EMPLOYEE SELECTOR -------------------- */

function renderContextEmployeeOptions(searchTerm = "") {
  const select = $("#contextEmployeeId");
  if (!select) return;

  const query = searchTerm.trim().toLowerCase();
  const previousValue = select.value;

  select.innerHTML = "";

  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = query
    ? "Choose a matching employee..."
    : "Choose an employee...";
  select.appendChild(placeholder);

  const matches = state.employees.filter(employee => {
    const searchable = [
      getEmployeeName(employee),
      employee.employee_code,
      employee.email,
      employee.id
    ].filter(Boolean).join(" ").toLowerCase();

    return searchable.includes(query);
  });

  matches.forEach(employee => {
    const option = document.createElement("option");
    option.value = String(employee.id);
    option.textContent =
      `${getEmployeeName(employee)} · ${employee.employee_code || `ID ${employee.id}`}`;
    select.appendChild(option);
  });

  const previousStillExists = matches.some(
    employee => String(employee.id) === previousValue
  );

  if (previousStillExists) {
    select.value = previousValue;
  } else {
    select.value = "";
  }

  if (query && matches.length === 0) {
    const noMatch = document.createElement("option");
    noMatch.value = "";
    noMatch.textContent = "No matching employees";
    noMatch.disabled = true;
    select.appendChild(noMatch);
  }
}

async function loadEmployeeOptions() {
  if (auth.role !== "HR") return;

  try {
    const data = await api("/employees/");
    state.employees = normalizeArray(data, ["employees", "items"]);

    renderContextEmployeeOptions($("#employeeSearch")?.value || "");

    const select = $("#contextEmployeeId");
    if (select && state.contextEmployeeId > 0) {
      const exists = state.employees.some(
        employee => Number(employee.id) === state.contextEmployeeId
      );

      select.value = exists ? String(state.contextEmployeeId) : "";
    }
  } catch (error) {
    console.error("Could not load employee list:", error);
    toast("Could not load the employee list.");
  }
}

/* -------------------- HR DEPARTMENT MANAGEMENT -------------------- */

state.departments = [];

function renderDepartmentSelectors() {
  const employeeSelect = $("#departmentEmployeeSelect");
  const departmentSelect = $("#departmentAssignmentSelect");
  if (!employeeSelect || !departmentSelect) return;

  const oldEmployee = employeeSelect.value;
  const oldDepartment = departmentSelect.value;
  employeeSelect.innerHTML = '<option value="">Select an employee</option>';
  departmentSelect.innerHTML = '<option value="">Select a department</option>';

  state.employees.forEach(employee => {
    const option = document.createElement("option");
    option.value = String(employee.id);
    const code = employee.employee_code || `ID ${employee.id}`;
    option.textContent = `${getEmployeeName(employee)} · ${code}`;
    employeeSelect.appendChild(option);
  });

  state.departments.forEach(department => {
    const option = document.createElement("option");
    option.value = String(department.id);
    option.textContent = `${department.name} · ${department.location}`;
    departmentSelect.appendChild(option);
  });

  if ([...employeeSelect.options].some(option => option.value === oldEmployee)) {
    employeeSelect.value = oldEmployee;
  }
  if ([...departmentSelect.options].some(option => option.value === oldDepartment)) {
    departmentSelect.value = oldDepartment;
  }
}

function renderDepartmentsTable() {
  const tbody = $("#departmentTableBody");
  if (!tbody) return;

  if (!state.departments.length) {
    tbody.innerHTML = '<tr><td colspan="7">No departments were returned by the server.</td></tr>';
    return;
  }

  tbody.innerHTML = state.departments.map(department => `
    <tr>
      <td><strong>${escapeHtml(department.name)}</strong><small class="department-id">Department ID ${Number(department.id)}</small></td>
      <td>${escapeHtml(department.location)}</td>
      <td>${Number(department.active_headcount || 0)}</td>
      <td>${Number(department.total_employees || 0)}</td>
      <td><label class="sr-only" for="target-${Number(department.id)}">Target for ${escapeHtml(department.name)}</label><input class="target-input" id="target-${Number(department.id)}" type="number" min="0" step="1" value="${Number(department.target_headcount || 0)}" /></td>
      <td><span class="gap-value">${Number(department.hiring_gap || 0)}</span></td>
      <td><button class="ghost-btn target-save-btn" type="button" data-save-target="${Number(department.id)}">Save</button></td>
    </tr>
  `).join("");

  const active = state.departments.reduce((sum, d) => sum + Number(d.active_headcount || 0), 0);
  const hiringGap = state.departments.reduce((sum, d) => sum + Number(d.hiring_gap || 0), 0);
  const targetsSet = state.departments.filter(d => Number(d.target_headcount || 0) > 0).length;
  setText("#departmentCount", state.departments.length);
  setText("#departmentActiveCount", active);
  setText("#departmentHiringGap", hiringGap);
  setText("#departmentTargetsSet", `${targetsSet}/${state.departments.length}`);
}

async function loadDepartments() {
  if (auth.role !== "HR") {
    toast("Department management is available to HR users only.");
    return;
  }

  const tbody = $("#departmentTableBody");
  if (tbody) tbody.innerHTML = '<tr><td colspan="7">Loading department data…</td></tr>';

  try {
    const data = await api("/departments/");
    state.departments = normalizeArray(data, ["departments", "items"]);

    if (!state.employees.length) {
      const employeesData = await api("/employees/");
      state.employees = normalizeArray(employeesData, ["employees", "items"]);
    }

    renderDepartmentsTable();
    renderDepartmentSelectors();
  } catch (error) {
    console.error("Could not load departments:", error);
    if (tbody) tbody.innerHTML = `<tr><td colspan="7">${escapeHtml(error.message)}</td></tr>`;
    toast(`Department loading failed: ${error.message}`);
  }
}

$("#refreshDepartments")?.addEventListener("click", loadDepartments);

$("#departmentTableBody")?.addEventListener("click", async event => {
  const button = event.target.closest("[data-save-target]");
  if (!button) return;
  if (auth.role !== "HR") {
    toast("Only HR can update department targets.");
    return;
  }

  const departmentId = Number(button.dataset.saveTarget);
  const input = $(`#target-${CSS.escape(String(departmentId))}`);
  const target = Number(input?.value);
  if (!Number.isInteger(target) || target < 0) {
    toast("Enter a whole-number target of zero or greater.");
    input?.focus();
    return;
  }

  button.disabled = true;
  button.textContent = "Saving…";
  try {
    await api(`/departments/${departmentId}/target`, {
      method: "PUT",
      body: JSON.stringify({ target_headcount: target })
    });
    toast("Hiring target saved.");
    await loadDepartments();
  } catch (error) {
    toast(`Could not save target: ${error.message}`);
  } finally {
    button.disabled = false;
    button.textContent = "Save";
  }
});

$("#departmentAssignmentForm")?.addEventListener("submit", async event => {
  event.preventDefault();
  if (auth.role !== "HR") {
    toast("Only HR can assign employees to departments.");
    return;
  }

  const employeeId = Number($("#departmentEmployeeSelect")?.value || 0);
  const departmentId = Number($("#departmentAssignmentSelect")?.value || 0);
  if (!employeeId || !departmentId) {
    toast("Select both an employee and a department.");
    return;
  }

  const employee = state.employees.find(item => Number(item.id) === employeeId);
  const department = state.departments.find(item => Number(item.id) === departmentId);
  const employeeName = getEmployeeName(employee || { id: employeeId });
  if (!window.confirm(`Assign ${employeeName} to ${department?.name || "the selected department"}?`)) {
    return;
  }

  const button = $("#assignDepartmentBtn");
  if (button) {
    button.disabled = true;
    button.textContent = "Assigning…";
  }

  try {
    await api(`/departments/assignments/${employeeId}`, {
      method: "PUT",
      body: JSON.stringify({ department_id: departmentId })
    });
    toast("Employee department updated.");
    await loadDepartments();
  } catch (error) {
    toast(`Assignment failed: ${error.message}`);
  } finally {
    if (button) {
      button.disabled = false;
      button.textContent = "Assign employee";
    }
  }
});

$("#employeeSearch")?.addEventListener("input", event => {
  renderContextEmployeeOptions(event.target.value);
});

$("#contextEmployeeId")?.addEventListener("change", async event => {
  if (auth.role !== "HR") return;

  const employeeId = Number(event.target.value || 0);
  state.contextEmployeeId = employeeId;

  if (employeeId > 0) {
    await loadEmployeeContext(employeeId);
  } else {
    clearEmployeeContextDisplay();
  }
});

$("#backToEnterprise")?.addEventListener("click", () => {
  // Clear the individual context selection, but keep the employee
  // selector available if the user returns to Employee Context later.
  state.contextEmployeeId = 0;

  if ($("#contextEmployeeId")) $("#contextEmployeeId").value = "";
  if ($("#employeeSearch")) $("#employeeSearch").value = "";

  renderContextEmployeeOptions("");
  clearEmployeeContextDisplay();
  switchView("overview");
});

/* -------------------- DASHBOARD -------------------- */

async function loadOverview() {
  if (!requireLogin()) return;

  if (auth.role === "EMPLOYEE") {
    await loadEmployeeOverview();
    return;
  }

  await loadHROverview();
}

async function loadHROverview() {
  try {
    const data = await api("/dashboard/overview");
    state.dashboardOverview = data;

    const employees = data.employees || {};
    const leave = data.leave || {};
    const attendance = data.attendance || {};
    const workflows = data.workflows || {};

    setText("#pulseLabel", "COMMAND CENTER");
    setText("#pulseTitle", "Enterprise pulse");
    setText("#metricsEyebrow", "SYSTEM OVERVIEW");
    setText("#metricsTitle", "Enterprise metrics");

    setMetric(
      "statLabel1", "statEmployees", "statEmployeesSub",
      "EMPLOYEES", employees.total ?? "—",
      `${employees.active ?? "—"} active`
    );

    setMetric(
      "statLabel2", "statPending", "statPendingSub",
      "PENDING LEAVE", leave.pending_requests ?? "—",
      "Awaiting HR review"
    );

    setMetric(
      "statLabel3", "statAttendance", "statAttendanceSub",
      "ATTENDANCE RECORDS", attendance.total_records ?? "—",
      "Recorded attendance entries"
    );

    setMetric(
      "statLabel4", "statCompleted", "statWorkflowSub",
      "COMPLETED WORKFLOWS", workflows.completed ?? "—",
      `${workflows.total ?? "—"} total workflows`
    );

    setText("#activityLabel", "RECENT ENGINE ACTIVITY");
    setText("#activityTitle", "Agent events");
    setDisplay("#activityViewBtn", true);

    state.overviewLoaded = true;

    await loadOperations();

    // Refresh charts only while the enterprise overview is active.
    if ($(".view.active")?.id === "overview") {
      renderDashboardCharts(
        state.dashboardOverview,
        state.workflowData,
        state.activityData
      );
    }
  } catch (error) {
    console.error("HR dashboard loading failed:", error);
    toast(`Dashboard error: ${error.message}`);
  }
}

async function loadEmployeeOverview() {
  const employeeId = auth.employeeId;

  if (!employeeId) {
    toast("Your account is not linked to an employee record.");
    return;
  }

  setText("#pulseLabel", "EMPLOYEE PORTAL");
  setText("#pulseTitle", "My HR snapshot");
  setText("#metricsEyebrow", "PERSONAL OVERVIEW");
  setText("#metricsTitle", "My information");

  setMetric(
    "statLabel1", "statEmployees", "statEmployeesSub",
    "MY PROFILE", "Loading…", "Your employee record"
  );

  setMetric(
    "statLabel2", "statPending", "statPendingSub",
    "LEAVE BALANCE", "Loading…", "Checking available leave"
  );

  setMetric(
    "statLabel3", "statAttendance", "statAttendanceSub",
    "ATTENDANCE", "—", "Attendance summary not verified"
  );

  setMetric(
    "statLabel4", "statCompleted", "statWorkflowSub",
    "EMPLOYEE ID", employeeId, "Your employee record"
  );

  setText("#activityLabel", "PERSONAL ACTIVITY");
  setText("#activityTitle", "My workspace");
  setDisplay("#activityViewBtn", false);
  setDisplay("#analyticsGrid", false);
  setDisplay(".analytics-heading", false);

  const [employeeResult, leaveResult] = await Promise.allSettled([
    api(`/employees/${employeeId}`),
    api(`/leaves/employee/${employeeId}`)
  ]);

  if (employeeResult.status === "fulfilled") {
    const response = employeeResult.value;
    const employee = response.employee || response;

    setText("#statEmployees", getEmployeeName(employee));
    setText(
      "#statEmployeesSub",
      employee.designation || employee.employee_code || "Employee profile"
    );
  } else {
    setText("#statEmployees", "Unavailable");
    setText("#statEmployeesSub", "Profile could not be loaded");
  }

  if (leaveResult.status === "fulfilled") {
    const balance = getLeaveBalance(leaveResult.value);

    if (hasLeaveBalance(balance)) {
      const casual = Number(balance.casual_leave || 0);
      const sick = Number(balance.sick_leave || 0);
      const earned = Number(balance.earned_leave || 0);

      setText("#statPending", casual + sick + earned);
      setText(
        "#statPendingSub",
        `Casual ${casual} · Sick ${sick} · Earned ${earned}`
      );
    } else {
      setText("#statPending", "—");
      setText("#statPendingSub", "Leave balance format unavailable");
    }
  } else {
    setText("#statPending", "Unavailable");
    setText("#statPendingSub", "Leave data could not be loaded");
  }

  showEmpty(
    "#recentActivity",
    "Personal activity is not yet available for this account."
  );

  state.overviewLoaded = true;

  if (
    employeeResult.status === "rejected" ||
    leaveResult.status === "rejected"
  ) {
    toast("Some employee information could not be loaded.");
  }
}

/* -------------------- EMPLOYEE CONTEXT VIEW -------------------- */

function clearEmployeeContextDisplay() {
  setText("#contextAvatar", "EC");
  setText("#contextEmployeeCode", "EMPLOYEE PROFILE");
  setText("#contextEmployeeName", "No employee selected");
  setText(
    "#contextEmployeeMeta",
    "Choose an employee above to view their information."
  );

  setText("#contextEmployeeIdValue", "—");
  setText("#contextLeaveBalance", "—");
  setText("#contextLeaveSub", "Available leave information");
  setText("#contextWorkflowCount", "—");
  setText("#contextActivityCount", "—");

  showEmpty(
    "#contextWorkflowList",
    "Select an employee to view their workflows."
  );

  showEmpty(
    "#contextActivityList",
    "Select an employee to view their agent activity."
  );

  $("#contextProfile")?.classList.add("empty");
}

async function loadEmployeeContext(employeeId) {
  if (auth.role !== "HR" || !employeeId) return;

  state.contextEmployeeId = employeeId;

  setText("#contextEmployeeName", "Loading employee...");
  setText("#contextEmployeeMeta", "Retrieving profile and activity.");
  setText("#contextEmployeeIdValue", employeeId);
  setText("#contextLeaveBalance", "Loading…");
  setText("#contextWorkflowCount", "Loading…");
  setText("#contextActivityCount", "Loading…");

  const [employeeResult, leaveResult] = await Promise.allSettled([
    api(`/employees/${employeeId}`),
    api(`/leaves/employee/${employeeId}`)
  ]);

  let employee = state.employees.find(
    item => Number(item.id) === employeeId
  ) || null;

  if (employeeResult.status === "fulfilled") {
    const response = employeeResult.value;
    employee = response.employee || response;
  }

  if (employee) {
    const name = getEmployeeName(employee);
    const initials = name
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map(part => part[0])
      .join("")
      .toUpperCase();

    setText("#contextAvatar", initials || "EC");
    setText("#contextEmployeeCode", employee.employee_code || `ID ${employeeId}`);
    setText("#contextEmployeeName", name);

    const metadata = [
      employee.designation,
      employee.department,
      employee.email,
      employee.status
    ].filter(Boolean);

    setText(
      "#contextEmployeeMeta",
      metadata.length ? metadata.join(" · ") : `Employee ID ${employeeId}`
    );

    $("#contextProfile")?.classList.remove("empty");
  } else {
    setText("#contextEmployeeName", "Profile unavailable");
    setText(
      "#contextEmployeeMeta",
      "The employee profile could not be retrieved."
    );
  }

  setText("#contextEmployeeIdValue", employeeId);

  if (leaveResult.status === "fulfilled") {
    const balance = getLeaveBalance(leaveResult.value);

    if (hasLeaveBalance(balance)) {
      setText("#contextLeaveBalance", getTotalLeave(balance));
      setText(
        "#contextLeaveSub",
        `Casual ${Number(balance.casual_leave || 0)} · Sick ${Number(balance.sick_leave || 0)} · Earned ${Number(balance.earned_leave || 0)}`
      );
    } else {
      setText("#contextLeaveBalance", "—");
      setText("#contextLeaveSub", "Leave balance details unavailable");
    }
  } else {
    setText("#contextLeaveBalance", "Unavailable");
    setText("#contextLeaveSub", "Could not load leave information");
  }

  // Fetch the latest workflow and agent records before filtering.
  await loadOperations();

  // Stop if the selection changed while requests were in progress.
  if (state.contextEmployeeId !== employeeId) return;

  const workflows = normalizeArray(state.workflowData, [
    "workflows", "items", "executions"
  ]).filter(item => Number(item.employee_id) === employeeId);

  const workflowIds = new Set(
    workflows.map(item => String(item.workflow_id ?? item.id))
  );

  const activities = normalizeArray(state.activityData, [
    "activities", "activity", "logs", "items"
  ]).filter(item => workflowIds.has(String(item.workflow_id)));

  setText("#contextWorkflowCount", workflows.length);
  setText("#contextActivityCount", activities.length);

  renderContextWorkflows(workflows);
  renderContextActivities(activities);

  if (employeeResult.status === "rejected") {
    toast("Could not load the selected employee's profile.");
  }
}

function renderContextWorkflows(workflows) {
  const container = $("#contextWorkflowList");
  if (!container) return;

  if (!workflows.length) {
    showEmpty("#contextWorkflowList", "No workflow records found for this employee.");
    return;
  }

  container.innerHTML = workflows.slice(0, 10).map(item => `
    <div class="data-row">
      <span class="id">#${escapeHtml(item.workflow_id ?? item.id ?? "—")}</span>
      <div>
        <strong>${escapeHtml(item.workflow_type || "Workflow")}</strong>
        <small>${escapeHtml(formatTime(item.started_at))}</small>
      </div>
      <span class="tag">${escapeHtml(item.status || "UNKNOWN")}</span>
    </div>
  `).join("");
}

function renderContextActivities(activities) {
  const container = $("#contextActivityList");
  if (!container) return;

  if (!activities.length) {
    showEmpty("#contextActivityList", "No agent activity found for this employee.");
    return;
  }

  container.innerHTML = activities.slice(0, 10).map(item => `
    <div class="data-row">
      <span class="id">#${escapeHtml(item.workflow_id ?? "—")}</span>
      <div>
        <strong>${escapeHtml(item.agent_name || "Agent")}</strong>
        <small>
          ${escapeHtml(item.action || "Activity")}
          · ${escapeHtml(formatTime(item.timestamp))}
        </small>
      </div>
      <span class="tag">${escapeHtml(item.status || "RECORDED")}</span>
    </div>
  `).join("");
}

/* -------------------- ACTIVITY FEED -------------------- */

function renderRecentActivity(data) {
  const container = $("#recentActivity");
  if (!container) return;

  const rows = normalizeArray(data, [
    "activities", "activity", "logs", "items"
  ]).slice(0, 6);

  if (!rows.length) {
    showEmpty("#recentActivity", "No recent agent activity returned.");
    return;
  }

  container.innerHTML = rows.map(item => `
    <div class="activity-row">
      <span class="activity-time">${escapeHtml(formatTime(item.timestamp))}</span>
      <div>
        <strong class="activity-main">
          ${escapeHtml(item.action || "Agent activity")}
        </strong>
        <div class="activity-agent">
          ${escapeHtml(item.agent_name || "Agent")}
        </div>
      </div>
      <span class="activity-status">
        ${escapeHtml(item.status || "RECORDED")}
      </span>
    </div>
  `).join("");
}

/* -------------------- WORKFLOW REQUESTS -------------------- */

async function runWorkflow(request) {
  if (!requireLogin()) return;

  // Employee users always use their own employee record.
  // HR requests use the selection in the Employee Context page.
  const employeeId = auth.role === "EMPLOYEE"
    ? auth.employeeId
    : Number($("#contextEmployeeId")?.value || state.contextEmployeeId || 0);

  if (!Number.isInteger(employeeId) || employeeId <= 0) {
    toast("HR: open Employee Context and select an employee before submitting a request.");
    return;
  }

  const sendButton = $("#sendBtn");
  if (sendButton) sendButton.disabled = true;

  setText("#radarStatus", "ROUTING");
  setText("#traceBadge", "EXECUTING");
  setText("#requestId", "EXECUTING / COORDINATING");

  addMessage("user", request);
  addMessage("assistant", "Routing request through the coordination engine…");

  try {
    const result = await api("/workflow", {
      method: "POST",
      body: JSON.stringify({ employee_id: employeeId, request })
    });

    state.lastWorkflow = result;

    if (result.error || result.success === false) {
      throw new Error(result.error || result.message || "Workflow failed.");
    }

    setText("#requestId", `WORKFLOW ${result.workflow_id ?? "PROCESSED"}`);
    setText("#traceBadge", "COMPLETED");
    setText("#radarStatus", "ACTIVE");

    renderTrace(result);
    replaceLastAssistant(result);

    // Refresh individual records if HR is viewing that employee.
    if (
      auth.role === "HR" &&
      state.contextEmployeeId === employeeId &&
      $(".view.active")?.id === "employee-context"
    ) {
      await loadEmployeeContext(employeeId);
    }
  } catch (error) {
    setText("#radarStatus", "ERROR");
    setText("#traceBadge", "FAILED");
    setText("#requestId", "REQUEST FAILED");

    const failedResult = {
      success: false,
      message: error.message,
      plan: [{
        step: 1,
        agent: "Request Validation",
        task: "Request could not be completed",
        status: "failed",
        finding: error.message
      }],
      decision: {
        decision: "REQUEST_BLOCKED",
        status: "failed",
        recommendation: error.message,
        evidence_count: 0,
        evidence: [],
        human_review_required: true
      }
    };

    state.lastWorkflow = failedResult;
    renderTrace(failedResult);
    replaceLastAssistant({ error: error.message });
    toast(error.message);
  } finally {
    if (sendButton) sendButton.disabled = false;

    setTimeout(() => setText("#radarStatus", "IDLE"), 1200);
    setTimeout(() => setText("#traceBadge", "WAITING"), 2500);
  }
}

function addMessage(type, text) {
  const container = $("#messages");
  if (!container) return;

  const intro = container.querySelector(".chat-intro");
  if (intro) intro.remove();

  const wrapper = document.createElement("div");
  wrapper.className = `message ${type}`;

  wrapper.innerHTML = `
    <div class="bubble">
      <span class="bubble-label">${type === "user" ? "YOU" : "ENGINE"}</span>
      <div>${escapeHtml(text)}</div>
    </div>
  `;

  container.appendChild(wrapper);

  if (container.parentElement) {
    container.parentElement.scrollTop = container.parentElement.scrollHeight;
  }
}

function replaceLastAssistant(result) {
  const messages = $$("#messages .message.assistant");
  const last = messages[messages.length - 1];
  if (!last) return;

  const bubble = last.querySelector(".bubble");
  if (!bubble) return;

  if (result.error) {
    bubble.innerHTML = `
      <span class="bubble-label">ENGINE</span>
      <div>Unable to complete the request.</div>
      <div class="result-card">
        <strong>ERROR</strong>
        <pre>${escapeHtml(result.error)}</pre>
      </div>
    `;
    return;
  }

  const decision = result.decision || {};
  const summary =
    decision.recommendation ||
    result.message ||
    "The request was processed by the coordination engine.";

  bubble.innerHTML = `
    <span class="bubble-label">
      ENGINE · ${escapeHtml(decision.decision || "PROCESSED")}
    </span>
    <div>${escapeHtml(summary)}</div>
    <div class="result-card">
      <strong>Evidence: ${escapeHtml(decision.evidence_count ?? 0)}</strong>
      <pre>${escapeHtml(summarizeResults(result.results || []))}</pre>
    </div>
  `;
}

function summarizeResults(results) {
  if (!Array.isArray(results) || !results.length) {
    return "No agent result details were returned.";
  }

  return results.map(item => {
    const agent = item.agent || "Agent";

    // Support both direct results and nested workflow results.
    const result = item.result || item;

    if (result.employee) {
      const employee = result.employee;
      const name = [employee.first_name, employee.last_name]
        .filter(Boolean)
        .join(" ");
      return `${agent}: Employee profile${name ? " — " + name : " retrieved"}`;
    }

    if (result.leave_balance) {
      const balance = result.leave_balance;
      return `${agent}: Leave balance — casual ${balance.casual_leave ?? "—"}, sick ${balance.sick_leave ?? "—"}, earned ${balance.earned_leave ?? "—"}`;
    }

    if (Array.isArray(result.policies)) {
      if (!result.policies.length) {
        return `${agent}: ${result.message || "No matching policies found."}`;
      }

      return `${agent}: ${result.policies.map(policy =>
        `${policy.policy_name || "HR Policy"}: ${policy.description || "No description available."}`
      ).join("\n\n")}`;
    }

    if (result.leave_history) {
      return `${agent}: Retrieved ${result.leave_history.length} leave history record(s).`;
    }

    if (result.summary) {
      return `${agent}: Attendance summary — ${result.summary.attendance_percentage ?? "unavailable"}%`;
    }

    if (result.attendance_percentage !== undefined) {
      return `${agent}: Attendance ${result.attendance_percentage}%`;
    }

    if (result.message) {
      return `${agent}: ${result.message}`;
    }

    return `${agent}: No displayable details were returned.`;
  }).join("\n\n");
}

function renderTrace(result) {
  const plan = Array.isArray(result.plan) ? result.plan : [];
  const employeeId = auth.role === "EMPLOYEE"
    ? auth.employeeId
    : Number($("#contextEmployeeId")?.value || 0);

  const items = [
    {
      title: "Request received",
      text: `Employee ${employeeId} submitted a request.`,
      tag: "INPUT"
    },
    ...plan.map((item, index) => ({
      title: item.agent || `Agent ${index + 1}`,
      text: item.task || "Specialized agent execution.",
      tag: `AGENT ${String(index + 1).padStart(2, "0")}`
    })),
    {
      title: "Decision Intelligence",
      text: result.decision?.recommendation ||
        "Decision details returned by the workflow.",
      tag: result.decision?.decision || "DECISION"
    }
  ];

  const container = $("#trace");
  if (!container) return;

  container.innerHTML = items.map((item, index) => `
    <div class="trace-item">
      <div class="trace-dot">${index + 1}</div>
      <h4>${escapeHtml(item.title)}</h4>
      <p>${escapeHtml(item.text)}</p>
      <small>${escapeHtml(item.tag)}</small>
    </div>
  `).join("");
}

/* -------------------- HR OPERATIONS -------------------- */

async function loadOperations() {
  if (auth.role !== "HR" || !auth.token) return;

  const [workflowResult, activityResult] = await Promise.allSettled([
    api("/workflows/"),
    api("/agents/activity")
  ]);

  state.workflowData = workflowResult.status === "fulfilled"
    ? workflowResult.value
    : null;

  state.activityData = activityResult.status === "fulfilled"
    ? activityResult.value
    : null;

  if (workflowResult.status === "fulfilled") {
    renderWorkflows(workflowResult.value);
  } else {
    showEmpty(
      "#workflowTable",
      `Workflow history unavailable: ${workflowResult.reason.message}`
    );
  }

  if (activityResult.status === "fulfilled") {
    renderActivityTable(activityResult.value);

    // Only update the enterprise activity feed when the enterprise
    // overview is the active page.
    if ($(".view.active")?.id === "overview") {
      renderRecentActivity(activityResult.value);
    }
  } else {
    showEmpty(
      "#activityTable",
      `Agent activity unavailable: ${activityResult.reason.message}`
    );

    if ($(".view.active")?.id === "overview") {
      showEmpty("#recentActivity", "Agent activity could not be loaded.");
    }
  }

  if (
    state.dashboardOverview &&
    $(".view.active")?.id === "overview"
  ) {
    renderDashboardCharts(
      state.dashboardOverview,
      state.workflowData,
      state.activityData
    );
  }
}

function renderWorkflows(data) {
  const container = $("#workflowTable");
  if (!container) return;

  const rows = normalizeArray(data, [
    "workflows", "items", "executions"
  ]).slice(0, 10);

  if (!rows.length) {
    showEmpty("#workflowTable", "No workflow executions returned.");
    return;
  }

  container.innerHTML = rows.map(item => `
    <div class="data-row">
      <span class="id">#${escapeHtml(item.workflow_id ?? item.id ?? "—")}</span>
      <div>
        <strong>${escapeHtml(item.workflow_type || "Workflow")}</strong>
        <small>
          Employee ${escapeHtml(item.employee_id ?? "—")}
          · ${escapeHtml(formatTime(item.started_at))}
        </small>
      </div>
      <span class="tag">${escapeHtml(item.status || "UNKNOWN")}</span>
    </div>
  `).join("");
}

function renderActivityTable(data) {
  const container = $("#activityTable");
  if (!container) return;

  const rows = normalizeArray(data, [
    "activities", "activity", "logs", "items"
  ]).slice(0, 10);

  if (!rows.length) {
    showEmpty("#activityTable", "No agent events returned.");
    return;
  }

  container.innerHTML = rows.map(item => `
    <div class="data-row">
      <span class="id">${escapeHtml(item.workflow_id ?? item.id ?? "—")}</span>
      <div>
        <strong>${escapeHtml(item.agent_name || "Agent")}</strong>
        <small>
          ${escapeHtml(item.action || "Activity")}
          · ${escapeHtml(formatTime(item.timestamp))}
        </small>
      </div>
      <span class="tag">${escapeHtml(item.status || "RECORDED")}</span>
    </div>
  `).join("");
}

/* -------------------- FORM EVENTS -------------------- */

$("#requestForm")?.addEventListener("submit", event => {
  event.preventDefault();

  const question = $("#question")?.value.trim();
  if (!question) return;

  $("#question").value = "";
  runWorkflow(question);
});

$("#question")?.addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    $("#requestForm")?.requestSubmit();
  }
});

$$("[data-question]").forEach(button => {
  button.addEventListener("click", () => {
    if ($("#question")) {
      $("#question").value = button.dataset.question;
    }

    switchView("assistant");
    $("#question")?.focus();
  });
});

$("#refreshOverview")?.addEventListener("click", loadOverview);
$("#refreshOps")?.addEventListener("click", loadOperations);

$$(".agent-node").forEach(node => {
  node.addEventListener("click", () => {
    if ($("#question")) {
      $("#question").value =
        `Show information handled by the ${node.dataset.agent}`;
    }

    switchView("assistant");
    $("#question")?.focus();
  });
});

/* -------------------- LOGIN FORM -------------------- */

$("#loginForm")?.addEventListener("submit", async event => {
  event.preventDefault();

  const username = $("#loginUsername").value.trim();
  const password = $("#loginPassword").value;
  const errorElement = $("#loginError");
  const button = $("#loginBtn");

  errorElement.textContent = "";

  if (!username || !password) {
    errorElement.textContent = "Username and password are required.";
    return;
  }

  button.disabled = true;

  const buttonText = button.querySelector("span");
  if (buttonText) buttonText.textContent = "AUTHENTICATING";

  try {
    await login(username, password);
    updateSessionUI();

    if (auth.role === "HR") {
      await loadEmployeeOptions();
    }

    // Both HR and employee accounts initially open the overview.
    switchView("overview");

    toast(`Authenticated as ${auth.role}`);
  } catch (error) {
    errorElement.textContent = error.message;
  } finally {
    button.disabled = false;
    if (buttonText) buttonText.textContent = "AUTHENTICATE";
  }
});

/* -------------------- DASHBOARD CHARTS -------------------- */

const chartColors = {
  cyan: "#48e0e8",
  violet: "#a78bfa",
  green: "#4ade80",
  amber: "#fbbf24",
  red: "#fb7185",
  muted: "#64748b",
  track: "rgba(148, 163, 184, 0.13)",
  text: "#a8b4c8"
};

function drawDonutChart(canvasId, legendId, entries, centerLabel) {
  const canvas = document.getElementById(canvasId);
  const legend = document.getElementById(legendId);
  if (!canvas || !legend) return;

  const validEntries = entries.map(item => ({
    label: String(item.label),
    value: Math.max(0, Number(item.value) || 0),
    color: item.color
  }));

  legend.innerHTML = validEntries.map(item => `
    <span class="chart-legend-item">
      <span class="chart-legend-dot" style="background:${item.color}"></span>
      ${escapeHtml(item.label)}: ${item.value}
    </span>
  `).join("");

  const rect = canvas.getBoundingClientRect();
  const width = Math.max(rect.width, 240);
  const height = Math.max(rect.height, 180);
  const dpr = window.devicePixelRatio || 1;

  canvas.width = Math.round(width * dpr);
  canvas.height = Math.round(height * dpr);

  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, width, height);

  const total = validEntries.reduce((sum, item) => sum + item.value, 0);
  const cx = width / 2;
  const cy = height / 2;
  const radius = Math.min(width * 0.25, height * 0.34, 82);
  const thickness = Math.max(16, radius * 0.25);

  ctx.lineWidth = thickness;
  ctx.lineCap = "butt";
  ctx.strokeStyle = chartColors.track;
  ctx.beginPath();
  ctx.arc(cx, cy, radius, 0, Math.PI * 2);
  ctx.stroke();

  if (total > 0) {
    let angle = -Math.PI / 2;

    validEntries.forEach(item => {
      if (item.value <= 0) return;

      const nextAngle = angle + (item.value / total) * Math.PI * 2;
      ctx.strokeStyle = item.color;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, angle, nextAngle);
      ctx.stroke();
      angle = nextAngle;
    });
  }

  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillStyle = "#f1f5f9";
  ctx.font = "600 27px system-ui, sans-serif";
  ctx.fillText(String(total), cx, cy - 7);

  ctx.fillStyle = chartColors.text;
  ctx.font = "11px system-ui, sans-serif";
  ctx.fillText(centerLabel, cx, cy + 17);

  if (total === 0) {
    ctx.fillStyle = chartColors.text;
    ctx.font = "12px system-ui, sans-serif";
    ctx.fillText("No records yet", cx, cy + radius + 28);
  }
}

function renderDashboardCharts(overview, workflowsData, activitiesData) {
  if (
    auth.role !== "HR" ||
    $(".view.active")?.id !== "overview"
  ) return;

  const employees = overview?.employees || {};
  const leave = overview?.leave || {};
  const workflowMetrics = overview?.workflows || {};

  const employeeTotal = Number(employees.total) || 0;
  const activeEmployees = Math.min(
    employeeTotal,
    Math.max(0, Number(employees.active) || 0)
  );

  drawDonutChart(
    "employeeChart",
    "employeeChartLegend",
    [
      { label: "Active", value: activeEmployees, color: chartColors.cyan },
      {
        label: "Inactive",
        value: Math.max(0, employeeTotal - activeEmployees),
        color: chartColors.muted
      }
    ],
    "Employees"
  );

  const totalLeave = Number(leave.total_requests) || 0;
  const pendingLeave = Math.min(
    totalLeave,
    Math.max(0, Number(leave.pending_requests) || 0)
  );

  drawDonutChart(
    "leaveChart",
    "leaveChartLegend",
    [
      { label: "Pending", value: pendingLeave, color: chartColors.amber },
      {
        label: "Other requests",
        value: Math.max(0, totalLeave - pendingLeave),
        color: chartColors.violet
      }
    ],
    "Requests"
  );

  const workflowTotal = Number(workflowMetrics.total) || 0;
  const workflowCompleted = Number(workflowMetrics.completed) || 0;
  const workflowFailed = Number(workflowMetrics.failed) || 0;

  drawDonutChart(
    "workflowChart",
    "workflowChartLegend",
    [
      { label: "Completed", value: workflowCompleted, color: chartColors.green },
      { label: "Failed", value: workflowFailed, color: chartColors.red },
      {
        label: "Other",
        value: Math.max(0, workflowTotal - workflowCompleted - workflowFailed),
        color: chartColors.violet
      }
    ],
    "Workflows"
  );

  const activityRows = normalizeArray(activitiesData, [
    "activities", "activity", "logs", "items"
  ]);

  const activityCounts = {};
  activityRows.forEach(item => {
    const status = String(item.status || "RECORDED").toUpperCase();
    activityCounts[status] = (activityCounts[status] || 0) + 1;
  });

  const agentEntries = Object.entries(activityCounts).map(([label, value]) => ({
    label,
    value,
    color: /COMPLETED|SUCCESS/.test(label)
      ? chartColors.green
      : /FAILED|ERROR/.test(label)
        ? chartColors.red
        : chartColors.cyan
  }));

  drawDonutChart(
    "agentChart",
    "agentChartLegend",
    agentEntries,
    "Agent events"
  );
}

/* -------------------- INITIALIZATION -------------------- */

async function initializeApp() {
  const validSession = Boolean(
    auth.token && ["HR", "EMPLOYEE"].includes(auth.role)
  );

  if (!validSession) {
    clearSession();
    updateSessionUI();
    return;
  }

  if (auth.role === "EMPLOYEE" && auth.employeeId <= 0) {
    clearSession();
    updateSessionUI();
    toast("Please sign in again with your employee account.");
    return;
  }

  state.employeeId = auth.role === "EMPLOYEE"
    ? auth.employeeId
    : 0;

  state.contextEmployeeId = 0;

  updateSessionUI();

  if (auth.role === "HR") {
    await loadEmployeeOptions();
  }

  switchView("overview");
}

initializeApp();
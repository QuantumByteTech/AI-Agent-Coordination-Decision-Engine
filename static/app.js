const form = document.getElementById("chatForm");
const input = document.getElementById("question");
const chat = document.getElementById("chat");
const sendBtn = document.getElementById("sendBtn");
const state = document.getElementById("requestState");

function addMessage(text, type, label) {
  const row = document.createElement("div");
  row.className = `message ${type}`;
  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.textContent = type === "user" ? "E" : "✦";
  const content = document.createElement("div");
  const strong = document.createElement("strong");
  strong.textContent = label;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  content.appendChild(strong);
  content.appendChild(bubble);
  row.appendChild(avatar);
  row.appendChild(content);
  chat.appendChild(row);
  chat.scrollTop = chat.scrollHeight;
}

async function sendQuestion(question) {
  question = question.trim();
  if (!question || sendBtn.disabled) return;

  addMessage(question, "user", "You");
  input.value = "";
  input.style.height = "auto";
  sendBtn.disabled = true;
  state.textContent = "Processing";
  state.classList.add("busy");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({question})
    });

    const data = await response.json();
    if (data.success) {
      addMessage(data.message, "assistant", "WorkSphere Assistant");
      state.textContent = data.agent || "Ready";
    } else {
      addMessage(data.message, "assistant", "WorkSphere Assistant");
      state.textContent = "Ready";
    }
  } catch (err) {
    addMessage("The HR service is temporarily unavailable. Please try again in a moment.", "assistant", "WorkSphere Assistant");
    state.textContent = "Unavailable";
  } finally {
    sendBtn.disabled = false;
    state.classList.remove("busy");
  }
}

form.addEventListener("submit", e => {
  e.preventDefault();
  sendQuestion(input.value);
});

input.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 120) + "px";
});

document.querySelectorAll(".quick-card").forEach(btn => {
  btn.addEventListener("click", () => sendQuestion(btn.dataset.question));
});

document.querySelectorAll(".nav-item").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach(x => x.classList.remove("active"));
    btn.classList.add("active");
    document.querySelectorAll(".view").forEach(v => v.classList.remove("active-view"));
    document.getElementById(btn.dataset.view).classList.add("active-view");
  });
});

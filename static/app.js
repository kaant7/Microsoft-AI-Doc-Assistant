const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const messages = document.getElementById("messages");

function addMessage(text, role) {
  const el = document.createElement("div");
  el.className = `msg ${role}`;
  el.textContent = text;
  messages.appendChild(el);
  messages.scrollTop = messages.scrollHeight;
  return el;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = input.value.trim();
  if (!question) return;

  addMessage(question, "user");
  input.value = "";
  input.disabled = true;
  form.querySelector("button").disabled = true;

  const pending = addMessage("Thinking...", "assistant pending");

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: question }),
    });
    const data = await res.json();

    if (!res.ok) {
      pending.textContent = data.error || "Something went wrong.";
      pending.className = "msg error";
    } else {
      pending.textContent = data.answer;
      pending.className = "msg assistant";
    }
  } catch (err) {
    pending.textContent = "Could not reach the server.";
    pending.className = "msg error";
  } finally {
    input.disabled = false;
    form.querySelector("button").disabled = false;
    input.focus();
  }
});

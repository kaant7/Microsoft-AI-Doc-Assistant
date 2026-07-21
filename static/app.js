const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const messages = document.getElementById("messages");
const newChatBtn = document.getElementById("new-chat");

const MIC_ICON = `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3Z" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
  <path d="M19 11a7 7 0 0 1-14 0M12 18v3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
</svg>`;

function timeNow() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// Minimal markdown-ish renderer: bold, inline code, code blocks, bullet lists, links-as-citations.
function renderRichText(raw) {
  const escaped = escapeHtml(raw);
  const lines = escaped.split("\n");
  let html = "";
  let inList = false;
  let inCode = false;

  for (const line of lines) {
    if (line.trim().startsWith("```")) {
      html += inCode ? "</code></pre>" : "<pre><code>";
      inCode = !inCode;
      continue;
    }
    if (inCode) {
      html += line + "\n";
      continue;
    }

    const bulletMatch = line.match(/^\s*[-*]\s+(.*)/);
    if (bulletMatch) {
      if (!inList) {
        html += "<ul>";
        inList = true;
      }
      html += `<li>${inlineFormat(bulletMatch[1])}</li>`;
      continue;
    }
    if (inList) {
      html += "</ul>";
      inList = false;
    }

    if (line.trim() === "") continue;
    html += `<p>${inlineFormat(line)}</p>`;
  }
  if (inList) html += "</ul>";
  if (inCode) html += "</code></pre>";
  return html;
}

function inlineFormat(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<span class="citation">$1</span>')
    .replace(/\[Source:\s*([^\]]+)\]/gi, (_, path) => {
      const name = path.trim().split("/").pop();
      return `<span class="citation">${name}</span>`;
    });
}

function addRow(text, role, { html = false, pending = false } = {}) {
  const row = document.createElement("div");
  row.className = `row ${role}`;

  const avatar = document.createElement("div");
  avatar.className = `avatar avatar-${role}`;
  avatar.innerHTML = role === "assistant" ? MIC_ICON : "You";

  const content = document.createElement("div");
  content.className = "row-content";

  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}${pending ? " pending" : ""}`;
  if (html) {
    bubble.innerHTML = text;
  } else {
    bubble.textContent = text;
  }

  const stamp = document.createElement("div");
  stamp.className = "timestamp";
  stamp.textContent = timeNow();

  content.appendChild(bubble);
  content.appendChild(stamp);
  row.appendChild(avatar);
  row.appendChild(content);
  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;
  return bubble;
}

function showWelcome() {
  messages.innerHTML = "";
  addRow(
    "Hello! I'm ready to answer questions about Microsoft Foundry Local, based on the official documentation.",
    "assistant"
  );
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = input.value.trim();
  if (!question) return;

  addRow(question, "user");
  input.value = "";
  input.disabled = true;
  form.querySelector("button").disabled = true;

  const pendingBubble = addRow("Thinking...", "assistant", { pending: true });

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: question }),
    });
    const data = await res.json();

    pendingBubble.classList.remove("pending");
    if (!res.ok) {
      pendingBubble.classList.add("error");
      pendingBubble.textContent = data.error || "Something went wrong.";
    } else {
      pendingBubble.innerHTML = renderRichText(data.answer);
    }
  } catch (err) {
    pendingBubble.classList.remove("pending");
    pendingBubble.classList.add("error");
    pendingBubble.textContent = "Could not reach the server.";
  } finally {
    input.disabled = false;
    form.querySelector("button").disabled = false;
    input.focus();
  }
});

newChatBtn.addEventListener("click", showWelcome);

showWelcome();

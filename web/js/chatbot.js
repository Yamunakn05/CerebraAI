// ============================================================
// chatbot.js — AI Assistant Chat Interface
// ============================================================

function renderChatbotPage(container) {
  const role = App.user?.role?.toLowerCase() || 'patient';
  if (['receptionist', 'admin'].includes(role)) {
    container.innerHTML = `
      <div class="page-header"><h1>🤖 AI Assistant</h1></div>
      <div class="glass-card" style="text-align:center;padding:40px">
        <div style="font-size:3.5rem;margin-bottom:12px">🚫</div>
        <h2 style="color:var(--red);margin-bottom:8px">Access Restricted</h2>
        <p style="color:var(--text-dim)"><strong style="color:var(--text-primary)">${role.charAt(0).toUpperCase() + role.slice(1)}</strong> role cannot access CerebraBot.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="page-header">
      <h1>🤖 AI Assistant</h1>
      <p>Ask questions about brain tumors, MRI results, medications, or general medical topics.</p>
    </div>

    <div class="alert alert-info">
      ⚠️ CerebraBot is an educational assistant and should complement, not replace, professional medical judgment.
    </div>

    <!-- Quick starters -->
    <div class="quick-grid" id="quick-starters">
      <button class="quick-btn" onclick="sendQuickPrompt('Explain my MRI results in simple terms')">💡 Explain my MRI results</button>
      <button class="quick-btn" onclick="sendQuickPrompt('What is tumor severity score and how is it calculated?')">💡 What is severity score?</button>
      <button class="quick-btn" onclick="sendQuickPrompt('What are common side effects of brain tumor treatment?')">💡 Common treatment side effects</button>
      <button class="quick-btn" onclick="sendQuickPrompt('How should I prepare for a neurology consultation?')">💡 Prepare for consultation</button>
    </div>

    <!-- Chat container -->
    <div class="glass-card chat-container">
      <div class="chat-messages" id="chat-messages"></div>
      <div class="chat-input-area">
        <textarea class="chat-input" id="chat-input-text" placeholder="Ask about brain tumors, MRI findings, reports, medications..." rows="1"></textarea>
        <button class="btn btn-primary chat-send" id="chat-send-btn" onclick="sendChatMessage()">
          🚀 Send
        </button>
      </div>
    </div>
  `;

  // Render initial message or history
  if (!App.chatHistory.length) {
    const userName = App.user?.full_name || App.user?.username || 'Patient';
    App.chatHistory.push({
      role: 'bot',
      text: `👋 Hello **${userName}**! I'm CerebraBot, your medical AI assistant. Ask me anything about MRI findings, brain tumors, treatment options, or general medical questions.`,
    });
  }

  renderChatHistory();

  // Auto-expand input & enter key
  const inputEl = document.getElementById('chat-input-text');
  if (inputEl) {
    inputEl.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChatMessage();
      }
    });
  }
}

function renderChatHistory() {
  const container = document.getElementById('chat-messages');
  if (!container) return;

  container.innerHTML = App.chatHistory.map((m, idx) => `
    <div class="chat-bubble ${m.role} animate-in">
      ${m.role === 'bot' ? renderMarkdown(m.text) : escapeHtml(m.text)}
      ${m.role === 'bot' ? `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;padding-top:6px;border-top:1px solid var(--border)">
          <span style="font-size:.68rem;color:var(--text-dim)">🤖 <em>Powered by Groq AI (llama-3.1-8b)</em></span>
          <div style="display:flex;gap:6px">
            <button class="btn btn-sm btn-secondary" onclick="copyChatMsg(${idx})">📋 Copy</button>
            <button class="btn btn-sm btn-secondary" onclick="likeChatMsg(${idx})">👍</button>
          </div>
        </div>
      ` : ''}
    </div>
  `).join('');

  container.scrollTop = container.scrollHeight;
}

async function sendChatMessage() {
  const inputEl = document.getElementById('chat-input-text');
  const msg = inputEl.value.trim();
  if (!msg) return;

  inputEl.value = '';
  App.chatHistory.push({ role: 'user', text: msg });
  renderChatHistory();

  // Show typing indicator
  const container = document.getElementById('chat-messages');
  const typingEl = document.createElement('div');
  typingEl.className = 'chat-bubble bot animate-in';
  typingEl.id = 'typing-indicator';
  typingEl.innerHTML = `<span class="typing-dots"><span></span><span></span><span></span></span> NeuroBot is thinking...`;
  container.appendChild(typingEl);
  container.scrollTop = container.scrollHeight;

  const btn = document.getElementById('chat-send-btn');
  if (btn) btn.disabled = true;

  const res = await api('/api/chat', { method: 'POST', body: { message: msg } });

  if (btn) btn.disabled = false;
  const tEl = document.getElementById('typing-indicator');
  if (tEl) tEl.remove();

  if (res.error) {
    App.chatHistory.push({ role: 'bot', text: `⚠️ ${res.error}` });
  } else {
    App.chatHistory.push({ role: 'bot', text: res.reply });
  }

  renderChatHistory();
}

function sendQuickPrompt(promptText) {
  const inputEl = document.getElementById('chat-input-text');
  if (inputEl) {
    inputEl.value = promptText;
    sendChatMessage();
  }
}

function copyChatMsg(idx) {
  const item = App.chatHistory[idx];
  if (item && item.text) {
    navigator.clipboard.writeText(item.text);
    toast('📋 Copied to clipboard!', 'success');
  }
}

function likeChatMsg() {
  toast('👍 Thanks for your feedback!', 'success');
}

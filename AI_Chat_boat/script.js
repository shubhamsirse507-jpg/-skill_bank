/* ========================================
   AI CHAT BOAT — JavaScript Engine
   ======================================== */

'use strict';

// ─── State ─────────────────────────────────────────
const state = {
  messages: [],
  chatSessions: [{ id: 'default', title: 'Getting Started', time: 'Just now' }],
  activeChatId: 'default',
  isLoading: false,
  messageCounter: 0,
  typingTimeout: null,
};

// ─── AI Responses (Smart Simulated) ────────────────
const AI_RESPONSES = {
  greetings: [
    "Hello! 👋 I'm **AI Chat Boat**, your intelligent assistant. How can I help you today? Whether you need help with code, creative writing, analysis, or just want to chat — I'm here!",
    "Hi there! Great to see you! I'm ready to assist with anything you have in mind. What's on your agenda today?",
    "Hey! 🌟 Welcome! I'm AI Chat Boat — powered by advanced language models. Ask me anything!",
  ],
  coding: [
    `Here's a clean Python implementation for you:\n\n\`\`\`python\ndef bubble_sort(arr):\n    n = len(arr)\n    for i in range(n - 1):\n        for j in range(n - i - 1):\n            if arr[j] > arr[j + 1]:\n                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n    return arr\n\n# Example usage\nmy_list = [64, 34, 25, 12, 22, 11, 90]\nprint("Sorted:", bubble_sort(my_list))\n# Output: Sorted: [11, 12, 22, 25, 34, 64, 90]\n\`\`\`\n\n**How it works:**\n- Compares adjacent elements and swaps if needed\n- After each pass, the largest unsorted element "bubbles up"\n- Time complexity: **O(n²)** — best for small datasets`,
    `Great coding question! Here's a JavaScript solution:\n\n\`\`\`javascript\nconst fetchUserData = async (userId) => {\n  try {\n    const response = await fetch(\`/api/users/\${userId}\`);\n    if (!response.ok) throw new Error(\`HTTP \${response.status}\`);\n    const data = await response.json();\n    return { success: true, data };\n  } catch (error) {\n    console.error('Fetch error:', error);\n    return { success: false, error: error.message };\n  }\n};\n\`\`\`\n\nThis pattern handles errors gracefully and returns a consistent response shape. 🚀`,
  ],
  quantum: [
    "Great question! **Quantum Computing** in simple terms:\n\n🔵 **Classical computers** use bits (0 or 1) — like light switches.\n\n🟣 **Quantum computers** use **qubits** which can be 0, 1, or *both at the same time* (called **superposition**)!\n\nImagine trying every key in a lock simultaneously instead of one by one. That's essentially quantum computing's power.\n\n**Key concepts:**\n- **Superposition** — being in multiple states at once\n- **Entanglement** — qubits linked across distances\n- **Interference** — amplifying correct answers\n\n💡 This makes quantum computers incredibly fast for specific tasks like cryptography, drug discovery, and optimization problems!",
  ],
  ideas: [
    "Here are **5 innovative mobile app ideas** for 2025 🚀\n\n1. **🧠 MindMap AI** — A mental health app that uses AI to detect mood patterns from journal entries and suggest personalized coping strategies.\n\n2. **🌿 GreenTrack** — Carbon footprint tracker that gamifies eco-friendly decisions with community challenges.\n\n3. **👁️ SightAssist** — Real-time AR app for visually impaired users that narrates surroundings using computer vision.\n\n4. **🎓 SkillSwap** — Peer-to-peer skill exchange platform: teach what you know, learn what you want.\n\n5. **🍽️ FridgeChef** — Scan your fridge, get personalized recipes with step-by-step video guidance powered by AI.\n\nWant me to deep-dive into any of these? 💡",
  ],
  webdesign: [
    "Here are the top **Web Design Best Practices for 2025** 🎨\n\n**Visual Design**\n- Dark mode as default with smooth light/dark transitions\n- Glassmorphism & neumorphism for depth\n- Micro-animations for engagement (60fps)\n\n**Typography**\n- Variable fonts for performance & flexibility\n- Fluid typography with `clamp()` — scales with viewport\n- High contrast ratios (WCAG AAA)\n\n**Performance**\n- Core Web Vitals: LCP < 2.5s, FID < 100ms, CLS < 0.1\n- Image optimization with WebP/AVIF\n- Lazy loading everything below the fold\n\n**UX Patterns**\n- Mobile-first responsive design\n- Skeleton loaders instead of spinners\n- Haptic feedback on mobile interactions\n\n**AI Integration** 🤖\n- Personalized content via ML\n- AI-powered search with semantic understanding\n\nWant a deep dive on any of these? 🚀",
  ],
  default: [
    "That's a great point! Let me think through this carefully...\n\nBased on what you've shared, I'd approach this by breaking it into smaller, manageable parts. The key is to start with a clear objective and work backwards from there.\n\nWould you like me to elaborate on any specific aspect? I can go deeper on the technical details, provide examples, or explore alternative approaches! 🎯",
    "Excellent question! Here's my analysis:\n\nThere are several dimensions to consider here. First, let's look at the core problem — then we can explore solutions that balance efficiency with practicality.\n\nI'd recommend starting with **Option A**: a phased approach that allows you to test assumptions early and adjust. This reduces risk while maximizing learning.\n\nWhat's your current constraint — time, budget, or technical complexity? That'll help me give more targeted advice! 💡",
    "Fascinating topic! 🔍 Let me break this down:\n\nThe intersection of what you're describing touches on several important areas. The most critical factors are:\n\n1. **Context** — Understanding the full picture before diving in\n2. **Strategy** — Choosing the right approach for your specific situation\n3. **Execution** — Implementing with precision and adaptability\n\nI'd love to explore this further with you. What specific outcome are you working towards? That way I can tailor my suggestions! ✨",
    "Great timing to ask about this! Here's what I know:\n\nThis is a rapidly evolving space, and the landscape has shifted significantly. The most important thing to keep in mind is that **the fundamentals still matter** even as new tools and approaches emerge.\n\nMy recommendation: start with a solid foundation, then layer in the advanced techniques. Would you like a structured roadmap? I can map out a clear path from where you are to where you want to be! 🗺️",
  ],
};

// ─── Helpers ────────────────────────────────────────
function getAIResponse(input) {
  const lower = input.toLowerCase();
  if (/\b(hi|hello|hey|good|greet|howdy|sup)\b/.test(lower)) {
    return random(AI_RESPONSES.greetings);
  }
  if (/\b(code|function|sort|javascript|python|program|algorithm|script)\b/.test(lower)) {
    return random(AI_RESPONSES.coding);
  }
  if (/\b(quantum|qubit|superposition)\b/.test(lower)) {
    return random(AI_RESPONSES.quantum);
  }
  if (/\b(idea|startup|app|mobile|business|innovat)\b/.test(lower)) {
    return random(AI_RESPONSES.ideas);
  }
  if (/\b(design|web|css|ui|ux|frontend|trend)\b/.test(lower)) {
    return random(AI_RESPONSES.webdesign);
  }
  return random(AI_RESPONSES.default);
}

function random(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

function formatTime() {
  return new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

// Minimal markdown to HTML
function renderMarkdown(text) {
  return text
    .replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang, code) =>
      `<pre><code class="lang-${lang || 'code'}">${escapeHtml(code.trim())}</code></pre>`)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/^### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^## (.+)$/gm, '<h3>$1</h3>')
    .replace(/^# (.+)$/gm, '<h2>$1</h2>')
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>(\n|$))+/g, match => `<ul>${match}</ul>`)
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
    .replace(/^(?!<)(.+)$/gm, (match) => match.startsWith('<') ? match : match);
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ─── DOM Refs ───────────────────────────────────────
const dom = {
  sidebar: document.getElementById('sidebar'),
  sidebarOverlay: document.getElementById('sidebarOverlay'),
  sidebarToggleBtn: document.getElementById('sidebarToggleBtn'),
  sidebarCloseBtn: document.getElementById('sidebarCloseBtn'),
  newChatBtn: document.getElementById('newChatBtn'),
  chatHistory: document.getElementById('chatHistory'),
  messagesContainer: document.getElementById('messagesContainer'),
  messagesList: document.getElementById('messagesList'),
  welcomeScreen: document.getElementById('welcomeScreen'),
  messageInput: document.getElementById('messageInput'),
  sendBtn: document.getElementById('sendBtn'),
  charCount: document.getElementById('charCount'),
  themeToggleBtn: document.getElementById('themeToggleBtn'),
  themeIcon: document.getElementById('themeIcon'),
  clearHistoryBtn: document.getElementById('clearHistoryBtn'),
  modelSelector: document.getElementById('modelSelector'),
  toast: document.getElementById('toast'),
  topShareBtn: document.getElementById('topShareBtn'),
  topExportBtn: document.getElementById('topExportBtn'),
  attachBtn: document.getElementById('attachBtn'),
  imageBtn: document.getElementById('imageBtn'),
};

// ─── UI: Messages ───────────────────────────────────
function hideWelcome() {
  if (dom.welcomeScreen && dom.welcomeScreen.style.display !== 'none') {
    dom.welcomeScreen.style.opacity = '0';
    dom.welcomeScreen.style.transform = 'scale(0.97)';
    dom.welcomeScreen.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
    setTimeout(() => { dom.welcomeScreen.style.display = 'none'; }, 220);
  }
}

function createMessageRow(role, content, id) {
  const isUser = role === 'user';
  const time = formatTime();

  const row = document.createElement('div');
  row.className = `message-row ${role}`;
  row.id = `msg-${id}`;
  row.setAttribute('role', 'listitem');

  const avatarSVG = `
    <div class="msg-avatar ${role}" aria-hidden="true">
      ${isUser ? 'U' : `
        <svg viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M6 18 Q18 5 30 18 Q18 31 6 18Z" fill="url(#msgGrad${id})" opacity="0.9"/>
          <circle cx="13" cy="15" r="2.2" fill="white"/>
          <circle cx="23" cy="15" r="2.2" fill="white"/>
          <circle cx="13.8" cy="14.2" r="0.8" fill="#1a1a2e"/>
          <circle cx="23.8" cy="14.2" r="0.8" fill="#1a1a2e"/>
          <defs>
            <linearGradient id="msgGrad${id}" x1="0" y1="0" x2="36" y2="36" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stop-color="#7c3aed"/>
              <stop offset="100%" stop-color="#06b6d4"/>
            </linearGradient>
          </defs>
        </svg>
      `}
    </div>`;

  const actionButtons = isUser ? `
    <button class="msg-action-btn" onclick="editMessage(${id})" aria-label="Edit message">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
      Edit
    </button>` : `
    <button class="msg-action-btn" onclick="copyMessage(${id})" aria-label="Copy message">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
      Copy
    </button>
    <button class="msg-action-btn" onclick="regenerateMessage()" aria-label="Regenerate response">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.86"/></svg>
      Regenerate
    </button>`;

  row.innerHTML = `
    ${avatarSVG}
    <div class="msg-content-wrap">
      <span class="msg-sender-name" aria-label="${isUser ? 'You' : 'AI'} at ${time}">
        ${isUser ? 'You' : '🤖 AI Chat Boat'} · ${time}
      </span>
      <div class="msg-bubble" id="bubble-${id}">
        ${isUser ? escapeHtml(content) : renderMarkdown(content)}
      </div>
      <div class="msg-actions" role="toolbar" aria-label="Message actions">
        ${actionButtons}
      </div>
    </div>`;

  return row;
}

function showTypingIndicator() {
  const existingTyping = document.getElementById('typing-row');
  if (existingTyping) return;

  const row = document.createElement('div');
  row.className = 'message-row ai';
  row.id = 'typing-row';
  row.setAttribute('aria-label', 'AI is typing');

  row.innerHTML = `
    <div class="msg-avatar ai" aria-hidden="true">
      <svg viewBox="0 0 36 36" fill="none">
        <path d="M6 18 Q18 5 30 18 Q18 31 6 18Z" fill="url(#typingGrad)" opacity="0.9"/>
        <defs>
          <linearGradient id="typingGrad" x1="0" y1="0" x2="36" y2="36">
            <stop offset="0%" stop-color="#7c3aed"/>
            <stop offset="100%" stop-color="#06b6d4"/>
          </linearGradient>
        </defs>
      </svg>
    </div>
    <div class="msg-content-wrap">
      <span class="msg-sender-name">🤖 AI Chat Boat · typing…</span>
      <div class="typing-indicator" role="status" aria-label="AI is typing">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>`;

  dom.messagesList.appendChild(row);
  scrollToBottom();
}

function removeTypingIndicator() {
  const typing = document.getElementById('typing-row');
  if (typing) {
    typing.style.opacity = '0';
    typing.style.transition = 'opacity 0.2s';
    setTimeout(() => typing.remove(), 200);
  }
}

function scrollToBottom(smooth = true) {
  requestAnimationFrame(() => {
    dom.messagesContainer.scrollTo({
      top: dom.messagesContainer.scrollHeight,
      behavior: smooth ? 'smooth' : 'instant',
    });
  });
}

// ─── Core: Send Message ─────────────────────────────
async function sendMessage() {
  const input = dom.messageInput.value.trim();
  if (!input || state.isLoading) return;

  hideWelcome();
  state.isLoading = true;
  state.messageCounter++;

  const userMsgId = state.messageCounter;
  state.messages.push({ id: userMsgId, role: 'user', content: input });

  // Render user message
  const userRow = createMessageRow('user', input, userMsgId);
  dom.messagesList.appendChild(userRow);
  scrollToBottom();

  // Reset input
  dom.messageInput.value = '';
  dom.messageInput.style.height = 'auto';
  dom.charCount.textContent = '0 / 8000';
  updateSendBtn();

  // Show loading state
  dom.sendBtn.classList.add('loading');
  dom.sendBtn.disabled = true;

  // Show typing indicator
  showTypingIndicator();

  // Simulate AI thinking delay (600ms – 2200ms)
  const delay = 600 + Math.random() * 1600;

  await new Promise(resolve => setTimeout(resolve, delay));

  // Generate response
  const aiResponse = getAIResponse(input);

  removeTypingIndicator();

  state.messageCounter++;
  const aiMsgId = state.messageCounter;
  state.messages.push({ id: aiMsgId, role: 'ai', content: aiResponse });

  const aiRow = createMessageRow('ai', aiResponse, aiMsgId);
  dom.messagesList.appendChild(aiRow);
  scrollToBottom();

  // Update history
  updateHistoryTitle(input);

  // Reset loading
  state.isLoading = false;
  dom.sendBtn.classList.remove('loading');
  updateSendBtn();
  dom.messageInput.focus();
}

function updateHistoryTitle(firstMessage) {
  const histItem = document.getElementById('hist-1');
  if (histItem && state.messages.length <= 2) {
    const title = firstMessage.length > 28 ? firstMessage.slice(0, 28) + '…' : firstMessage;
    histItem.querySelector('.history-item-title').textContent = title;
  }
}

// ─── Message Actions ────────────────────────────────
window.copyMessage = async function(id) {
  const bubble = document.getElementById(`bubble-${id}`);
  if (!bubble) return;
  const text = bubble.innerText;
  try {
    await navigator.clipboard.writeText(text);
    showToast('✅ Copied to clipboard!', 'success');
  } catch {
    showToast('❌ Copy failed. Please try manually.', 'error');
  }
};

window.editMessage = function(id) {
  const bubble = document.getElementById(`bubble-${id}`);
  if (!bubble) return;
  dom.messageInput.value = bubble.innerText;
  dom.messageInput.focus();
  dom.messageInput.dispatchEvent(new Event('input'));
  showToast('✏️ Message loaded for editing', 'success');
};

window.regenerateMessage = function() {
  if (state.isLoading) return;
  const lastUserMsg = [...state.messages].reverse().find(m => m.role === 'user');
  if (!lastUserMsg) return;
  // Remove last AI message from DOM
  const allRows = dom.messagesList.querySelectorAll('.message-row.ai');
  if (allRows.length) allRows[allRows.length - 1].remove();
  state.messages = state.messages.filter(m => m !== state.messages[state.messages.length - 1]);
  // Resend
  dom.messageInput.value = lastUserMsg.content;
  sendMessage();
};

// ─── New Chat ───────────────────────────────────────
function newChat() {
  state.messages = [];
  state.messageCounter = 0;
  dom.messagesList.innerHTML = '';
  dom.welcomeScreen.style.display = '';
  dom.welcomeScreen.style.opacity = '1';
  dom.welcomeScreen.style.transform = '';
  dom.welcomeScreen.style.transition = '';
  dom.messageInput.value = '';
  dom.charCount.textContent = '0 / 8000';
  updateSendBtn();

  const sessionId = `chat-${Date.now()}`;
  state.activeChatId = sessionId;

  const histItem = document.createElement('button');
  histItem.className = 'history-item active';
  histItem.id = sessionId;
  histItem.innerHTML = `
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 0 2 2z"/></svg>
    <div class="history-item-info">
      <span class="history-item-title">New Chat</span>
      <span class="history-item-time">${formatTime()}</span>
    </div>`;

  document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
  dom.chatHistory.insertBefore(histItem, dom.chatHistory.firstChild);
  dom.chatHistory.scrollTo({ top: 0, behavior: 'smooth' });

  if (window.innerWidth < 768) closeSidebar();
}

// ─── Input Handling ─────────────────────────────────
function updateSendBtn() {
  const hasText = dom.messageInput.value.trim().length > 0;
  dom.sendBtn.disabled = !hasText || state.isLoading;
}

dom.messageInput.addEventListener('input', () => {
  // Auto-resize
  dom.messageInput.style.height = 'auto';
  dom.messageInput.style.height = Math.min(dom.messageInput.scrollHeight, 200) + 'px';

  // Char count
  const len = dom.messageInput.value.length;
  dom.charCount.textContent = `${len} / 8000`;
  dom.charCount.style.color = len > 7000 ? '#ef4444' : len > 6000 ? '#f59e0b' : '';

  updateSendBtn();
});

dom.messageInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    if (!dom.sendBtn.disabled) sendMessage();
  }
});

dom.sendBtn.addEventListener('click', sendMessage);

// ─── Suggestion Cards ───────────────────────────────
document.querySelectorAll('.suggestion-card').forEach(card => {
  card.addEventListener('click', () => {
    const prompt = card.dataset.prompt;
    if (prompt) {
      dom.messageInput.value = prompt;
      dom.messageInput.dispatchEvent(new Event('input'));
      dom.messageInput.focus();
      setTimeout(() => sendMessage(), 150);
    }
  });
});

// ─── Sidebar ────────────────────────────────────────
function openSidebar() {
  dom.sidebar.classList.add('open');
  dom.sidebarOverlay.classList.add('active');
  dom.sidebarToggleBtn.setAttribute('aria-expanded', 'true');
}

function closeSidebar() {
  dom.sidebar.classList.remove('open');
  dom.sidebarOverlay.classList.remove('active');
  dom.sidebarToggleBtn.setAttribute('aria-expanded', 'false');
}

dom.sidebarToggleBtn.addEventListener('click', () => {
  dom.sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
});

dom.sidebarCloseBtn.addEventListener('click', closeSidebar);
dom.sidebarOverlay.addEventListener('click', closeSidebar);
dom.newChatBtn.addEventListener('click', newChat);

// ─── Theme Toggle ───────────────────────────────────
let isDarkMode = true;

dom.themeToggleBtn.addEventListener('click', () => {
  isDarkMode = !isDarkMode;
  document.body.classList.toggle('light-mode', !isDarkMode);
  const span = dom.themeToggleBtn.querySelector('span');
  if (isDarkMode) {
    dom.themeIcon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>';
    if (span) span.textContent = 'Dark Mode';
  } else {
    dom.themeIcon.innerHTML = '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>';
    if (span) span.textContent = 'Light Mode';
  }
  showToast(isDarkMode ? '🌙 Dark mode activated' : '☀️ Light mode activated', 'success');
});

// ─── Clear History ──────────────────────────────────
dom.clearHistoryBtn.addEventListener('click', () => {
  state.messages = [];
  dom.messagesList.innerHTML = '';
  dom.welcomeScreen.style.display = '';
  dom.welcomeScreen.style.opacity = '1';
  dom.welcomeScreen.style.transform = '';
  document.querySelectorAll('.history-item:not(#hist-1)').forEach(el => el.remove());
  const histItem = document.getElementById('hist-1');
  if (histItem) {
    histItem.querySelector('.history-item-title').textContent = 'Getting Started';
    histItem.querySelector('.history-item-time').textContent = 'Just now';
  }
  showToast('🗑️ Chat history cleared', 'success');
});

// ─── Export ─────────────────────────────────────────
dom.topExportBtn.addEventListener('click', () => {
  if (!state.messages.length) {
    showToast('⚠️ No messages to export', 'error');
    return;
  }
  const text = state.messages.map(m =>
    `[${m.role.toUpperCase()}]\n${m.content}\n`
  ).join('\n' + '─'.repeat(40) + '\n\n');

  const blob = new Blob([`AI Chat Boat — Conversation Export\n${'='.repeat(40)}\n${new Date().toLocaleString()}\n\n${text}`], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `ai-chat-export-${Date.now()}.txt`;
  a.click();
  URL.revokeObjectURL(url);
  showToast('📄 Conversation exported!', 'success');
});

// ─── Share ──────────────────────────────────────────
dom.topShareBtn.addEventListener('click', async () => {
  if (!state.messages.length) {
    showToast('⚠️ Nothing to share yet', 'error');
    return;
  }
  const shareText = `AI Chat Boat Conversation\n\n${state.messages.slice(-4).map(m => `${m.role === 'user' ? 'Me' : 'AI'}: ${m.content.slice(0, 100)}...`).join('\n\n')}`;
  try {
    if (navigator.share) {
      await navigator.share({ title: 'AI Chat Boat', text: shareText });
    } else {
      await navigator.clipboard.writeText(shareText);
      showToast('🔗 Conversation copied to clipboard!', 'success');
    }
  } catch {
    showToast('❌ Share failed', 'error');
  }
});

// ─── Tool Buttons ────────────────────────────────────
dom.attachBtn.addEventListener('click', () => {
  showToast('📎 File attachment coming soon!', 'success');
});
dom.imageBtn.addEventListener('click', () => {
  showToast('🖼️ Image upload coming soon!', 'success');
});

// ─── Toast ──────────────────────────────────────────
let toastTimeout;
function showToast(message, type = '') {
  clearTimeout(toastTimeout);
  dom.toast.textContent = message;
  dom.toast.className = `toast${type ? ' ' + type : ''} show`;
  toastTimeout = setTimeout(() => {
    dom.toast.classList.remove('show');
  }, 3000);
}

// ─── Particles ──────────────────────────────────────
(function initParticles() {
  const canvas = document.getElementById('particles-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let W = window.innerWidth, H = window.innerHeight;
  canvas.width = W;
  canvas.height = H;

  const PARTICLE_COUNT = 55;
  const particles = [];

  const colors = ['rgba(124,58,237,', 'rgba(6,182,212,', 'rgba(236,72,153,'];

  for (let i = 0; i < PARTICLE_COUNT; i++) {
    particles.push({
      x: Math.random() * W,
      y: Math.random() * H,
      r: Math.random() * 1.5 + 0.3,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      color: colors[Math.floor(Math.random() * colors.length)],
      opacity: Math.random() * 0.5 + 0.1,
    });
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0) p.x = W;
      if (p.x > W) p.x = 0;
      if (p.y < 0) p.y = H;
      if (p.y > H) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = p.color + p.opacity + ')';
      ctx.fill();
    });

    // Draw connections
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 130) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(124,58,237,${0.08 * (1 - dist / 130)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(draw);
  }
  draw();

  window.addEventListener('resize', () => {
    W = window.innerWidth; H = window.innerHeight;
    canvas.width = W; canvas.height = H;
  });
})();

// ─── Keyboard Shortcuts ──────────────────────────────
document.addEventListener('keydown', (e) => {
  // Ctrl/Cmd + K → focus input
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    dom.messageInput.focus();
  }
  // Ctrl/Cmd + N → new chat
  if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
    e.preventDefault();
    newChat();
  }
  // Esc → close sidebar on mobile
  if (e.key === 'Escape') closeSidebar();
});

// ─── Init ───────────────────────────────────────────
dom.messageInput.focus();
console.log('%c🤖 AI Chat Boat', 'color:#7c3aed;font-size:20px;font-weight:bold;');
console.log('%cWelcome! Built with ❤️ by Antigravity AI', 'color:#06b6d4;font-size:12px;');

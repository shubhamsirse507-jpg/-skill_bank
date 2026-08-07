/* ========================================
   AI CHAT BOAT — Django Integration JS
   ======================================== */
'use strict';

// ─── State ─────────────────────────────────────────
const state = {
  messages: [],
  isLoading: false,
  messageCounter: 0,
};

// ─── AI Responses ───────────────────────────────────
const AI_RESPONSES = {
  greetings: [
    "Hello! 👋 I'm **AI Chat Boat**, your intelligent assistant built into **Skill Bank**. Ask me anything — coding, career advice, skills, or just a chat!",
    "Hi there! Great to see you on Skill Bank! I'm ready to help with anything — skill-building, technical questions, or general knowledge. What's on your mind?",
    "Hey! 🌟 Welcome! I'm AI Chat Boat — your personal AI companion. Ask me about skills, technology, learning paths, or anything else!",
  ],
  coding: [
    "Here's a clean Python implementation:\n\n```python\ndef bubble_sort(arr):\n    n = len(arr)\n    for i in range(n - 1):\n        for j in range(n - i - 1):\n            if arr[j] > arr[j + 1]:\n                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n    return arr\n\n# Example\nmy_list = [64, 34, 25, 12, 22, 11, 90]\nprint(\"Sorted:\", bubble_sort(my_list))\n```\n\n**How it works:**\n- Compares adjacent elements and swaps if needed\n- Time complexity: **O(n²)** — ideal for small datasets\n- Space complexity: **O(1)** — in-place sorting 🚀",
    "Great coding question! Here's a Django view pattern:\n\n```python\nfrom django.views.generic import ListView\nfrom django.contrib.auth.mixins import LoginRequiredMixin\n\nclass SkillListView(LoginRequiredMixin, ListView):\n    model = Skill\n    template_name = 'skills/list.html'\n    context_object_name = 'skills'\n    paginate_by = 12\n\n    def get_queryset(self):\n        return Skill.objects.filter(\n            user=self.request.user\n        ).order_by('-created_at')\n```\n\nThis pattern combines **class-based views** with **login protection** — a Django best practice! 💡",
  ],
  quantum: [
    "Great question! **Quantum Computing** explained simply:\n\n🔵 **Classical computers** use bits (0 or 1) — like light switches.\n\n🟣 **Quantum computers** use **qubits** which can be 0, 1, or *both at once* (superposition)!\n\nImagine searching every key in a lock simultaneously — that's quantum power.\n\n**Key concepts:**\n- **Superposition** — multiple states simultaneously\n- **Entanglement** — qubits linked across distances\n- **Interference** — amplifying correct answers\n\n💡 Quantum computers excel at cryptography, drug discovery, and optimization!",
  ],
  skills: [
    "Great question about skill development! 🎯\n\n**Top In-Demand Skills for 2025:**\n\n1. **🤖 AI & Machine Learning** — Python, TensorFlow, PyTorch\n2. **☁️ Cloud Computing** — AWS, Azure, Google Cloud\n3. **🔒 Cybersecurity** — Ethical hacking, SIEM, Zero Trust\n4. **📊 Data Science** — SQL, Pandas, visualization\n5. **🌐 Full-Stack Web** — React, Django, Node.js\n6. **📱 Mobile Dev** — Flutter, React Native\n\n**My recommendation:** Start with Python + one cloud platform. That combination opens 80% of tech doors! 🚀\n\nWould you like a personalized learning roadmap?",
    "Building skills effectively requires a smart approach! 📚\n\n**The 3-Phase Learning Method:**\n\n1. **Learn** (20%) — Consume tutorials, docs, courses\n2. **Build** (60%) — Create real projects from scratch\n3. **Teach** (20%) — Write blogs, explain to others\n\n**Pro tip:** The Feynman Technique is gold — if you can't explain it simply, you don't understand it yet.\n\nWhat specific skill are you trying to build? I can give you a targeted roadmap! 🎯",
  ],
  ideas: [
    "Here are **5 innovative app ideas** for 2025 🚀\n\n1. **🧠 MindMap AI** — Mental health app detecting mood from journals\n2. **🌿 GreenTrack** — Carbon footprint gamification platform\n3. **👁️ SightAssist** — AR app for visually impaired with real-time narration\n4. **🎓 SkillSwap** — Peer-to-peer skill exchange marketplace\n5. **🍽️ FridgeChef** — AI recipe generator from fridge contents\n\nWant a deep-dive into any of these? 💡",
  ],
  webdesign: [
    "Top **Web Design Best Practices for 2025** 🎨\n\n**Visual Design**\n- Dark mode with smooth transitions\n- Glassmorphism for depth & premium feel\n- 60fps micro-animations\n\n**Typography**\n- Variable fonts (e.g., Outfit, Inter)\n- Fluid type with `clamp()`\n- WCAG AAA contrast ratios\n\n**Performance**\n- Core Web Vitals: LCP < 2.5s, CLS < 0.1\n- WebP/AVIF images\n- Lazy loading below the fold\n\n**Django-specific tips:**\n- Use `{% static %}` for all assets\n- WhiteNoise for static file serving in production\n- django-compressor for CSS/JS minification\n\nWant a deep dive? 🚀",
  ],
  django: [
    "**Django Best Practices** for your Skill Bank project! 🐍\n\n**Project Structure**\n```\nskill_bank/\n├── apps/\n│   ├── authentication/\n│   ├── profiles/\n│   ├── chatboat/      ← You are here!\n│   └── notifications/\n├── templates/\n├── static/\n└── manage.py\n```\n\n**Key patterns to follow:**\n- Use **class-based views** for CRUD operations\n- **`@login_required`** for protected pages\n- **Custom managers** for complex querysets\n- **signals** for decoupled side-effects (e.g., notifications)\n- **`django-environ`** for environment variables\n\n**Performance:**\n- `select_related()` / `prefetch_related()` to avoid N+1 queries\n- Database indexing on frequently filtered fields\n\nWhat specific Django topic would you like help with? 🎯",
  ],
  default: [
    "That's a great point! 🎯\n\nBased on what you've shared, I'd approach this by breaking it into smaller, manageable parts. Start with a clear objective and work backwards.\n\nWould you like me to elaborate on any specific aspect? I can dive deeper into technical details, provide examples, or explore alternative approaches! ✨",
    "Excellent question! Here's my analysis:\n\nThere are several important dimensions to consider here. Let's look at the core problem — then explore solutions balancing efficiency with practicality.\n\nI'd recommend a **phased approach** — test assumptions early, adjust as you go. This minimizes risk while maximizing learning.\n\nWhat's your biggest constraint — time, budget, or technical complexity? That'll help me give more targeted advice! 💡",
    "Fascinating topic! 🔍\n\nThe most critical factors are:\n\n1. **Context** — Understanding the full picture first\n2. **Strategy** — Choosing the right approach for your situation\n3. **Execution** — Implementing with precision and adaptability\n\nI'd love to explore this further. What specific outcome are you working towards? ✨",
  ],
};

function getAIResponse(input) {
  const lower = input.toLowerCase();
  if (/\b(hi|hello|hey|good|greet|howdy)\b/.test(lower)) return random(AI_RESPONSES.greetings);
  if (/\b(code|function|sort|javascript|python|program|algorithm|django|view)\b/.test(lower)) return random(AI_RESPONSES.coding);
  if (/\b(quantum|qubit|superposition)\b/.test(lower)) return random(AI_RESPONSES.quantum);
  if (/\b(skill|learn|career|roadmap|course|training)\b/.test(lower)) return random(AI_RESPONSES.skills);
  if (/\b(idea|startup|app|mobile|business|innovat)\b/.test(lower)) return random(AI_RESPONSES.ideas);
  if (/\b(design|web|css|ui|ux|frontend|trend)\b/.test(lower)) return random(AI_RESPONSES.webdesign);
  if (/\b(django|model|url|template|migration|orm)\b/.test(lower)) return random(AI_RESPONSES.django);
  return random(AI_RESPONSES.default);
}

function random(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function formatTime() { return new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }); }

// ─── Markdown renderer ──────────────────────────────
function renderMarkdown(text) {
  return text
    .replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang, code) =>
      `<pre><code class="lang-${lang||'code'}">${escapeHtml(code.trim())}</code></pre>`)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>(\n|$))+/g, m => `<ul>${m}</ul>`)
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n/g, '<br>');
}

function escapeHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ─── DOM refs ───────────────────────────────────────
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
  toast: document.getElementById('toast'),
  topExportBtn: document.getElementById('topExportBtn'),
  topShareBtn: document.getElementById('topShareBtn'),
};

// ─── Messages ───────────────────────────────────────
function hideWelcome() {
  const ws = dom.welcomeScreen;
  if (ws && ws.style.display !== 'none') {
    ws.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
    ws.style.opacity = '0'; ws.style.transform = 'scale(0.97)';
    setTimeout(() => { ws.style.display = 'none'; }, 220);
  }
}

function createMessageRow(role, content, id, providerName) {
  const isUser = role === 'user';
  const time = formatTime();
  const row = document.createElement('div');
  row.className = `message-row ${role}`;
  row.id = `msg-${id}`;
  row.setAttribute('role', 'listitem');

  const avatarSVG = isUser
    ? `<div class="msg-avatar user" aria-hidden="true">${window.CHAT_USERNAME ? window.CHAT_USERNAME[0].toUpperCase() : 'U'}</div>`
    : `<div class="msg-avatar ai" aria-hidden="true">
        <svg viewBox="0 0 36 36" fill="none">
          <path d="M6 18 Q18 5 30 18 Q18 31 6 18Z" fill="url(#mg${id})" opacity="0.9"/>
          <circle cx="13" cy="15" r="2.2" fill="white"/>
          <circle cx="23" cy="15" r="2.2" fill="white"/>
          <defs><linearGradient id="mg${id}" x1="0" y1="0" x2="36" y2="36" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#7c3aed"/><stop offset="100%" stop-color="#06b6d4"/>
          </linearGradient></defs>
        </svg>
      </div>`;

  const actions = isUser
    ? `<button class="msg-action-btn" onclick="editMsg(${id})">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>Edit</button>`
    : `<button class="msg-action-btn" onclick="copyMsg(${id})">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>Copy</button>
       <button class="msg-action-btn" onclick="regenerate()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.86"/></svg>Regenerate</button>`;

  const senderTag = isUser ? (window.CHAT_USERNAME || 'You') : (providerName || '🤖 AI Chat Boat');

  row.innerHTML = `${avatarSVG}
    <div class="msg-content-wrap">
      <span class="msg-sender-name">${senderTag} · ${time}</span>
      <div class="msg-bubble" id="bubble-${id}">${isUser ? escapeHtml(content) : renderMarkdown(content)}</div>
      <div class="msg-actions">${actions}</div>
    </div>`;
  return row;
}

function showTyping() {
  if (document.getElementById('typing-row')) return;
  const row = document.createElement('div');
  row.className = 'message-row ai'; row.id = 'typing-row';
  row.innerHTML = `
    <div class="msg-avatar ai" aria-hidden="true">
      <svg viewBox="0 0 36 36" fill="none">
        <path d="M6 18 Q18 5 30 18 Q18 31 6 18Z" fill="url(#tg)" opacity="0.9"/>
        <defs><linearGradient id="tg" x1="0" y1="0" x2="36" y2="36">
          <stop offset="0%" stop-color="#7c3aed"/><stop offset="100%" stop-color="#06b6d4"/>
        </linearGradient></defs>
      </svg>
    </div>
    <div class="msg-content-wrap">
      <span class="msg-sender-name">🤖 AI Chat Boat · typing…</span>
      <div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>
    </div>`;
  dom.messagesList.appendChild(row);
  scrollBottom();
}

function removeTyping() {
  const t = document.getElementById('typing-row');
  if (t) { t.style.opacity = '0'; t.style.transition = 'opacity 0.2s'; setTimeout(() => t.remove(), 200); }
}

function scrollBottom() {
  requestAnimationFrame(() => dom.messagesContainer.scrollTo({ top: dom.messagesContainer.scrollHeight, behavior: 'smooth' }));
}

// ─── Send ───────────────────────────────────────────
async function sendMessage() {
  const input = dom.messageInput.value.trim();
  if (!input || state.isLoading) return;
  hideWelcome();
  state.isLoading = true;
  state.messageCounter++;
  const uid = state.messageCounter;
  state.messages.push({ id: uid, role: 'user', content: input });
  dom.messagesList.appendChild(createMessageRow('user', input, uid));
  scrollBottom();
  dom.messageInput.value = '';
  dom.messageInput.style.height = 'auto';
  dom.charCount.textContent = '0 / 8000';
  updateSendBtn();
  dom.sendBtn.classList.add('loading');
  dom.sendBtn.disabled = true;
  showTyping();

  const selectedModel = document.getElementById('modelSelector') ? document.getElementById('modelSelector').value : 'gemini';
  let reply = '';
  let providerName = '🤖 AI Chat Boat';

  try {
    const res = await fetch('/chat/api/send/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: input, provider: selectedModel })
    });
    const data = await res.json();

    if (data.response) {
      reply = data.response;
      providerName = `🤖 ${data.provider_used || 'AI Chat Boat'}`;
    } else {
      reply = getAIResponse(input);
    }
  } catch (err) {
    console.warn('API error:', err);
    reply = getAIResponse(input);
  }

  removeTyping();
  state.messageCounter++;
  const aid = state.messageCounter;
  state.messages.push({ id: aid, role: 'ai', content: reply });
  dom.messagesList.appendChild(createMessageRow('ai', reply, aid, providerName));
  scrollBottom();
  updateHistoryTitle(input);
  state.isLoading = false;
  dom.sendBtn.classList.remove('loading');
  updateSendBtn();
  dom.messageInput.focus();
}

function updateHistoryTitle(msg) {
  const h = document.getElementById('hist-current');
  if (h && state.messages.length <= 2) {
    h.querySelector('.history-item-title').textContent = msg.length > 26 ? msg.slice(0, 26) + '…' : msg;
  }
}

// ─── Actions ────────────────────────────────────────
window.copyMsg = async function(id) {
  const b = document.getElementById(`bubble-${id}`);
  if (!b) return;
  try { await navigator.clipboard.writeText(b.innerText); showToast('✅ Copied!', 'success'); }
  catch { showToast('❌ Copy failed', 'error'); }
};

window.editMsg = function(id) {
  const b = document.getElementById(`bubble-${id}`);
  if (!b) return;
  dom.messageInput.value = b.innerText;
  dom.messageInput.focus();
  dom.messageInput.dispatchEvent(new Event('input'));
  showToast('✏️ Loaded for editing', 'success');
};

window.regenerate = function() {
  if (state.isLoading) return;
  const last = [...state.messages].reverse().find(m => m.role === 'user');
  if (!last) return;
  const lastAiRow = [...dom.messagesList.querySelectorAll('.message-row.ai')].pop();
  if (lastAiRow) lastAiRow.remove();
  state.messages = state.messages.slice(0, -1);
  dom.messageInput.value = last.content;
  sendMessage();
};

// ─── New Chat ────────────────────────────────────────
function newChat() {
  state.messages = []; state.messageCounter = 0;
  dom.messagesList.innerHTML = '';
  const ws = dom.welcomeScreen;
  ws.style.display = ''; ws.style.opacity = '1'; ws.style.transform = '';
  dom.messageInput.value = ''; dom.charCount.textContent = '0 / 8000';
  updateSendBtn();

  const histItem = document.createElement('button');
  histItem.className = 'history-item active'; histItem.id = 'hist-current';
  histItem.innerHTML = `
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
    <div class="history-item-info">
      <span class="history-item-title">New Chat</span>
      <span class="history-item-time">${formatTime()}</span>
    </div>`;
  document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
  dom.chatHistory.insertBefore(histItem, dom.chatHistory.firstChild);
  if (window.innerWidth < 768) closeSidebar();
}

// ─── Input handling ──────────────────────────────────
function updateSendBtn() {
  dom.sendBtn.disabled = !dom.messageInput.value.trim() || state.isLoading;
}

dom.messageInput.addEventListener('input', () => {
  dom.messageInput.style.height = 'auto';
  dom.messageInput.style.height = Math.min(dom.messageInput.scrollHeight, 200) + 'px';
  const len = dom.messageInput.value.length;
  dom.charCount.textContent = `${len} / 8000`;
  dom.charCount.style.color = len > 7000 ? '#ef4444' : len > 6000 ? '#f59e0b' : '';
  updateSendBtn();
});

dom.messageInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); if (!dom.sendBtn.disabled) sendMessage(); }
});

dom.sendBtn.addEventListener('click', sendMessage);

// ─── Suggestion cards ────────────────────────────────
document.querySelectorAll('.suggestion-card').forEach(card => {
  card.addEventListener('click', () => {
    const prompt = card.dataset.prompt;
    if (prompt) { dom.messageInput.value = prompt; dom.messageInput.dispatchEvent(new Event('input')); setTimeout(() => sendMessage(), 100); }
  });
});

// ─── Sidebar ─────────────────────────────────────────
function openSidebar() { dom.sidebar.classList.add('open'); dom.sidebarOverlay.classList.add('active'); }
function closeSidebar() { dom.sidebar.classList.remove('open'); dom.sidebarOverlay.classList.remove('active'); }
dom.sidebarToggleBtn.addEventListener('click', () => dom.sidebar.classList.contains('open') ? closeSidebar() : openSidebar());
dom.sidebarCloseBtn.addEventListener('click', closeSidebar);
dom.sidebarOverlay.addEventListener('click', closeSidebar);
dom.newChatBtn.addEventListener('click', newChat);

// ─── Theme ────────────────────────────────────────────
let dark = true;
dom.themeToggleBtn && dom.themeToggleBtn.addEventListener('click', () => {
  dark = !dark;
  document.body.classList.toggle('light-mode', !dark);
  const span = dom.themeToggleBtn.querySelector('span');
  if (dark) {
    if (dom.themeIcon) dom.themeIcon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>';
    if (span) span.textContent = 'Dark Mode';
  } else {
    if (dom.themeIcon) dom.themeIcon.innerHTML = '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>';
    if (span) span.textContent = 'Light Mode';
  }
  showToast(dark ? '🌙 Dark mode' : '☀️ Light mode', 'success');
});

// ─── Clear ────────────────────────────────────────────
dom.clearHistoryBtn && dom.clearHistoryBtn.addEventListener('click', () => {
  state.messages = []; dom.messagesList.innerHTML = '';
  const ws = dom.welcomeScreen;
  ws.style.display = ''; ws.style.opacity = '1'; ws.style.transform = '';
  showToast('🗑️ Chat cleared', 'success');
});

// ─── Export ───────────────────────────────────────────
dom.topExportBtn && dom.topExportBtn.addEventListener('click', () => {
  if (!state.messages.length) { showToast('⚠️ No messages to export', 'error'); return; }
  const text = state.messages.map(m => `[${m.role.toUpperCase()}]\n${m.content}`).join('\n\n' + '─'.repeat(40) + '\n\n');
  const blob = new Blob([`AI Chat Boat — Skill Bank\n${'='.repeat(40)}\n${new Date().toLocaleString()}\n\n${text}`], { type: 'text/plain' });
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
  a.download = `chat-export-${Date.now()}.txt`; a.click();
  showToast('📄 Exported!', 'success');
});

// ─── Share ────────────────────────────────────────────
dom.topShareBtn && dom.topShareBtn.addEventListener('click', async () => {
  if (!state.messages.length) { showToast('⚠️ Nothing to share', 'error'); return; }
  const txt = state.messages.slice(-4).map(m => `${m.role === 'user' ? (window.CHAT_USERNAME||'Me') : 'AI'}: ${m.content.slice(0, 100)}...`).join('\n\n');
  try {
    if (navigator.share) await navigator.share({ title: 'AI Chat Boat', text: txt });
    else { await navigator.clipboard.writeText(txt); showToast('🔗 Copied to clipboard!', 'success'); }
  } catch { showToast('❌ Share failed', 'error'); }
});

// ─── Toast ────────────────────────────────────────────
let toastTimeout;
function showToast(msg, type = '') {
  clearTimeout(toastTimeout);
  const t = dom.toast;
  t.textContent = msg;
  t.className = `toast${type ? ' ' + type : ''} show`;
  toastTimeout = setTimeout(() => t.classList.remove('show'), 3000);
}

// ─── Particles ────────────────────────────────────────
(function() {
  const canvas = document.getElementById('particles-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W = innerWidth, H = innerHeight;
  canvas.width = W; canvas.height = H;
  const colors = ['rgba(124,58,237,', 'rgba(6,182,212,', 'rgba(236,72,153,'];
  const particles = Array.from({ length: 50 }, () => ({
    x: Math.random() * W, y: Math.random() * H,
    r: Math.random() * 1.5 + 0.3,
    vx: (Math.random() - 0.5) * 0.4, vy: (Math.random() - 0.5) * 0.4,
    color: colors[Math.floor(Math.random() * 3)],
    opacity: Math.random() * 0.5 + 0.1,
  }));
  function draw() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0) p.x = W; if (p.x > W) p.x = 0;
      if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = p.color + p.opacity + ')'; ctx.fill();
    });
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x, dy = particles[i].y - particles[j].y;
        const d = Math.sqrt(dx*dx + dy*dy);
        if (d < 120) {
          ctx.beginPath(); ctx.moveTo(particles[i].x, particles[i].y); ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(124,58,237,${0.08*(1-d/120)})`; ctx.lineWidth = 0.5; ctx.stroke();
        }
      }
    }
    requestAnimationFrame(draw);
  }
  draw();
  addEventListener('resize', () => { W = innerWidth; H = innerHeight; canvas.width = W; canvas.height = H; });
})();

// ─── Keyboard shortcuts ───────────────────────────────
document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); dom.messageInput.focus(); }
  if ((e.ctrlKey || e.metaKey) && e.key === 'n') { e.preventDefault(); newChat(); }
  if (e.key === 'Escape') closeSidebar();
});

// ─── Init ─────────────────────────────────────────────
dom.messageInput.focus();

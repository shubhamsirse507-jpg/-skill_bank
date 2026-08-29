/* ========================================
   AI CHAT BOAT — Django Integration JS
   Multimodal Voice (Mic) & Vision (Camera)
   ======================================== */
'use strict';

// ─── State ─────────────────────────────────────────
const state = {
  messages: [],
  isLoading: false,
  messageCounter: 0,
  attachedImage: null, // Base64 Data URL
  isRecording: false,
  recognition: null,
  cameraStream: null,
  facingMode: 'user', // 'user' or 'environment'
  currentlySpeakingId: null,
};

// ─── AI Responses Fallbacks ─────────────────────────
const AI_RESPONSES = {
  greetings: [
    "Hello! 👋 I'm **AI Chat Boat**, your intelligent assistant built into **Skill Bank**. Ask me anything — via text, mic 🎙️, or photo 📸!",
    "Hi there! Great to see you on Skill Bank! I can help you find skill swap matches, learn technical roadmaps, or analyze documents/photos you upload. What's on your mind?",
  ],
  skills: [
    "Great question about skill development! 🎯\n\n**Top In-Demand Skills for 2025:**\n\n1. **🤖 AI & Prompting** — Python, LLMs, LangChain\n2. **☁️ Cloud Computing** — AWS, Azure, Docker\n3. **🌐 Full-Stack Web** — React, Django, Node.js\n4. **🎨 UI/UX & Design** — Figma, Design Systems\n\nWhat skill are you looking to trade or learn today?",
  ],
  default: [
    "That's a great question! 🎯\n\nBased on what you've shared, I can help connect this with suitable skill exchange paths on SkillBank. Feel free to ask more or attach an image / speak via mic for more details!",
  ],
};

function getAIResponse(input) {
  const lower = input.toLowerCase();
  if (/\b(hi|hello|hey|greet)\b/.test(lower)) return AI_RESPONSES.greetings[0];
  if (/\b(skill|learn|career|roadmap|course)\b/.test(lower)) return AI_RESPONSES.skills[0];
  return AI_RESPONSES.default[0];
}

function formatTime() {
  return new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

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
  return str ? str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') : '';
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

  // Mic & Camera Elements
  micBtn: document.getElementById('micBtn'),
  voiceListeningBar: document.getElementById('voiceListeningBar'),
  voiceStopBtn: document.getElementById('voiceStopBtn'),
  cameraBtn: document.getElementById('cameraBtn'),
  imageUploadBtn: document.getElementById('imageUploadBtn'),
  fileUploadInput: document.getElementById('fileUploadInput'),
  imagePreviewBar: document.getElementById('imagePreviewBar'),
  imagePreviewThumb: document.getElementById('imagePreviewThumb'),
  removeImageBtn: document.getElementById('removeImageBtn'),

  // Camera Modal Elements
  cameraModal: document.getElementById('cameraModal'),
  cameraVideo: document.getElementById('cameraVideo'),
  cameraCanvas: document.getElementById('cameraCanvas'),
  closeCameraBtn: document.getElementById('closeCameraBtn'),
  snapPhotoBtn: document.getElementById('snapPhotoBtn'),
  switchCameraBtn: document.getElementById('switchCameraBtn'),
  modalUploadBtn: document.getElementById('modalUploadBtn'),
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

function createMessageRow(role, content, id, providerName, attachedImgUrl) {
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
            <stop offset="0%" stop-color="#0c6c63"/><stop offset="100%" stop-color="#14b8a6"/>
          </linearGradient></defs>
        </svg>
      </div>`;

  const imgHtml = attachedImgUrl ? `<img src="${attachedImgUrl}" class="msg-attached-img" alt="Uploaded Image" />` : '';

  const actions = isUser
    ? `<button class="msg-action-btn" onclick="editMsg(${id})">
        <i class="fa-solid fa-pen-to-square"></i> Edit</button>`
    : `<button class="msg-action-btn" onclick="copyMsg(${id})">
        <i class="fa-solid fa-copy"></i> Copy</button>
       <button class="msg-action-btn" onclick="speakMsg(${id})" id="tts-btn-${id}">
        <i class="fa-solid fa-volume-high"></i> Listen</button>
       <button class="msg-action-btn" onclick="regenerate()">
        <i class="fa-solid fa-arrows-rotate"></i> Retry</button>`;

  const senderTag = isUser ? (window.CHAT_USERNAME || 'You') : (providerName || '🤖 AI Chat Boat');

  row.innerHTML = `${avatarSVG}
    <div class="msg-content-wrap">
      <span class="msg-sender-name">${senderTag} · ${time}</span>
      <div class="msg-bubble" id="bubble-${id}">
        ${imgHtml}
        ${isUser ? escapeHtml(content) : renderMarkdown(content)}
      </div>
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
          <stop offset="0%" stop-color="#0c6c63"/><stop offset="100%" stop-color="#14b8a6"/>
        </linearGradient></defs>
      </svg>
    </div>
    <div class="msg-content-wrap">
      <span class="msg-sender-name">🤖 AI Chat Boat · analyzing…</span>
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

// ─── Send Message Flow ──────────────────────────────
async function sendMessage() {
  const input = dom.messageInput.value.trim();
  const currentImg = state.attachedImage;
  if ((!input && !currentImg) || state.isLoading) return;

  hideWelcome();
  state.isLoading = true;
  state.messageCounter++;
  const uid = state.messageCounter;

  state.messages.push({ id: uid, role: 'user', content: input || '[Attached Image]', image: currentImg });
  dom.messagesList.appendChild(createMessageRow('user', input, uid, null, currentImg));
  scrollBottom();

  // Reset inputs & preview
  dom.messageInput.value = '';
  dom.messageInput.style.height = 'auto';
  dom.charCount.textContent = '0 / 8000';
  removeAttachedImage();
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
      body: JSON.stringify({ message: input, provider: selectedModel, image: currentImg })
    });
    const data = await res.json();

    if (data.response) {
      reply = data.response;
      providerName = `🤖 ${data.provider_used || 'AI Chat Boat'}`;
    } else {
      reply = getAIResponse(input || "analyze image");
    }
  } catch (err) {
    console.warn('API error:', err);
    reply = getAIResponse(input || "analyze image");
  }

  removeTyping();
  state.messageCounter++;
  const aid = state.messageCounter;
  state.messages.push({ id: aid, role: 'ai', content: reply });
  dom.messagesList.appendChild(createMessageRow('ai', reply, aid, providerName));
  scrollBottom();
  updateHistoryTitle(input || 'Visual Query');
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

// ─── Image Handling ─────────────────────────────────
function setAttachedImage(dataUrl) {
  state.attachedImage = dataUrl;
  if (dom.imagePreviewThumb) dom.imagePreviewThumb.src = dataUrl;
  if (dom.imagePreviewBar) dom.imagePreviewBar.style.display = 'flex';
  updateSendBtn();
  showToast('📸 Image attached!', 'success');
}

function removeAttachedImage() {
  state.attachedImage = null;
  if (dom.imagePreviewThumb) dom.imagePreviewThumb.src = '';
  if (dom.imagePreviewBar) dom.imagePreviewBar.style.display = 'none';
  if (dom.fileUploadInput) dom.fileUploadInput.value = '';
  updateSendBtn();
}

if (dom.removeImageBtn) {
  dom.removeImageBtn.addEventListener('click', removeAttachedImage);
}

if (dom.imageUploadBtn && dom.fileUploadInput) {
  dom.imageUploadBtn.addEventListener('click', () => dom.fileUploadInput.click());
  dom.fileUploadInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (evt) => setAttachedImage(evt.target.result);
      reader.readAsDataURL(file);
    }
  });
}

// ─── Camera Modal & Live Stream ─────────────────────
async function startCamera() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    showToast('⚠️ Camera not supported in this browser', 'error');
    return;
  }
  try {
    stopCamera();
    const constraints = {
      video: { facingMode: state.facingMode, width: { ideal: 1280 }, height: { ideal: 720 } }
    };
    state.cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
    dom.cameraVideo.srcObject = state.cameraStream;
    dom.cameraModal.style.display = 'flex';
  } catch (err) {
    console.error('Camera access error:', err);
    showToast('❌ Camera permission denied', 'error');
  }
}

function stopCamera() {
  if (state.cameraStream) {
    state.cameraStream.getTracks().forEach(track => track.stop());
    state.cameraStream = null;
  }
  if (dom.cameraVideo) dom.cameraVideo.srcObject = null;
  if (dom.cameraModal) dom.cameraModal.style.display = 'none';
}

function snapPhoto() {
  if (!state.cameraStream || !dom.cameraVideo) return;
  const canvas = dom.cameraCanvas;
  canvas.width = dom.cameraVideo.videoWidth || 640;
  canvas.height = dom.cameraVideo.videoHeight || 480;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(dom.cameraVideo, 0, 0, canvas.width, canvas.height);
  const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
  setAttachedImage(dataUrl);
  stopCamera();
}

if (dom.cameraBtn) dom.cameraBtn.addEventListener('click', startCamera);
if (dom.closeCameraBtn) dom.closeCameraBtn.addEventListener('click', stopCamera);
if (dom.snapPhotoBtn) dom.snapPhotoBtn.addEventListener('click', snapPhoto);

if (dom.switchCameraBtn) {
  dom.switchCameraBtn.addEventListener('click', () => {
    state.facingMode = state.facingMode === 'user' ? 'environment' : 'user';
    startCamera();
  });
}

if (dom.modalUploadBtn) {
  dom.modalUploadBtn.addEventListener('click', () => {
    stopCamera();
    dom.fileUploadInput.click();
  });
}

// ─── Microphone Voice Recognition ───────────────────
function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    showToast('⚠️ Voice recognition not supported on this browser', 'error');
    return null;
  }

  const recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = 'en-US';

  recognition.onstart = () => {
    state.isRecording = true;
    if (dom.micBtn) dom.micBtn.classList.add('recording');
    if (dom.voiceListeningBar) dom.voiceListeningBar.style.display = 'flex';
    showToast('🎙️ Listening... Speak now', 'success');
  };

  recognition.onresult = (event) => {
    let transcript = '';
    for (let i = 0; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript;
    }
    dom.messageInput.value = transcript;
    dom.messageInput.dispatchEvent(new Event('input'));
  };

  recognition.onerror = (event) => {
    console.warn('Speech recognition error:', event.error);
    stopRecording();
    if (event.error === 'not-allowed') {
      showToast('❌ Microphone permission denied', 'error');
    }
  };

  recognition.onend = () => {
    stopRecording();
  };

  return recognition;
}

function startRecording() {
  if (!state.recognition) {
    state.recognition = initSpeechRecognition();
  }
  if (state.recognition) {
    try {
      state.recognition.start();
    } catch (e) {
      console.warn('Recognition already started:', e);
    }
  }
}

function stopRecording() {
  state.isRecording = false;
  if (dom.micBtn) dom.micBtn.classList.remove('recording');
  if (dom.voiceListeningBar) dom.voiceListeningBar.style.display = 'none';
  if (state.recognition) {
    try {
      state.recognition.stop();
    } catch (e) {}
  }
}

if (dom.micBtn) {
  dom.micBtn.addEventListener('click', () => {
    if (state.isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  });
}

if (dom.voiceStopBtn) {
  dom.voiceStopBtn.addEventListener('click', stopRecording);
}

// ─── Text-to-Speech (Speaker 🔊) ────────────────────
window.speakMsg = function(id) {
  const b = document.getElementById(`bubble-${id}`);
  if (!b) return;
  const text = b.innerText;

  if (!window.speechSynthesis) {
    showToast('⚠️ Speech Synthesis not supported', 'error');
    return;
  }

  if (state.currentlySpeakingId === id) {
    window.speechSynthesis.cancel();
    state.currentlySpeakingId = null;
    const btn = document.getElementById(`tts-btn-${id}`);
    if (btn) btn.innerHTML = '<i class="fa-solid fa-volume-high"></i> Listen';
    return;
  }

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1.0;
  utterance.pitch = 1.0;

  utterance.onstart = () => {
    state.currentlySpeakingId = id;
    const btn = document.getElementById(`tts-btn-${id}`);
    if (btn) btn.innerHTML = '<i class="fa-solid fa-stop text-danger"></i> Stop';
  };

  utterance.onend = () => {
    state.currentlySpeakingId = null;
    const btn = document.getElementById(`tts-btn-${id}`);
    if (btn) btn.innerHTML = '<i class="fa-solid fa-volume-high"></i> Listen';
  };

  window.speechSynthesis.speak(utterance);
};

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
  if (last.image) setAttachedImage(last.image);
  sendMessage();
};

// ─── New Chat ────────────────────────────────────────
function newChat() {
  state.messages = []; state.messageCounter = 0;
  dom.messagesList.innerHTML = '';
  const ws = dom.welcomeScreen;
  ws.style.display = ''; ws.style.opacity = '1'; ws.style.transform = '';
  dom.messageInput.value = ''; dom.charCount.textContent = '0 / 8000';
  removeAttachedImage();
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
  dom.sendBtn.disabled = (!dom.messageInput.value.trim() && !state.attachedImage) || state.isLoading;
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
let dark = false;
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
  const colors = ['rgba(12,108,99,', 'rgba(20,184,166,', 'rgba(14,165,233,'];
  const particles = Array.from({ length: 40 }, () => ({
    x: Math.random() * W, y: Math.random() * H,
    r: Math.random() * 1.5 + 0.3,
    vx: (Math.random() - 0.5) * 0.3, vy: (Math.random() - 0.5) * 0.3,
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
        if (d < 110) {
          ctx.beginPath(); ctx.moveTo(particles[i].x, particles[i].y); ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(12,108,99,${0.08*(1-d/110)})`; ctx.lineWidth = 0.5; ctx.stroke();
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
  if (e.key === 'Escape') { closeSidebar(); stopCamera(); }
});

// ─── Init ─────────────────────────────────────────────
dom.messageInput.focus();

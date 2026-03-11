// ── CONFIG ────────────────────────────────────────────────────────────────
const API_BASE = '';  // Same origin; update if running separately

// ── TOAST ─────────────────────────────────────────────────────────────────
function showToast(message, type = 'default', duration = 3500) {
  const icons = { success: '✅', error: '❌', default: 'ℹ️' };
  const container = document.getElementById('toast-container') || (() => {
    const el = document.createElement('div');
    el.id = 'toast-container';
    document.body.appendChild(el);
    return el;
  })();

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = `${icons[type] || ''} ${message}`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), duration);
}

// ── LOADING ───────────────────────────────────────────────────────────────
function showLoader(containerId, message = 'Analyzing…') {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = `
    <div class="loader-wrap">
      <div class="spinner"></div>
      <p class="loader-text">${message}</p>
    </div>`;
}

function hideLoader(containerId) {
  const el = document.getElementById(containerId);
  if (el) el.innerHTML = '';
}

// ── API HELPERS ────────────────────────────────────────────────────────────
async function apiPost(endpoint, formData) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

async function apiGet(endpoint) {
  const res = await fetch(`${API_BASE}${endpoint}`);
  if (!res.ok) throw new Error('Request failed');
  return res.json();
}

async function apiDelete(endpoint) {
  const res = await fetch(`${API_BASE}${endpoint}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Request failed');
  return res.json();
}

// ── DATE FORMAT ────────────────────────────────────────────────────────────
function formatDate(isoStr) {
  if (!isoStr) return '—';
  const d = new Date(isoStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function timeAgo(isoStr) {
  const now = Date.now();
  const then = new Date(isoStr).getTime();
  const diff = Math.floor((now - then) / 1000);
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

// ── DRAG AND DROP ──────────────────────────────────────────────────────────
function initDropZone(zoneId, fileInputId, onFile) {
  const zone = document.getElementById(zoneId);
  if (!zone) return;

  zone.addEventListener('dragover', e => {
    e.preventDefault();
    zone.classList.add('dragover');
  });
  zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) onFile(file);
  });

  const input = document.getElementById(fileInputId);
  if (input) {
    input.addEventListener('change', () => {
      if (input.files[0]) onFile(input.files[0]);
    });
  }
}

// ── SPEAKER CHART ──────────────────────────────────────────────────────────
function renderSpeakerChart(stats, containerId) {
  const container = document.getElementById(containerId);
  if (!container || !stats || Object.keys(stats).length === 0) return;

  const colors = ['#4F46E5', '#818CF8', '#C7D2FE', '#A5B4FC', '#6366F1'];
  const entries = Object.entries(stats);

  container.innerHTML = `<ul class="speaker-list">
    ${entries.map(([name, pct], i) => `
      <li class="speaker-item">
        <span class="speaker-name">${name}</span>
        <div class="speaker-bar-wrap">
          <div class="speaker-bar" style="width:0%;background:${colors[i % colors.length]}" data-pct="${pct}"></div>
        </div>
        <span class="speaker-pct">${pct}%</span>
      </li>
    `).join('')}
  </ul>`;

  // Animate bars
  requestAnimationFrame(() => {
    container.querySelectorAll('.speaker-bar').forEach(bar => {
      bar.style.width = bar.dataset.pct + '%';
    });
  });
}

// ── RENDER RESULTS ─────────────────────────────────────────────────────────
function renderAnalysis(data, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const actionItems = data.action_items || [];
  const decisions = data.decisions || [];
  const speakerStats = data.speaker_stats || {};

  container.innerHTML = `
    <div class="results-grid fade-in">
      <!-- Summary -->
      <div class="result-card full">
        <div class="result-header">
          <span class="icon">📋</span>
          <h3>Meeting Summary</h3>
        </div>
        <p class="summary-text">${data.summary || 'No summary generated.'}</p>
      </div>

      <!-- Action Items -->
      <div class="result-card">
        <div class="result-header">
          <span class="icon">✅</span>
          <h3>Action Items</h3>
          <span class="tag tag-primary" style="margin-left:auto">${actionItems.length}</span>
        </div>
        ${actionItems.length ? actionItems.map(item => `
          <div class="action-item">
            <span class="action-owner">${item.owner}</span>
            <span class="action-task">${item.task}</span>
          </div>
        `).join('') : '<p style="color:var(--text-muted);font-size:.875rem">No action items detected.</p>'}
      </div>

      <!-- Decisions -->
      <div class="result-card">
        <div class="result-header">
          <span class="icon">⚡</span>
          <h3>Key Decisions</h3>
          <span class="tag tag-success" style="margin-left:auto">${decisions.length}</span>
        </div>
        ${decisions.length ? decisions.map(d => `
          <div class="decision-item">
            <span class="decision-bullet"></span>
            <span class="decision-text">${d}</span>
          </div>
        `).join('') : '<p style="color:var(--text-muted);font-size:.875rem">No key decisions detected.</p>'}
      </div>

      <!-- Speaker Insights -->
      <div class="result-card full">
        <div class="result-header">
          <span class="icon">🎤</span>
          <h3>Speaker Insights</h3>
        </div>
        <div id="speaker-chart-render"></div>
      </div>
    </div>
  `;

  renderSpeakerChart(speakerStats, 'speaker-chart-render');
}

// ── EXPORT ─────────────────────────────────────────────────────────────────
function exportMeeting(meetingId, format) {
  window.open(`${API_BASE}/export/${meetingId}/${format}`, '_blank');
}

// ── SESSION STORAGE HELPER ──────────────────────────────────────────────────
function saveAnalysisToSession(data) {
  sessionStorage.setItem('clairo_last_analysis', JSON.stringify(data));
}

function loadAnalysisFromSession() {
  try {
    return JSON.parse(sessionStorage.getItem('clairo_last_analysis') || 'null');
  } catch { return null; }
}

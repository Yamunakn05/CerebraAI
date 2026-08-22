// ============================================================
// app.js — SPA Router, Landing Page, Auth Modal, Global State
// ============================================================

const App = {
  currentPage: null,
  user: null,
  uploadedImage: null,
  analysisResult: null,
  uploadVersion: 0,
  uploadSequence: 0,
  analysisVersion: 0,
  uploadAbortController: null,
  analysisAbortController: null,
  chatHistory: [],

  async init() {
    await this.checkSession();
    this._initSidebar();
    this._initMobileNav();

    if (this.user) {
      this._showApp();
      const currentHash = location.hash.replace('#', '');
      const initialPage = currentHash || 'dashboard';
      this.navigate(initialPage);
    } else {
      this._showLanding();
      renderLandingPage();
    }

    window.addEventListener('hashchange', () => {
      if (!this.user) return;
      const page = location.hash.replace('#', '') || 'dashboard';
      this.navigate(page);
    });
  },

  async checkSession() {
    try {
      const res = await api('/api/auth/me');
      this.user = res.user || null;
    } catch { this.user = null; }
  },

  navigate(page) {
    this.currentPage = page;
    location.hash = page;
    this._updateNav(page);
    this._renderPage(page);
  },

  _renderPage(page) {
    const role = (this.user?.role || 'patient').toLowerCase();
    const roleNavs = {
      patient: ['dashboard', 'upload', 'analysis', 'chatbot', 'medicine', 'emergency'],
      doctor: ['dashboard', 'analysis', 'chatbot', 'medicine', 'emergency'],
      radiologist: ['dashboard', 'analysis', 'chatbot', 'emergency'],
      receptionist: ['dashboard', 'emergency'],
      admin: ['dashboard', 'upload', 'analysis', 'chatbot', 'medicine', 'emergency'],
    };
    const allowedPages = roleNavs[role] || roleNavs['patient'];

    const container = document.getElementById('page-container');
    container.innerHTML = '';
    container.className = 'animate-in';
    void container.offsetWidth;

    if (!allowedPages.includes(page)) {
      container.innerHTML = `
        <div class="page-header"><h1>🔒 Feature Restricted</h1></div>
        <div class="glass-card" style="text-align:center;padding:40px">
          <div style="font-size:3.5rem;margin-bottom:12px">🚫</div>
          <h2 style="color:var(--red);margin-bottom:8px">Access Restricted for ${role.charAt(0).toUpperCase() + role.slice(1)}</h2>
          <p style="color:var(--text-dim);margin-bottom:20px">The <strong style="color:var(--text-primary)">${page.toUpperCase()}</strong> workspace is not enabled for your account role.</p>
          <button class="btn btn-primary" onclick="App.navigate('dashboard')">📊 Return to Dashboard</button>
        </div>
      `;
      return;
    }

    const pages = {
      upload: () => renderUploadPage(container),
      analysis: () => renderAnalysisPage(container),
      dashboard: () => renderDashboardPage(container),
      chatbot: () => renderChatbotPage(container),
      medicine: () => renderMedicinePage(container),
      emergency: () => renderEmergencyPage(container),
    };
    const fn = pages[page] || pages['dashboard'];
    fn();
  },

  _updateNav(page) {
    document.querySelectorAll('.nav-item').forEach(el => {
      el.classList.toggle('active', el.dataset.page === page);
    });
  },

  _showApp() {
    document.getElementById('app').classList.remove('hidden');
    document.getElementById('landing-screen').classList.add('hidden');
    closeAuthModal();
    this._updateUserSidebar();
  },

  _showLanding() {
    document.getElementById('app').classList.add('hidden');
    document.getElementById('landing-screen').classList.remove('hidden');
  },

  _updateUserSidebar() {
    if (!this.user) return;
    const role = (this.user.role || 'patient').toLowerCase();
    const name = this.user.full_name || this.user.username || 'User';
    document.getElementById('sidebar-username').textContent = name;
    document.getElementById('sidebar-role').textContent = role.charAt(0).toUpperCase() + role.slice(1);
    document.getElementById('user-avatar').textContent = name.charAt(0).toUpperCase();

    const roleNavs = {
      patient: ['dashboard', 'upload', 'analysis', 'chatbot', 'medicine', 'emergency'],
      doctor: ['dashboard', 'analysis', 'chatbot', 'medicine', 'emergency'],
      radiologist: ['dashboard', 'analysis', 'chatbot', 'emergency'],
      receptionist: ['dashboard', 'emergency'],
      admin: ['dashboard', 'upload', 'analysis', 'chatbot', 'medicine', 'emergency'],
    };
    const allowedPages = roleNavs[role] || roleNavs['patient'];

    document.querySelectorAll('.nav-item').forEach(el => {
      const p = el.dataset.page;
      if (allowedPages.includes(p)) {
        el.style.display = 'flex';
      } else {
        el.style.display = 'none';
      }
    });
  },

  _initSidebar() {
    document.querySelectorAll('.nav-item').forEach(el => {
      el.addEventListener('click', e => {
        e.preventDefault();
        this.navigate(el.dataset.page);
        document.getElementById('sidebar').classList.remove('open');
      });
    });

    document.getElementById('logout-btn').addEventListener('click', async () => {
      showLoader('Signing out...');
      await api('/api/auth/logout', { method: 'POST' });
      App.user = null;
      App.uploadedImage = null;
      App.analysisResult = null;
      App.uploadVersion++;
      App.analysisVersion++;
      App.uploadAbortController?.abort();
      App.analysisAbortController?.abort();
      App.chatHistory = [];
      hideLoader();
      location.hash = '';
      this._showLanding();
      renderLandingPage();
    });
  },

  _initMobileNav() {
    const hamburger = document.getElementById('hamburger');
    const sidebar = document.getElementById('sidebar');
    if (!hamburger) return;
    hamburger.addEventListener('click', () => sidebar.classList.toggle('open'));
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay hidden';
    document.body.appendChild(overlay);
    overlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.classList.add('hidden');
    });
    sidebar.addEventListener('transitionend', () => {
      overlay.classList.toggle('hidden', !sidebar.classList.contains('open'));
    });
  },

  setUser(user) {
    // Login can replace an existing session without a full page refresh.
    // Never carry an MRI, report, or conversation into another account.
    if (this.user?.user_id !== user?.user_id) {
      this.uploadVersion++;
      this.analysisVersion++;
      this.uploadAbortController?.abort();
      this.analysisAbortController?.abort();
      this.uploadedImage = null;
      this.analysisResult = null;
      this.chatHistory = [];
    }
    this.user = user;
    this._updateUserSidebar();
    this._showApp();
    this.navigate('upload');
  },
};

// ── API helper ────────────────────────────────────────────────
async function api(url, options = {}) {
  const defaults = {
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
  };
  if (options.body && typeof options.body !== 'string' && !(options.body instanceof FormData)) {
    options.body = JSON.stringify(options.body);
  }
  if (options.body instanceof FormData) {
    delete defaults.headers['Content-Type'];
  }
  const res = await fetch(url, { ...defaults, ...options, headers: { ...defaults.headers, ...options.headers } });
  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json')) {
    return res.json();
  }
  return res;
}

// ── Toast ─────────────────────────────────────────────────────
function toast(msg, type = 'info', duration = 3500) {
  const container = document.getElementById('toast-container');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  container.appendChild(el);
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transform = 'translateX(60px)';
    el.style.transition = '0.3s ease';
    setTimeout(() => el.remove(), 300);
  }, duration);
}

// ── Loader ────────────────────────────────────────────────────
function showLoader(msg = 'Loading...') {
  document.getElementById('loader-text').textContent = msg;
  document.getElementById('global-loader').classList.remove('hidden');
}
function hideLoader() {
  document.getElementById('global-loader').classList.add('hidden');
}

// ── Auth Modal control ────────────────────────────────────────
function openAuthModal(tab = 'login') {
  renderAuthPage(tab);
  document.getElementById('auth-modal').classList.remove('hidden');
}
function closeAuthModal() {
  const modal = document.getElementById('auth-modal');
  if (modal) modal.classList.add('hidden');
}

// ── Markdown mini-renderer ────────────────────────────────────
function renderMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/```[\w]*\n([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/^\s*[-*] (.+)/gm, '<li>$1</li>')
    .replace(/(<li>[\s\S]*?<\/li>)/g, '<ul>$1</ul>')
    .replace(/<\/ul>\s*<ul>/g, '')
    .replace(/^\|(.+)\|$/gm, row => {
      const cells = row.split('|').slice(1, -1).map(c => c.trim());
      return '<tr>' + cells.map(c => `<td>${c}</td>`).join('') + '</tr>';
    })
    .replace(/\n/g, '<br>');
}

// ── Severity color helper ───────────────────────────────
function severityColor(level) {
  const m = { Mild: '#22c55e', Low: '#22c55e', Moderate: '#eab308', Severe: '#f97316', High: '#f97316', Critical: '#ef4444', 'No Tumor': '#38bdf8', None: '#38bdf8' };
  return m[level] || '#94a3b8';
}

// ── HTML escape (global utility) ───────────────────────────
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ── Init ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => App.init());

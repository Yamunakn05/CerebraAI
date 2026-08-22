// ============================================================
// auth.js — CerebraAI Landing Page + Auth Modal & One-Click Demo
// ============================================================

function renderLandingPage() {
  const container = document.getElementById('landing-screen');
  if (!container) return;

  container.innerHTML = `
    <!-- Top Navbar -->
    <header class="landing-navbar">
      <div class="landing-logo">
        <span class="logo-icon">🧠</span>
        <div>
          <div class="logo-name">CerebraAI</div>
          <div class="logo-sub" style="font-size:0.68rem;color:var(--accent)">Clinical AI System v2.1</div>
        </div>
      </div>

      <nav class="landing-nav-links">
        <a href="#overview">Overview</a>
        <a href="#features">AI Capabilities</a>
        <a href="#portals">Hospital Portals</a>
        <a href="#emergency">Emergency</a>
      </nav>

      <div class="landing-nav-actions">
        <button class="btn btn-secondary btn-sm" onclick="openAuthModal('login')">🔑 Sign In</button>
        <button class="btn btn-primary btn-sm" onclick="openAuthModal('register')">🚀 Get Started</button>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="landing-hero" id="overview">
      <div class="hero-badge">✨ Clinical Decision Support System</div>
      <h1 class="hero-title">
        Advanced Deep Learning Brain Tumor Diagnostic System & Clinical Workspace Platform
      </h1>
      <p class="hero-subtitle">
        Multi-Class Brain Tumor Detection, Explainable AI Visualization (Grad-CAM), 3D Surface Reconstruction, and Integrated Role-Aware Medical Management.
      </p>

      <div class="hero-cta-group">
        <button class="btn btn-primary btn-lg" onclick="openAuthModal('login')">
          🚀 Launch AI Diagnostics
        </button>
        <button class="btn btn-secondary btn-lg" onclick="openAuthModal('register')">
          📝 Create Account
        </button>
      </div>

      <!-- Quick Demo Login Bar -->
      <div class="demo-quick-bar">
        <span class="demo-label">⚡ One-Click Demo Access:</span>
        <button class="demo-chip" onclick="quickDemoLogin('doctor')">👨‍⚕️ Doctor</button>
        <button class="demo-chip" onclick="quickDemoLogin('patient')">👤 Patient</button>
        <button class="demo-chip" onclick="quickDemoLogin('radiologist')">🧪 Radiologist</button>
        <button class="demo-chip" onclick="quickDemoLogin('receptionist')">🧾 Receptionist</button>
        <button class="demo-chip" onclick="quickDemoLogin('admin')">🛠️ Admin</button>
      </div>

      <!-- Hero Stats -->
      <div class="hero-stats-grid">
        <div class="hero-stat-card">
          <div class="hero-stat-icon">🎯</div>
          <div class="hero-stat-val">98.4%</div>
          <div class="hero-stat-lbl">Diagnostic Accuracy</div>
        </div>
        <div class="hero-stat-card">
          <div class="hero-stat-icon">🧠</div>
          <div class="hero-stat-val">4 Classes</div>
          <div class="hero-stat-lbl">Glioma, Meningioma, Pituitary & Normal</div>
        </div>
        <div class="hero-stat-card">
          <div class="hero-stat-icon">🔥</div>
          <div class="hero-stat-val">Grad-CAM</div>
          <div class="hero-stat-lbl">Explainable AI Heatmaps</div>
        </div>
        <div class="hero-stat-card">
          <div class="hero-stat-icon">🏥</div>
          <div class="hero-stat-val">5 Portals</div>
          <div class="hero-stat-lbl">Role-Aware Hospital Workflows</div>
        </div>
      </div>
    </section>

    <!-- AI Features Section -->
    <section class="landing-section" id="features">
      <div class="section-header">
        <h2>🔬 Core AI & Clinical Capabilities</h2>
        <p>Comprehensive diagnostic intelligence pipeline from MRI upload to multi-lingual voice & PDF reports.</p>
      </div>

      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">🧠</div>
          <h3>Multi-Class Deep Learning Classification</h3>
          <p>Convolutional Neural Network distinguishing Glioma, Meningioma, Pituitary Adenoma, and Healthy Brain scans with confidence charts.</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">🔥</div>
          <h3>Explainable AI (Grad-CAM Heatmaps)</h3>
          <p>Visual attention heatmaps rendering exact spatial regions influencing the deep neural network's diagnostic output.</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">✂️</div>
          <h3>Lesion Segmentation & Millimeter Metrics</h3>
          <p>Pixel-accurate contour extraction, percentage area calculation, and physical width/height estimations.</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">🗺️</div>
          <h3>Anatomical Brain Region Mapping</h3>
          <p>Localization to Frontal, Temporal, Parietal, Occipital, Cerebellum, or Brain Stem with surgical accessibility ratings.</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">🚨</div>
          <h3>Severity Gauge & Clinical Protocols</h3>
          <p>Automated 0–100 severity index with tumor-specific clinical recommendations (Resection, Radiation, Chemotherapy).</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">🌐</div>
          <h3>Interactive 3D Surface Reconstruction</h3>
          <p>3D depth mesh view rendering MRI tissue intensity elevation with highlighted tumor geometry.</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">🎯</div>
          <h3>Surgical Risk Vector & Density Map</h3>
          <p>Magma tissue density heatmap with mass-effect pressure vectors and customizable threshold sliders.</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">📄</div>
          <h3>PDF, Voice TTS & QR Reports</h3>
          <p>One-click PDF reports, multi-lingual voice synthesis reports (English, Hindi, Kannada, Tamil), and mobile QR cards.</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">💊</div>
          <h3>Medicine Intelligence Center</h3>
          <p>Pharmaceutical lookup, side effect profiles, safety parameters, AI Q&A, and direct online pharmacy links.</p>
        </div>
      </div>
    </section>

    <!-- Role Portals Section -->
    <section class="landing-section" id="portals">
      <div class="section-header">
        <h2>🏥 Role-Aware Hospital Workflows</h2>
        <p>Tailored environments for every healthcare role in the clinical ecosystem.</p>
      </div>

      <div class="roles-grid">
        <div class="role-portal-card doctor">
          <div class="role-portal-icon">👨‍⚕️</div>
          <h3>Doctor Portal</h3>
          <p>Review patient MRI scans, verify severity scores, approve referrals, and manage appointments.</p>
          <button class="btn btn-sm btn-primary" onclick="quickDemoLogin('doctor')">Launch Doctor Portal →</button>
        </div>

        <div class="role-portal-card patient">
          <div class="role-portal-icon">👤</div>
          <h3>Patient Portal</h3>
          <p>View diagnostic history, download PDF & Audio reports, track prescriptions, and consult NeuroBot.</p>
          <button class="btn btn-sm btn-primary" onclick="quickDemoLogin('patient')">Launch Patient Portal →</button>
        </div>

        <div class="role-portal-card radiologist">
          <div class="role-portal-icon">🧪</div>
          <h3>Radiologist Portal</h3>
          <p>Inspect incoming scans, perform DICOM image quality validation, and route scans to specialists.</p>
          <button class="btn btn-sm btn-primary" onclick="quickDemoLogin('radiologist')">Launch Radiologist Portal →</button>
        </div>

        <div class="role-portal-card receptionist">
          <div class="role-portal-icon">🧾</div>
          <h3>Reception Desk</h3>
          <p>Schedule appointments, check doctor availability, and manage queue approvals.</p>
          <button class="btn btn-sm btn-primary" onclick="quickDemoLogin('receptionist')">Launch Reception Desk →</button>
        </div>

        <div class="role-portal-card admin">
          <div class="role-portal-icon">🛠️</div>
          <h3>Hospital Admin</h3>
          <p>Monitor platform stats, audit security logs, manage user directories, and hospital profiles.</p>
          <button class="btn btn-sm btn-primary" onclick="quickDemoLogin('admin')">Launch Admin Portal →</button>
        </div>
      </div>
    </section>
  `;
}

function renderAuthPage(defaultTab = 'login') {
  const screen = document.getElementById('auth-screen');
  screen.innerHTML = `
    <div class="auth-card animate-in">
      <div class="auth-header">
        <div class="auth-logo">
          <div class="auth-logo-icon">🧠</div>
          <div>
            <h1>CerebraAI</h1>
            <p>Advanced Deep Learning Brain Tumor Diagnostic System & Clinical Workspace Platform</p>
          </div>
        </div>

        <div class="auth-tabs">
          <button class="auth-tab ${defaultTab === 'login' ? 'active' : ''}" id="tab-login" onclick="switchAuthTab('login')">🔑 Login</button>
          <button class="auth-tab ${defaultTab === 'register' ? 'active' : ''}" id="tab-register" onclick="switchAuthTab('register')">📝 Register</button>
        </div>
      </div>

      <div class="auth-body">
        <!-- Login Form -->
        <div id="login-pane" class="${defaultTab === 'login' ? '' : 'hidden'}">
          <div class="form-group">
            <label class="form-label">Email Address</label>
            <input class="form-input" type="email" id="login-email" placeholder="your@email.com" autocomplete="email" />
          </div>
          <div class="form-group">
            <label class="form-label">Password</label>
            <input class="form-input" type="password" id="login-password" placeholder="••••••••" autocomplete="current-password" />
          </div>
          <div id="login-error" class="alert alert-error hidden" style="margin-bottom:14px"></div>
          <button class="btn btn-primary btn-full btn-lg" id="login-btn" onclick="doLogin()">
            🚀 Sign In
          </button>
          
          <!-- One-click Demo Account Bar -->
          <div style="margin-top:18px;text-align:center;border-top:1px solid var(--border);padding-top:14px">
            <p style="font-size:0.75rem;color:var(--text-dim);margin-bottom:10px;text-transform:uppercase;font-weight:700">Instant Demo Login</p>
            <div style="display:flex;gap:6px;flex-wrap:wrap;justify-content:center">
              <button class="demo-chip" onclick="quickDemoLogin('doctor')">👨‍⚕️ Doctor</button>
              <button class="demo-chip" onclick="quickDemoLogin('patient')">👤 Patient</button>
              <button class="demo-chip" onclick="quickDemoLogin('radiologist')">🧪 Radiologist</button>
              <button class="demo-chip" onclick="quickDemoLogin('receptionist')">🧾 Receptionist</button>
              <button class="demo-chip" onclick="quickDemoLogin('admin')">🛠️ Admin</button>
            </div>
          </div>
        </div>

        <!-- Register Form -->
        <div id="register-pane" class="${defaultTab === 'register' ? '' : 'hidden'}">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Account Type</label>
              <select class="form-select" id="reg-role" onchange="onRoleChange()">
                <option value="patient">Patient</option>
                <option value="doctor">Doctor</option>
                <option value="admin">Admin</option>
                <option value="receptionist">Receptionist</option>
                <option value="radiologist">Radiologist</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Full Name</label>
              <input class="form-input" id="reg-name" type="text" placeholder="John Doe" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Username</label>
              <input class="form-input" id="reg-username" type="text" placeholder="johndoe" />
            </div>
            <div class="form-group">
              <label class="form-label">Email</label>
              <input class="form-input" id="reg-email" type="email" placeholder="your@email.com" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Age</label>
              <input class="form-input" id="reg-age" type="number" value="30" min="1" max="120" />
            </div>
            <div class="form-group">
              <label class="form-label">Gender</label>
              <select class="form-select" id="reg-gender">
                <option>Prefer not to say</option>
                <option>Male</option>
                <option>Female</option>
                <option>Other</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Phone (optional)</label>
            <input class="form-input" id="reg-phone" type="tel" placeholder="+91 98765 43210" />
          </div>

          <!-- Patient-only fields -->
          <div id="patient-fields" class="patient-medical-card">
            <div class="medical-card-title">🩺 Medical Details</div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Weight (kg)</label>
                <input class="form-input" id="reg-weight" type="number" value="70" min="1" max="250" step="0.1" />
              </div>
              <div class="form-group">
                <label class="form-label">Blood Group</label>
                <select class="form-select" id="reg-blood">
                  <option>O+</option><option>O-</option><option>A+</option><option>A-</option>
                  <option>B+</option><option>B-</option><option>AB+</option><option>AB-</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Allergies / Drug Sensitivities</label>
              <textarea class="form-textarea" id="reg-allergies" rows="2" placeholder="e.g., Penicillin, Peanuts, None">None</textarea>
            </div>
            <div class="form-group">
              <label class="form-label">Past Surgeries / Medical Conditions</label>
              <textarea class="form-textarea" id="reg-surgeries" rows="2" placeholder="e.g., Appendectomy 2018, None">None</textarea>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Password</label>
              <input class="form-input" id="reg-pass" type="password" placeholder="Min 6 characters" />
            </div>
            <div class="form-group">
              <label class="form-label">Confirm Password</label>
              <input class="form-input" id="reg-pass2" type="password" placeholder="Repeat password" />
            </div>
          </div>
          <div id="reg-error" class="alert alert-error hidden" style="margin-bottom:14px"></div>
          <button class="btn btn-primary btn-full btn-lg" onclick="doRegister()">
            ✅ Create Account
          </button>
        </div>
      </div>
    </div>
  `;

  screen.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      if (!document.getElementById('login-pane').classList.contains('hidden')) doLogin();
      else doRegister();
    }
  });
}

function switchAuthTab(tab) {
  document.getElementById('tab-login').classList.toggle('active', tab === 'login');
  document.getElementById('tab-register').classList.toggle('active', tab === 'register');
  document.getElementById('login-pane').classList.toggle('hidden', tab !== 'login');
  document.getElementById('register-pane').classList.toggle('hidden', tab !== 'register');
}

function onRoleChange() {
  const role = document.getElementById('reg-role').value;
  const pf = document.getElementById('patient-fields');
  pf.classList.toggle('hidden', role !== 'patient');
}

async function doLogin() {
  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  const errEl = document.getElementById('login-error');
  errEl.classList.add('hidden');

  if (!email || !password) {
    errEl.textContent = 'Please enter email and password.';
    errEl.classList.remove('hidden');
    return;
  }

  const btn = document.getElementById('login-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-sm"></span> Authenticating...';

  const res = await api('/api/auth/login', {
    method: 'POST',
    body: { email, password },
  });

  btn.disabled = false;
  btn.innerHTML = '🚀 Sign In';

  if (res.error) {
    errEl.textContent = res.error;
    errEl.classList.remove('hidden');
    return;
  }

  toast(`Welcome back, ${res.user.full_name || res.user.username}! 👋`, 'success');
  App.setUser(res.user);
}

async function doRegister() {
  const role = document.getElementById('reg-role').value;
  const name = document.getElementById('reg-name').value.trim();
  const username = document.getElementById('reg-username').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const age = parseInt(document.getElementById('reg-age').value) || 30;
  const gender = document.getElementById('reg-gender').value;
  const phone = document.getElementById('reg-phone').value.trim();
  const pass = document.getElementById('reg-pass').value;
  const pass2 = document.getElementById('reg-pass2').value;
  const errEl = document.getElementById('reg-error');
  errEl.classList.add('hidden');

  if (!name || !username || !email || !pass) {
    errEl.textContent = 'Please fill in all required fields.';
    errEl.classList.remove('hidden');
    return;
  }
  if (pass !== pass2) {
    errEl.textContent = 'Passwords do not match.';
    errEl.classList.remove('hidden');
    return;
  }
  if (pass.length < 6) {
    errEl.textContent = 'Password must be at least 6 characters.';
    errEl.classList.remove('hidden');
    return;
  }

  const body = { username, email, password: pass, full_name: name, role, age, gender, phone };
  if (role === 'patient') {
    body.weight = parseFloat(document.getElementById('reg-weight').value) || 70;
    body.blood_group = document.getElementById('reg-blood').value;
    body.allergies = document.getElementById('reg-allergies').value;
    body.surgeries = document.getElementById('reg-surgeries').value;
  }

  showLoader('Creating account...');
  const res = await api('/api/auth/register', { method: 'POST', body });
  hideLoader();

  if (res.error) {
    errEl.textContent = res.error;
    errEl.classList.remove('hidden');
    return;
  }
  toast('🎉 Account created! Please sign in.', 'success');
  switchAuthTab('login');
}

async function quickDemoLogin(role) {
  const demoAccounts = {
    admin: { email: 'admin@cerebraai.com', pass: 'admin123' },
    doctor: { email: 'doctor@cerebraai.com', pass: 'doctor123' },
    patient: { email: 'patient@cerebraai.com', pass: 'patient123' },
    radiologist: { email: 'radiologist@cerebraai.com', pass: 'radio123' },
    receptionist: { email: 'receptionist@cerebraai.com', pass: 'recep123' },
  };

  const cred = demoAccounts[role] || demoAccounts['patient'];
  showLoader(`Signing in as demo ${role}...`);

  const res = await api('/api/auth/login', {
    method: 'POST',
    body: { email: cred.email, password: cred.pass },
  });
  hideLoader();

  if (res.error) {
    // Demo accounts are seeded asynchronously on server start.
    // If not yet available, show info and retry after 2 seconds.
    toast(`⏳ Demo account is being set up… please try again in a moment.`, 'info', 4000);
    return;
  }

  toast(`👋 Welcome! Signed in as ${role.toUpperCase()} demo user.`, 'success');
  App.setUser(res.user);
}

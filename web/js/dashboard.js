// ============================================================
// dashboard.js — Role-Based Dashboard
// ============================================================

async function renderDashboardPage(container) {
  container.innerHTML = `
    <div class="page-header"><h1>📊 Dashboard</h1><p>Loading your personalized dashboard...</p></div>
    <div class="glass-card" style="text-align:center;padding:40px">
      <div class="loader-spinner" style="margin:0 auto 16px"></div>
      <p style="color:var(--text-muted)">Fetching dashboard data...</p>
    </div>
  `;

  const data = await api('/api/dashboard');
  if (data.error) {
    container.innerHTML = `<div class="alert alert-error">${data.error}</div>`;
    return;
  }

  const role  = data.role?.toLowerCase() || 'patient';
  const user  = data.user || App.user || {};
  const name  = user.full_name || user.username || 'User';

  const ROLE_META = {
    patient:      { emoji: '👤',    label: 'Patient Health Overview',  accent: '#22c55e' },
    doctor:       { emoji: '👨‍⚕️', label: 'Doctor Dashboard',        accent: '#38bdf8' },
    admin:        { emoji: '🛠️',   label: 'Hospital Administration',   accent: '#f59e0b' },
    receptionist: { emoji: '🧾',   label: 'Reception Desk',            accent: '#8b5cf6' },
    radiologist:  { emoji: '🧪',   label: 'Radiology Review',          accent: '#14b8a6' },
  };
  const meta = ROLE_META[role] || { emoji: '👤', label: 'Dashboard', accent: '#38bdf8' };

  container.innerHTML = `
    <div class="role-header animate-in">
      <div class="role-emoji">${meta.emoji}</div>
      <div>
        <div class="role-title">${meta.label}</div>
        <div class="role-sub">CerebraAI Diagnostic System</div>
      </div>
      <div style="margin-left:auto;text-align:right">
        <div style="font-size:.9rem;font-weight:700">${name}</div>
        <div style="font-size:.7rem;color:${meta.accent};font-weight:700;text-transform:uppercase;letter-spacing:.08em">
          <span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:${meta.accent};margin-right:4px;box-shadow:0 0 8px ${meta.accent}"></span>
          ${role.charAt(0).toUpperCase()+role.slice(1)}
        </div>
      </div>
    </div>
    <div id="dashboard-body"></div>
  `;

  const body = document.getElementById('dashboard-body');
  const renders = { patient: _renderPatientDash, doctor: _renderDoctorDash, admin: _renderAdminDash, receptionist: _renderReceptionistDash, radiologist: _renderRadiologistDash };
  const fn = renders[role] || _renderPatientDash;
  fn(body, data);
}

function _statCard(icon, label, value, color = 'var(--accent)') {
  return `
    <div class="stat-card animate-in">
      <div class="stat-icon">${icon}</div>
      <div class="stat-value" style="color:${color}">${value}</div>
      <div class="stat-label">${label}</div>
    </div>
  `;
}

// ── Patient Dashboard ─────────────────────────────────────────
function _renderPatientDash(el, data) {
  let scans  = data.scans || [];
  const appts  = data.appointments || [];
  const doctors = data.doctors || [];
  const assignedDoc = data.assigned_doctor || null;

  // Fallback to session analysis result if scan list is empty
  if (!scans.length && App.analysisResult) {
    const ar = App.analysisResult;
    scans = [{
      scan_id: ar.upload_id || 'session-scan',
      scan_date: new Date().toISOString(),
      filename: ar.filename || 'Recent_Scan.png',
      tumor_type: ar.display_label || ar.label || 'Tumor',
      confidence: ar.confidence || 0,
      brain_region: ar.brain_region || 'Brain',
      severity_level: ar.severity_level || 'Moderate',
      status: 'Pending Doctor Review',
    }];
  }

  const latest = scans[0];

  el.innerHTML = `
    <div class="grid-4" style="margin-bottom:24px">
      ${_statCard('📁', 'Total Scans',      scans.length,  'var(--green)')}
      ${_statCard('🔬', 'Latest Diagnosis', latest ? (latest.display_label || latest.tumor_type?.replace(/\b\w/g,c=>c.toUpperCase())) : 'No Scans', 'var(--accent)')}
      ${_statCard('📅', 'Appointments',     appts.length,  'var(--violet)')}
      ${_statCard('💊', 'Prescriptions',    (data.prescriptions||[]).length, 'var(--yellow)')}
    </div>

    <!-- Assigned Consulting Doctor Card -->
    <div class="glass-card" style="margin-bottom:20px;border-left:4px solid var(--accent)">
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
        <div>
          <div style="font-size:0.75rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:.06em;font-weight:700">👨‍⚕️ My Consulting Neurologist / Specialist</div>
          <div style="font-size:1.15rem;font-weight:800;color:var(--text-primary);margin-top:2px">
            ${assignedDoc ? (assignedDoc.full_name || assignedDoc.username) : '<span style="color:var(--text-muted)">No primary doctor assigned yet</span>'}
          </div>
          <div style="font-size:0.8rem;color:var(--text-muted)">
            ${assignedDoc ? `Email: ${assignedDoc.email} | Status: <span class="badge badge-green">Active Link</span>` : 'Select your doctor below so they can view and review your diagnostic MRI scans.'}
          </div>
        </div>
        <div style="display:flex;gap:8px;align-items:center">
          <select class="form-select" id="select-primary-doc" style="max-width:260px">
            <option value="">-- Choose Consulting Doctor --</option>
            ${doctors.map(d => `<option value="${d.user_id}" ${assignedDoc && assignedDoc.user_id === d.user_id ? 'selected' : ''}>${d.full_name || d.username}</option>`).join('')}
          </select>
          <button class="btn btn-sm btn-primary" onclick="assignConsultingDoctor()">🩺 Set Doctor</button>
        </div>
      </div>
    </div>

    <!-- Scan History -->
    <div class="glass-card" style="margin-bottom:20px">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
        <p style="font-weight:700;margin:0">📁 Patient Diagnostic History & MRI Scans</p>
        <button class="btn btn-sm btn-primary" onclick="App.navigate('upload')">📤 Upload New Scan</button>
      </div>
      ${scans.length ? `
        <table class="data-table">
          <thead><tr><th>Date</th><th>Filename</th><th>Diagnosis</th><th>Brain Region</th><th>Severity</th><th>Status</th><th>Report</th></tr></thead>
          <tbody>
            ${scans.map(s => `
              <tr>
                <td>${(s.scan_date||'').slice(0,10) || 'Today'}</td>
                <td><strong>${s.filename || 'MRI_Scan'}</strong></td>
                <td>${s.display_label || (s.tumor_type||'').replace(/\b\w/g,c=>c.toUpperCase()) || '—'} <span style="font-size:.75rem;color:var(--text-dim)">(${(s.confidence||0).toFixed(0)}%)</span></td>
                <td>🗺️ ${s.brain_region || '—'}</td>
                <td><span class="badge badge-${_sevBadge(s.severity_level)}">${s.severity_level || '—'}</span></td>
                <td><span class="badge badge-blue">${s.status || 'Pending Review'}</span></td>
                <td><a href="/api/reports/pdf" target="_blank" class="btn btn-sm btn-secondary">📄 PDF</a></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      ` : `<div class="alert alert-info">No scan records found in your medical history. <button class="btn btn-sm btn-primary" style="margin-left:10px" onclick="App.navigate('upload')">📤 Upload First MRI</button></div>`}
    </div>

    <!-- Appointment Booking & Appointments Grid -->
    <div class="grid-2" style="gap:18px;margin-bottom:20px">
      <!-- Book Appointment Form -->
      <div class="glass-card">
        <p style="font-weight:700;margin-bottom:14px;color:var(--accent)">📅 Book Doctor Appointment</p>
        <div class="form-group" style="margin-bottom:12px">
          <label class="form-label">Select Registered Doctor</label>
          <select class="form-select" id="book-doctor">
            ${doctors.length ? doctors.map(d => `<option value="${d.user_id}|${d.full_name || d.username}">${d.full_name || d.username}</option>`).join('') : '<option value="">No registered doctors available</option>'}
          </select>
        </div>
        <div class="grid-2" style="gap:10px;margin-bottom:12px">
          <div>
            <label class="form-label">Preferred Date</label>
            <input type="date" class="form-input" id="book-date" value="${new Date(Date.now()+86400000).toISOString().slice(0,10)}">
          </div>
          <div>
            <label class="form-label">Preferred Time</label>
            <select class="form-select" id="book-time">
              <option value="09:00 AM">09:00 AM</option>
              <option value="10:30 AM">10:30 AM</option>
              <option value="02:00 PM">02:00 PM</option>
              <option value="04:00 PM">04:00 PM</option>
            </select>
          </div>
        </div>
        <div class="form-group" style="margin-bottom:16px">
          <label class="form-label">Consultation Reason</label>
          <input type="text" class="form-input" id="book-reason" placeholder="e.g. Brain MRI scan review and treatment consultation" value="MRI Scan Review & Consultation">
        </div>
        <button class="btn btn-primary btn-full" onclick="bookAppointment()">📅 Confirm & Book Appointment</button>
      </div>

      <!-- My Appointments List -->
      <div class="glass-card">
        <p style="font-weight:700;margin-bottom:14px">📋 My Scheduled Appointments</p>
        ${appts.length ? `
          <table class="data-table">
            <thead><tr><th>Date</th><th>Time</th><th>Doctor</th><th>Reason</th><th>Status</th></tr></thead>
            <tbody>
              ${appts.map(a => `<tr>
                <td>${a.appointment_date||'—'}</td>
                <td>${a.appointment_time||'—'}</td>
                <td><strong>${a.doctor_name||'Doctor'}</strong></td>
                <td style="font-size:.78rem">${a.reason||'Consultation'}</td>
                <td><span class="badge badge-${a.status==='Approved'?'green':(a.status==='Rejected'?'red':'yellow')}">${a.status||'Pending'}</span></td>
              </tr>`).join('')}
            </tbody>
          </table>
        ` : `<div class="alert alert-info">No appointments scheduled yet. Use the form on the left to book a consultation with a neurologist.</div>`}
      </div>
    </div>

    <!-- Patient Prescriptions Section -->
    <div class="glass-card" style="margin-bottom:20px">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
        <div>
          <p style="font-weight:700;margin:0">💊 My Prescriptions & Clinical Regimen</p>
          <p style="font-size:0.75rem;color:var(--text-muted);margin:0">Prescriptions issued by your consulting neurologist after consultation review</p>
        </div>
        <span class="badge badge-yellow">Rx Medical Orders</span>
      </div>
      ${(data.prescriptions && data.prescriptions.length) ? `
        <table class="data-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Prescribing Doctor</th>
              <th>Diagnosis / Indication</th>
              <th>Medication & Dosage</th>
              <th>Frequency & Duration</th>
              <th>Clinical Instructions</th>
            </tr>
          </thead>
          <tbody>
            ${data.prescriptions.map(p => `
              <tr>
                <td>${(p.created_at||'').slice(0,10) || 'Recent'}</td>
                <td><strong>${p.doctor_name || 'Neurologist'}</strong></td>
                <td style="font-size:0.8rem;color:var(--accent)">${p.diagnosis || 'Clinical Consultation'}</td>
                <td><strong>💊 ${p.medicine_name || 'Medication'}</strong><br><span style="font-size:0.75rem;color:var(--text-muted)">Dosage: ${p.dosage || 'As directed'}</span></td>
                <td><span class="badge badge-cyan">${p.frequency || 'Twice Daily'}</span><br><span style="font-size:0.75rem;color:var(--text-dim)">Duration: ${p.duration || '14 Days'}</span></td>
                <td style="font-size:0.8rem;color:var(--text-muted)">${p.instructions || 'Follow physician directions.'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      ` : `
        <div class="alert alert-info">
          💊 <strong>No prescriptions issued yet.</strong><br>
          <span style="font-size:0.82rem;color:var(--text-muted)">Once your consulting neurologist completes your appointment or scan review, any prescribed medications (e.g. Temozolomide, Dexamethasone, Levetiracetam) and dosage instructions will appear here.</span>
        </div>
      `}
    </div>
  `;
}

// ── Doctor Dashboard ──────────────────────────────────────────
function _renderDoctorDash(el, data) {
  const stats        = data.stats || {};
  const patients     = data.assigned_patients || [];
  const scans        = data.all_scans || [];
  const appts        = data.all_appointments || [];
  const prescList    = data.prescriptions || [];

  el.innerHTML = `
    <div class="grid-4" style="margin-bottom:24px">
      ${_statCard('👥', 'My Patients',     stats.total_patients || patients.length, 'var(--green)')}
      ${_statCard('🔬', 'Patient Scans',   stats.total_scans || scans.length,       'var(--accent)')}
      ${_statCard('🚨', 'Critical Cases',  stats.critical_cases || 0,               'var(--red)')}
      ${_statCard('💊', 'Prescriptions',   prescList.length,                         'var(--yellow)')}
    </div>

    <!-- Assigned Patients List -->
    <div class="glass-card" style="margin-bottom:20px">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
        <div>
          <p style="font-weight:700;margin:0">👥 My Assigned Patients & Clinical Charts</p>
          <p style="font-size:0.75rem;color:var(--text-muted);margin:0">Patients who have selected you as their consulting specialist or scheduled consultations</p>
        </div>
        <span class="badge badge-green">🔒 Role-Isolated Medical View</span>
      </div>
      ${patients.length ? `
        <table class="data-table">
          <thead>
            <tr>
              <th>Patient Name</th>
              <th>Age / Gender</th>
              <th>Blood Group</th>
              <th>Allergies</th>
              <th>Surgeries / Conditions</th>
              <th>Scans</th>
              <th>Contact</th>
            </tr>
          </thead>
          <tbody>
            ${patients.map(p => `
              <tr>
                <td><strong>${p.full_name || p.username}</strong><br><span style="font-size:0.7rem;color:var(--text-dim)">ID: ${p.user_id}</span></td>
                <td>${p.age || '—'} / ${p.gender || '—'}</td>
                <td><span class="badge badge-cyan">${p.blood_group || 'O+'}</span></td>
                <td style="font-size:0.78rem;color:${p.allergies && p.allergies !== 'None' ? 'var(--red)' : 'var(--text-muted)'}">
                  ${p.allergies || 'None'}
                </td>
                <td style="font-size:0.78rem;color:var(--text-muted)">${p.surgeries || 'None'}</td>
                <td><span class="badge badge-blue">📁 ${p.scan_count || 0}</span></td>
                <td style="font-size:0.75rem;color:var(--text-dim)">${p.email || p.phone || '—'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      ` : `
        <div class="alert alert-info">
          📋 <strong>No patients have selected or booked consultations with you yet.</strong><br>
          <span style="font-size:0.82rem;color:var(--text-muted)">When a patient selects you as their consulting neurologist or books an appointment, their clinical chart and diagnostic MRI scans will automatically appear in this workspace.</span>
        </div>
      `}
    </div>

    <!-- Patient Diagnostic Scans for Doctor Review -->
    <div class="glass-card" style="margin-bottom:20px">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
        <p style="font-weight:700;margin:0">🔬 Diagnostic Scans for Review</p>
        <span class="badge badge-blue">👨‍⚕️ Clinical Diagnostic Review</span>
      </div>
      ${scans.length ? `
        <table class="data-table">
          <thead><tr><th>Date</th><th>Patient</th><th>Filename</th><th>Diagnosis</th><th>Region</th><th>Severity</th><th>Status</th><th>Review Action</th></tr></thead>
          <tbody>
            ${scans.map(s => `<tr>
              <td>${(s.scan_date||'').slice(0,10)||'Today'}</td>
              <td><strong>${s.patient_name||'Patient'}</strong></td>
              <td>${s.filename||'MRI_Scan'}</td>
              <td>${s.display_label || (s.tumor_type||'').replace(/\b\w/g,c=>c.toUpperCase())||'—'}</td>
              <td>🗺️ ${s.brain_region||'—'}</td>
              <td><span class="badge badge-${_sevBadge(s.severity_level)}">${s.severity_level||'—'}</span></td>
              <td style="font-size:.76rem;color:var(--text-muted)">${s.status||'Pending'}</td>
              <td>
                <select class="form-select" style="padding:4px 8px;font-size:.75rem" onchange="updateScanStatus('${s.scan_id}', this.value)">
                  <option value="Pending Doctor Review" ${s.status==='Pending Doctor Review'?'selected':''}>Pending Review</option>
                  <option value="Approved" ${s.status==='Approved'?'selected':''}>Approved ✅</option>
                  <option value="Rejected" ${s.status==='Rejected'?'selected':''}>Rejected ❌</option>
                  <option value="Requires Additional Tests" ${s.status==='Requires Additional Tests'?'selected':''}>More Tests 🧪</option>
                </select>
              </td>
            </tr>`).join('')}
          </tbody>
        </table>
      ` : `<p style="color:var(--text-dim);font-size:.85rem">No MRI scans from your assigned patients currently pending review.</p>`}
    </div>

    <!-- Doctor Appointments & Issue Prescription Grid -->
    <div class="grid-2" style="gap:18px;margin-bottom:20px">
      <!-- Doctor Appointments -->
      <div class="glass-card">
        <p style="font-weight:700;margin-bottom:14px">📅 Scheduled Consultations</p>
        ${appts.length ? `
          <table class="data-table">
            <thead><tr><th>Patient</th><th>Date</th><th>Time</th><th>Reason</th><th>Status</th><th>Action</th></tr></thead>
            <tbody>
              ${appts.map(a => `<tr>
                <td><strong>${a.patient_name||'Patient'}</strong></td>
                <td>${a.appointment_date||'—'}</td>
                <td>${a.appointment_time||'—'}</td>
                <td>${a.reason||'Consultation'}</td>
                <td><span class="badge badge-${a.status==='Approved'?'green':'yellow'}">${a.status||'Pending'}</span></td>
                <td>
                  ${a.status !== 'Approved' ? `<button class="btn btn-sm btn-success" onclick="approveAppt('${a.appointment_id}')">✅ Approve</button>` : '<span style="color:var(--green);font-size:.78rem">Approved</span>'}
                </td>
              </tr>`).join('')}
            </tbody>
          </table>
        ` : `<p style="color:var(--text-dim);font-size:.85rem">No patient consultations currently scheduled for your profile.</p>`}
      </div>

      <!-- Issue Medical Prescription Form -->
      <div class="glass-card">
        <p style="font-weight:700;margin-bottom:14px;color:var(--accent)">💊 Issue Medical Prescription</p>
        <div class="form-group" style="margin-bottom:10px">
          <label class="form-label">Select Patient</label>
          <select class="form-select" id="presc-patient">
            ${patients.length ? patients.map(p => `<option value="${p.user_id}|${p.full_name || p.username}">${p.full_name || p.username} (ID: ${p.user_id})</option>`).join('') : '<option value="">No assigned patients available</option>'}
          </select>
        </div>
        <div class="form-group" style="margin-bottom:10px">
          <label class="form-label">Clinical Diagnosis / Indication</label>
          <input type="text" class="form-input" id="presc-diagnosis" placeholder="e.g. Glioblastoma Multiforme (Post-Resection Protocol)" value="Neurological Consultation & Treatment">
        </div>
        <div class="grid-2" style="gap:10px;margin-bottom:10px">
          <div>
            <label class="form-label">Medication Name</label>
            <input type="text" class="form-input" id="presc-med-name" placeholder="e.g. Temozolomide" value="Temozolomide">
          </div>
          <div>
            <label class="form-label">Dosage</label>
            <input type="text" class="form-input" id="presc-dosage" placeholder="e.g. 140 mg Capsule" value="140 mg">
          </div>
        </div>
        <div class="grid-2" style="gap:10px;margin-bottom:10px">
          <div>
            <label class="form-label">Frequency</label>
            <select class="form-select" id="presc-freq">
              <option value="Once Daily (Night / Bedtime)">Once Daily (Bedtime)</option>
              <option value="Twice Daily (Morning & Night)">Twice Daily (BD)</option>
              <option value="Three Times Daily (TDS)">Three Times Daily (TDS)</option>
              <option value="As Needed (SOS / PRN)">As Needed (SOS / PRN)</option>
            </select>
          </div>
          <div>
            <label class="form-label">Duration</label>
            <input type="text" class="form-input" id="presc-duration" placeholder="e.g. 5 Days / 28-day cycle" value="5 Days (28-day cycle)">
          </div>
        </div>
        <div class="form-group" style="margin-bottom:14px">
          <label class="form-label">Instructions / Precautions</label>
          <input type="text" class="form-input" id="presc-instructions" placeholder="e.g. Take on empty stomach with Ondansetron 8mg 30 mins prior." value="Take on empty stomach 1 hr before bedtime with water.">
        </div>
        <button class="btn btn-primary btn-full" onclick="issuePrescription()">💊 Issue & Sign Prescription</button>
      </div>
    </div>

    <!-- Issued Prescriptions History -->
    <div class="glass-card">
      <p style="font-weight:700;margin-bottom:14px">📋 My Issued Prescriptions History</p>
      ${prescList.length ? `
        <table class="data-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Patient</th>
              <th>Diagnosis</th>
              <th>Medication</th>
              <th>Dosage & Frequency</th>
              <th>Duration</th>
              <th>Instructions</th>
            </tr>
          </thead>
          <tbody>
            ${prescList.map(p => `
              <tr>
                <td>${(p.created_at||'').slice(0,10) || 'Today'}</td>
                <td><strong>${p.patient_name || 'Patient'}</strong></td>
                <td style="font-size:0.8rem;color:var(--accent)">${p.diagnosis || 'Clinical Care'}</td>
                <td><strong>💊 ${p.medicine_name || 'Medication'}</strong></td>
                <td><span class="badge badge-cyan">${p.dosage || '—'}</span> ${p.frequency || ''}</td>
                <td>${p.duration || '14 Days'}</td>
                <td style="font-size:0.8rem;color:var(--text-muted)">${p.instructions || '—'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      ` : `<p style="color:var(--text-dim);font-size:.85rem">No prescriptions issued by your account yet.</p>`}
    </div>
  `;
}

// ── Admin Dashboard ───────────────────────────────────────────
function _renderAdminDash(el, data) {
  const stats = data.stats || {};
  const users = data.users || [];
  const logs  = data.audit_logs || [];
  const hosp  = (data.hospitals || [])[0] || { name: 'Apollo Health City - Neurosciences Institute', location: 'Bengaluru, KA', contact: '+91 80 2630 4050' };

  el.innerHTML = `
    <div class="grid-4" style="margin-bottom:24px">
      ${_statCard('👥', 'Total Users',        stats.total_users || users.length, 'var(--accent)')}
      ${_statCard('🔬', 'Total AI Scans',     stats.total_scans || 0,            'var(--green)')}
      ${_statCard('🚨', 'Critical Alerts',    stats.critical_cases || 0,        'var(--red)')}
      ${_statCard('🛡️', 'System Security',    'HIPAA Compliant',                'var(--yellow)')}
    </div>

    <!-- User Management & Role Promotion -->
    <div class="glass-card" style="margin-bottom:20px">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
        <div>
          <p style="font-weight:800;color:var(--accent);margin:0">👥 User Directory & Role Assignment</p>
          <p style="font-size:0.75rem;color:var(--text-muted);margin:0">Manage user accounts and instantly promote or reassign system roles</p>
        </div>
        <span class="badge badge-green">Master Admin Access</span>
      </div>
      ${users.length ? `
        <table class="data-table">
          <thead>
            <tr>
              <th>User</th>
              <th>Current Role</th>
              <th>Email</th>
              <th>Change / Reassign Role</th>
            </tr>
          </thead>
          <tbody>
            ${users.map(u => `
              <tr>
                <td><strong>${u.full_name || u.username}</strong><br><span style="font-size:0.7rem;color:var(--text-dim)">ID: ${u.user_id}</span></td>
                <td><span class="badge badge-${u.role==='doctor'?'blue':(u.role==='radiologist'?'yellow':(u.role==='admin'?'red':'cyan'))}">${(u.role||'patient').toUpperCase()}</span></td>
                <td style="font-size:0.78rem;color:var(--text-muted)">${u.email || '—'}</td>
                <td>
                  <select class="form-select" style="padding:4px 8px;font-size:0.78rem" onchange="updateUserRole('${u.user_id}', this.value)">
                    <option value="patient" ${u.role==='patient'?'selected':''}>👤 Patient</option>
                    <option value="doctor" ${u.role==='doctor'?'selected':''}>👨‍⚕️ Doctor</option>
                    <option value="radiologist" ${u.role==='radiologist'?'selected':''}>👨‍🔬 Radiologist</option>
                    <option value="receptionist" ${u.role==='receptionist'?'selected':''}>👩‍💼 Receptionist</option>
                    <option value="admin" ${u.role==='admin'?'selected':''}>🛡️ Admin</option>
                  </select>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      ` : '<p style="color:var(--text-dim)">No users found in database.</p>'}
    </div>

    <div class="grid-2" style="gap:20px;margin-bottom:20px">
      <!-- Hospital Facilities Status -->
      <div class="glass-card">
        <p style="font-weight:800;margin-bottom:14px;color:var(--text-primary)">🏥 Facility Infrastructure & Equipment</p>
        <div style="display:flex;flex-direction:column;gap:10px">
          <div style="display:flex;justify-content:space-between;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:6px">
            <span>🧠 3.0 Tesla MRI Scanner (Suite A)</span>
            <span class="badge badge-green">Operational (99.8%)</span>
          </div>
          <div style="display:flex;justify-content:space-between;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:6px">
            <span>🔬 1.5 Tesla MRI Scanner (Suite B)</span>
            <span class="badge badge-green">Operational</span>
          </div>
          <div style="display:flex;justify-content:space-between;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:6px">
            <span>🛏️ Neuro-ICU Dedicated Beds</span>
            <span class="badge badge-cyan">18 / 24 Occupied</span>
          </div>
          <div style="display:flex;justify-content:space-between;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:6px">
            <span>🚑 24x7 Advanced Cardiac/Neuro Ambulance</span>
            <span class="badge badge-green">4 Units Ready</span>
          </div>
        </div>
      </div>

      <!-- Live Security & Audit Logs -->
      <div class="glass-card">
        <p style="font-weight:800;margin-bottom:14px">🛡️ Security & Compliance Audit Log</p>
        <div style="max-height:240px;overflow-y:auto;display:flex;flex-direction:column;gap:8px">
          ${logs.length ? logs.map(l => `
            <div style="padding:8px 10px;background:rgba(255,255,255,0.02);border-left:3px solid var(--accent);border-radius:4px;font-size:0.78rem">
              <div style="display:flex;justify-content:space-between">
                <strong style="color:var(--accent)">${l.username || 'System'}</strong>
                <span style="color:var(--text-dim)">${(l.timestamp || '').slice(11, 19) || 'Recent'}</span>
              </div>
              <div style="color:var(--text-muted);margin-top:2px">${l.action || 'Activity'}: <span style="color:var(--text-primary)">${l.details || ''}</span></div>
            </div>
          `).join('') : '<p style="color:var(--text-dim);font-size:0.85rem">No audit events recorded yet.</p>'}
        </div>
      </div>
    </div>
  `;
}

// ── Receptionist Dashboard ────────────────────────────────────
function _renderReceptionistDash(el, data) {
  const stats   = data.stats || {};
  const appts   = data.appointments || [];
  const patients= data.patients || [];
  const doctors = data.doctors || [];

  el.innerHTML = `
    <div class="grid-4" style="margin-bottom:24px">
      ${_statCard('📅', 'Total Appointments', stats.total_appointments || appts.length, 'var(--accent)')}
      ${_statCard('⏳', 'Pending / Intake',  stats.pending_appointments || 0,          'var(--yellow)')}
      ${_statCard('👥', 'Registered Patients',stats.total_patients || patients.length, 'var(--green)')}
      ${_statCard('👨‍⚕️', 'Doctors On Duty',    stats.active_doctors || doctors.length,   'var(--violet)')}
    </div>

    <div class="grid-2" style="gap:20px;margin-bottom:20px">
      <!-- Fast Walk-in Patient Registration Form -->
      <div class="glass-card">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
          <p style="font-weight:800;color:var(--accent);margin:0">👤 Fast Walk-in Patient Intake</p>
          <span class="badge badge-green">Front Desk Registration</span>
        </div>
        <div class="grid-2" style="gap:10px;margin-bottom:10px">
          <div class="form-group">
            <label class="form-label">Patient Full Name</label>
            <input type="text" class="form-input" id="reg-name" placeholder="e.g. Ramesh Kumar">
          </div>
          <div class="form-group">
            <label class="form-label">Phone Number</label>
            <input type="tel" class="form-input" id="reg-phone" placeholder="e.g. +91 98765 12345">
          </div>
        </div>
        <div class="grid-3" style="gap:10px;margin-bottom:10px">
          <div class="form-group">
            <label class="form-label">Age</label>
            <input type="number" class="form-input" id="reg-age" placeholder="42" value="38">
          </div>
          <div class="form-group">
            <label class="form-label">Gender</label>
            <select class="form-select" id="reg-gender">
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Blood Group</label>
            <select class="form-select" id="reg-blood">
              <option value="O+">O+</option>
              <option value="O-">O-</option>
              <option value="A+">A+</option>
              <option value="B+">B+</option>
              <option value="AB+">AB+</option>
            </select>
          </div>
        </div>
        <div class="form-group" style="margin-bottom:10px">
          <label class="form-label">Consulting Neurologist</label>
          <select class="form-select" id="reg-doc">
            ${doctors.map(d => `<option value="${d.user_id}">${d.full_name || d.username} (${d.specialty || 'Neurology'})</option>`).join('')}
          </select>
        </div>
        <div class="form-group" style="margin-bottom:14px">
          <label class="form-label">Emergency Contact Name & Phone</label>
          <input type="text" class="form-input" id="reg-emergency" placeholder="e.g. Sunita Kumar (+91 98765 00000)">
        </div>
        <button class="btn btn-primary btn-full" onclick="registerWalkInPatient()">👤 Register Patient & Open Chart</button>
      </div>

      <!-- Doctor Roster & Availability -->
      <div class="glass-card">
        <p style="font-weight:800;margin-bottom:14px">👨‍⚕️ Neurologist Roster & Availability</p>
        <div style="display:flex;flex-direction:column;gap:10px">
          ${doctors.map(d => `
            <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:rgba(255,255,255,0.02);border-radius:6px;border:1px solid var(--border)">
              <div>
                <strong>${d.full_name || d.username}</strong>
                <div style="font-size:0.75rem;color:var(--text-muted)">${d.specialty || 'Consultant Neurologist & Neuro-Surgeon'}</div>
              </div>
              <span class="badge badge-green">🟢 Available</span>
            </div>
          `).join('')}
        </div>
      </div>
    </div>

    <!-- Live Appointment Queue Table -->
    <div class="glass-card">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
        <p style="font-weight:800;margin:0">📋 Front-Desk Appointment & Check-In Queue</p>
        <span class="badge badge-cyan">Live Schedule</span>
      </div>
      ${appts.length ? `
        <table class="data-table">
          <thead><tr><th>Patient</th><th>Doctor</th><th>Date & Time</th><th>Reason</th><th>Status</th><th>Front Desk Action</th></tr></thead>
          <tbody>
            ${appts.map(a => `<tr>
              <td><strong>${a.patient_name||'Patient'}</strong></td>
              <td>${a.doctor_name||'Doctor'}</td>
              <td>${a.appointment_date||'—'} <span style="font-size:0.75rem;color:var(--text-muted)">(${a.appointment_time||'—'})</span></td>
              <td style="font-size:0.8rem">${a.reason||'Consultation'}</td>
              <td><span class="badge badge-${a.status==='Approved'?'green':(a.status==='Checked In'?'cyan':(a.status==='Completed'?'blue':'yellow'))}">${a.status||'Pending'}</span></td>
              <td style="display:flex;gap:6px">
                ${a.status !== 'Approved' ? `<button class="btn btn-sm btn-success" onclick="approveAppt('${a.appointment_id}')">✅ Approve</button>` : ''}
                <button class="btn btn-sm btn-secondary" onclick="updateAppointmentStatus('${a.appointment_id}', 'Checked In')">🏥 Check-In</button>
                <button class="btn btn-sm btn-primary" onclick="updateAppointmentStatus('${a.appointment_id}', 'Completed')">🏁 Done</button>
              </td>
            </tr>`).join('')}
          </tbody>
        </table>
      ` : '<p style="color:var(--text-dim)">No appointments scheduled in system.</p>'}
    </div>
  `;
}

// ── Radiologist Dashboard ─────────────────────────────────────
function _renderRadiologistDash(el, data) {
  const stats   = data.stats || {};
  const pending = data.pending_scans || [];
  const allScans= data.all_scans || [];

  el.innerHTML = `
    <div class="grid-4" style="margin-bottom:24px">
      ${_statCard('⏳', 'Pending Review',  stats.pending_reviews || pending.length, 'var(--yellow)')}
      ${_statCard('📁', 'Total MRI Scans', stats.total_scans || allScans.length,    'var(--accent)')}
      ${_statCard('🚨', 'Critical Cases',  stats.critical_cases || 0,               'var(--red)')}
      ${_statCard('✅', 'AI Agreement',    '98.4%',                                 'var(--green)')}
    </div>

    <!-- Diagnostic Scans Queue -->
    <div class="glass-card" style="margin-bottom:20px">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
        <div>
          <p style="font-weight:800;margin:0;color:var(--accent)">🔬 Radiology Diagnostic Review Hub</p>
          <p style="font-size:0.75rem;color:var(--text-muted);margin:0">Detailed AI-assisted segmentation, brain mapping, and diagnostic verification</p>
        </div>
        <span class="badge badge-blue">Clinical PACS Review</span>
      </div>
      ${(pending.length ? pending : allScans).length ? `
        <table class="data-table">
          <thead><tr><th>Date</th><th>Patient</th><th>AI Diagnosis</th><th>Brain Region</th><th>Severity</th><th>Status</th><th>Diagnostic Decision</th></tr></thead>
          <tbody>
            ${(pending.length ? pending : allScans).map(s => `<tr>
              <td>${(s.scan_date||'').slice(0,10)||'Today'}</td>
              <td><strong>${s.patient_name||'Patient'}</strong><br><span style="font-size:0.7rem;color:var(--text-dim)">${s.filename||'MRI'}</span></td>
              <td><span class="badge badge-cyan">${s.display_label || (s.tumor_type||'').replace(/\b\w/g,c=>c.toUpperCase())||'—'}</span></td>
              <td>🗺️ ${s.brain_region||'—'}</td>
              <td><span class="badge badge-${_sevBadge(s.severity_level)}">${s.severity_level||'—'}</span></td>
              <td><span class="badge badge-${s.status==='Approved'?'green':'yellow'}">${s.status||'Pending'}</span></td>
              <td>
                <select class="form-select" style="padding:4px 8px;font-size:0.75rem" onchange="updateScanStatus('${s.scan_id}', this.value)">
                  <option value="Pending Doctor Review" ${s.status==='Pending Doctor Review'?'selected':''}>⏳ Pending</option>
                  <option value="Approved" ${s.status==='Approved'?'selected':''}>✅ Approve Diagnosis</option>
                  <option value="Requires Additional Tests" ${s.status==='Requires Additional Tests'?'selected':''}>🔬 3D Re-Segmentation</option>
                  <option value="Rejected" ${s.status==='Rejected'?'selected':''}>❌ Reject Artifact</option>
                </select>
              </td>
            </tr>`).join('')}
          </tbody>
        </table>
      ` : '<div class="alert alert-success">✅ No scans pending radiology review.</div>'}
    </div>

    <!-- Quality Assurance & Modality Matrix -->
    <div class="glass-card">
      <p style="font-weight:800;margin-bottom:12px">📋 Quality Assurance & Imaging Protocol Standards</p>
      <div class="grid-3" style="gap:12px;font-size:0.82rem">
        <div style="padding:10px;background:rgba(255,255,255,0.02);border-radius:6px;border:1px solid var(--border)">
          <strong style="color:var(--accent)">T1-Weighted (Post-Contrast)</strong>
          <div style="color:var(--text-muted);margin-top:4px">Ideal for active tumor margin enhancement and blood-brain barrier breakdown.</div>
        </div>
        <div style="padding:10px;background:rgba(255,255,255,0.02);border-radius:6px;border:1px solid var(--border)">
          <strong style="color:var(--cyan)">T2-FLAIR Sequence</strong>
          <div style="color:var(--text-muted);margin-top:4px">Suppresses CSF signals to reveal peritumoral vasogenic edema and infiltration.</div>
        </div>
        <div style="padding:10px;background:rgba(255,255,255,0.02);border-radius:6px;border:1px solid var(--border)">
          <strong style="color:var(--green)">Grad-CAM Heatmap Validation</strong>
          <div style="color:var(--text-muted);margin-top:4px">Verifies neural network focus alignment with radiological hyperintensities.</div>
        </div>
      </div>
    </div>
  `;
}

// ── Action helpers ────────────────────────────────────────────
async function updateScanStatus(scanId, status) {
  const res = await api(`/api/scans/${scanId}/status`, { method: 'PUT', body: { status } });
  if (res.error) { toast(`❌ ${res.error}`, 'error'); return; }
  toast(`✅ Scan status updated to "${status}"`, 'success');
  renderDashboardPage(document.getElementById('page-container'));
}

async function approveAppt(apptId) {
  const res = await api(`/api/appointments/${apptId}/status`, { method: 'PUT', body: { status: 'Approved' } });
  if (res.error) { toast(`❌ ${res.error}`, 'error'); return; }
  toast('✅ Appointment approved.', 'success');
  renderDashboardPage(document.getElementById('page-container'));
}

async function assignConsultingDoctor() {
  const selectEl = document.getElementById('select-primary-doc');
  const doctorId = selectEl?.value;
  if (!doctorId) {
    toast('⚠️ Please select a doctor from the dropdown.', 'error');
    return;
  }
  showLoader('Setting your consulting doctor...');
  const res = await api('/api/doctor/assign', {
    method: 'POST',
    body: { doctor_id: doctorId }
  });
  hideLoader();
  if (res.error) {
    toast(`❌ ${res.error}`, 'error');
    return;
  }
  toast(`✅ ${res.message}`, 'success');
  renderDashboardPage(document.getElementById('page-container'));
}

async function issuePrescription() {
  const patientSelect = document.getElementById('presc-patient');
  const patientVal = (patientSelect?.value || '').split('|');
  const patientId = patientVal[0];
  const patientName = patientVal[1] || 'Patient';
  const diag = document.getElementById('presc-diagnosis')?.value || 'Neurology Consultation';
  const medName = document.getElementById('presc-med-name')?.value || 'Temozolomide';
  const dosage = document.getElementById('presc-dosage')?.value || '140 mg';
  const freq = document.getElementById('presc-freq')?.value || 'Once Daily (Bedtime)';
  const duration = document.getElementById('presc-duration')?.value || '14 Days';
  const instructions = document.getElementById('presc-instructions')?.value || 'Take as directed.';

  if (!patientId) {
    toast('⚠️ Please select an assigned patient.', 'error');
    return;
  }
  if (!medName) {
    toast('⚠️ Medication name is required.', 'error');
    return;
  }

  showLoader('Issuing medical prescription...');
  const res = await api('/api/prescriptions', {
    method: 'POST',
    body: {
      patient_id: patientId,
      patient_name: patientName,
      diagnosis: diag,
      medicine_name: medName,
      dosage: dosage,
      frequency: freq,
      duration: duration,
      instructions: instructions,
    }
  });
  hideLoader();

  if (res.error) {
    toast(`❌ ${res.error}`, 'error');
    return;
  }

  toast(`✅ Prescription issued for ${patientName}!`, 'success');
  renderDashboardPage(document.getElementById('page-container'));
}

async function bookAppointment() {
  const doctorSelect = document.getElementById('book-doctor');
  const doctorVal = (doctorSelect?.value || '').split('|');
  const date = document.getElementById('book-date')?.value;
  const time = document.getElementById('book-time')?.value;
  const reason = document.getElementById('book-reason')?.value || 'Neurology Consultation & MRI Review';

  if (!date || !time) { toast('⚠️ Please select date and time.', 'error'); return; }

  showLoader('Booking appointment...');
  const res = await api('/api/appointments', { method: 'POST', body: {
    doctor_id:    doctorVal[0] || 'usr-doctor-001',
    doctor_name:  doctorVal[1] || 'Dr. Sarah Jenkins (Neurology)',
    appointment_date: date,
    appointment_time: time,
    reason: reason,
  }});
  hideLoader();
  if (res.error) { toast(`❌ ${res.error}`, 'error'); return; }
  toast('✅ Appointment booked successfully!', 'success');
  renderDashboardPage(document.getElementById('page-container'));
}

async function updateUserRole(userId, newRole) {
  showLoader('Updating user role...');
  const res = await api(`/api/admin/users/${userId}/role`, {
    method: 'PUT',
    body: { role: newRole }
  });
  hideLoader();
  if (res.error) {
    toast(`❌ ${res.error}`, 'error');
    return;
  }
  toast(`✅ ${res.message}`, 'success');
  renderDashboardPage(document.getElementById('page-container'));
}

async function registerWalkInPatient() {
  const name = document.getElementById('reg-name')?.value.trim();
  const phone = document.getElementById('reg-phone')?.value.trim();
  const age = document.getElementById('reg-age')?.value;
  const gender = document.getElementById('reg-gender')?.value;
  const blood = document.getElementById('reg-blood')?.value;
  const doctorId = document.getElementById('reg-doc')?.value;
  const emergency = document.getElementById('reg-emergency')?.value.trim();

  if (!name) {
    toast('⚠️ Please enter the patient full name.', 'error');
    return;
  }

  showLoader('Registering walk-in patient...');
  const res = await api('/api/receptionist/register-patient', {
    method: 'POST',
    body: {
      full_name: name,
      phone: phone,
      age: age,
      gender: gender,
      blood_group: blood,
      assigned_doctor_id: doctorId,
      emergency_contact_name: emergency,
    }
  });
  hideLoader();
  if (res.error) {
    toast(`❌ ${res.error}`, 'error');
    return;
  }
  toast(`✅ ${res.message}`, 'success');
  renderDashboardPage(document.getElementById('page-container'));
}

async function updateAppointmentStatus(apptId, status) {
  const res = await api(`/api/appointments/${apptId}/status`, {
    method: 'PUT',
    body: { status: status }
  });
  if (res.error) {
    toast(`❌ ${res.error}`, 'error');
    return;
  }
  toast(`✅ Appointment marked as "${status}"`, 'success');
  renderDashboardPage(document.getElementById('page-container'));
}

function _sevBadge(level) {
  if (!level) return 'cyan';
  const m = { Low: 'green', Mild: 'green', None: 'green', Moderate: 'yellow', High: 'yellow', Severe: 'orange', Critical: 'red', 'No Tumor': 'green' };
  return m[level] || 'cyan';
}

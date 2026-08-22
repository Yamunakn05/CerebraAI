// ============================================================
// emergency.js — Emergency Contacts & SOS Profile Page
// ============================================================

async function renderEmergencyPage(container) {
  container.innerHTML = `
    <div class="page-header">
      <h1>🏥 Emergency SOS & Crisis Center</h1>
      <p>Configure your personal emergency contact, address, and medical alerts for immediate 1-click SOS response. In acute danger, call <strong>112</strong> immediately.</p>
    </div>

    <!-- 1-Click SOS Alert Dispatch Banner -->
    <div class="glass-card" style="margin-bottom:24px;border:2px solid var(--red);background:rgba(239,68,68,0.08);box-shadow:0 0 30px rgba(239,68,68,0.2)">
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px">
        <div>
          <div style="font-size:1.3rem;font-weight:900;color:var(--red);display:flex;align-items:center;gap:8px">
            🚨 <span>ACUTE NEUROLOGICAL EMERGENCY SOS</span>
          </div>
          <p style="color:var(--text-muted);font-size:0.88rem;margin-top:4px;max-width:650px">
            If you or someone nearby is experiencing acute neurological deficits (such as seizures, sudden paralysis, facial drooping, loss of speech, or severe head trauma), trigger the SOS alert below.
          </p>
        </div>
        <button class="btn btn-danger btn-lg" style="font-weight:800;letter-spacing:0.04em;padding:14px 28px;box-shadow:0 0 20px rgba(239,68,68,0.5)" onclick="triggerSOSAlert()">
          🚨 TRIGGER 1-CLICK SOS
        </button>
      </div>
      <div id="sos-dispatch-result" style="margin-top:14px"></div>
    </div>

    <!-- 2-Column Grid: Emergency Profile Form & National Hotlines -->
    <div class="grid-2" style="gap:20px;margin-bottom:24px">
      <!-- Emergency Contact & Address Profile Card -->
      <div class="glass-card">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
          <div>
            <p style="font-weight:800;color:var(--accent);margin:0">📝 My Emergency Profile & Address</p>
            <p style="font-size:0.75rem;color:var(--text-dim);margin:0">Used by first responders and consulting doctors during an emergency</p>
          </div>
          <span class="badge badge-cyan">SOS Profile</span>
        </div>

        <div class="grid-2" style="gap:10px;margin-bottom:10px">
          <div class="form-group">
            <label class="form-label">Emergency Contact Name</label>
            <input type="text" class="form-input" id="em-contact-name" placeholder="e.g. John Doe (Spouse / Parent)">
          </div>
          <div class="form-group">
            <label class="form-label">Emergency Contact Phone</label>
            <input type="tel" class="form-input" id="em-contact-phone" placeholder="e.g. +91 98765 43210">
          </div>
        </div>

        <div class="grid-2" style="gap:10px;margin-bottom:10px">
          <div class="form-group">
            <label class="form-label">Relationship to Patient</label>
            <select class="form-select" id="em-contact-relation">
              <option value="Spouse">Spouse / Partner</option>
              <option value="Parent">Parent / Guardian</option>
              <option value="Sibling">Sibling</option>
              <option value="Child">Son / Daughter</option>
              <option value="Other">Other Family / Friend</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Blood Group</label>
            <select class="form-select" id="em-blood-group">
              <option value="O+">O+</option>
              <option value="O-">O-</option>
              <option value="A+">A+</option>
              <option value="A-">A-</option>
              <option value="B+">B+</option>
              <option value="B-">B-</option>
              <option value="AB+">AB+</option>
              <option value="AB-">AB-</option>
            </select>
          </div>
        </div>

        <div class="form-group" style="margin-bottom:10px">
          <label class="form-label">Home Address & Landmark (for Ambulance Dispatch)</label>
          <textarea class="form-input" id="em-home-address" rows="2" placeholder="e.g. Flat 402, Green Meadows, 12th Cross, MG Road, Bengaluru, Karnataka - 560001"></textarea>
        </div>

        <div class="form-group" style="margin-bottom:14px">
          <label class="form-label">Critical Medical Alerts & Allergies</label>
          <input type="text" class="form-input" id="em-alert-notes" placeholder="e.g. Glioblastoma patient, Seizure risk, Severe Penicillin allergy">
        </div>

        <button class="btn btn-primary btn-full" onclick="saveEmergencyProfile()">💾 Save Emergency Profile</button>
      </div>

      <!-- Quick Emergency Numbers -->
      <div class="glass-card">
        <p style="font-weight:800;margin-bottom:14px;color:var(--text-primary)">📞 Official Emergency Helplines</p>
        <div id="emergency-grid" style="display:flex;flex-direction:column;gap:10px"></div>
      </div>
    </div>

    <!-- Map Locators -->
    <div class="glass-card" style="margin-bottom:24px">
      <p style="font-weight:800;margin-bottom:14px">🗺️ Instant Nearby Healthcare & Hospital Locator</p>
      <div class="grid-4" id="map-links-grid" style="gap:12px"></div>
    </div>

    <!-- Clinical Disclaimer -->
    <div class="glass-card" style="border-left:4px solid var(--red)">
      <p style="font-weight:700;color:var(--red);margin-bottom:8px">⚠️ Emergency Protocol Notice</p>
      <ul style="color:var(--text-muted);font-size:.83rem;line-height:1.9;padding-left:16px">
        <li>CerebraAI provides decision support and dispatch assistance. Always call local paramedics at <strong>112</strong> or <strong>102</strong> during acute crises.</li>
        <li>Keep the airway clear and protect the patient from physical impact during seizures. Do not place objects into the patient's mouth.</li>
      </ul>
    </div>
  `;

  // Fetch emergency numbers and current user profile
  _loadEmergencyData();
}

async function _loadEmergencyData() {
  // Load numbers & map links
  const res = await api('/api/emergency');
  if (res && res.numbers) {
    const grid = document.getElementById('emergency-grid');
    if (grid) {
      grid.innerHTML = res.numbers.map(item => `
        <div class="emergency-card" style="padding:10px 14px">
          <div class="emergency-icon" style="font-size:1.5rem">${item.icon}</div>
          <div style="flex:1">
            <div style="display:flex;justify-content:space-between;align-items:center">
              <div class="emergency-name" style="font-size:0.9rem">${item.name}</div>
              <a href="tel:${item.number}" class="badge badge-red" style="font-size:0.8rem;text-decoration:none;padding:2px 8px">📞 ${item.number}</a>
            </div>
            <div class="emergency-desc" style="font-size:0.75rem">${item.desc}</div>
          </div>
        </div>
      `).join('');
    }
  }

  if (res && res.map_links) {
    const mapGrid = document.getElementById('map-links-grid');
    if (mapGrid) {
      mapGrid.innerHTML = res.map_links.map(l => `
        <a href="${l.url}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary btn-full" style="justify-content:center;text-align:center;font-size:0.85rem">
          ${l.label} ↗
        </a>
      `).join('');
    }
  }

  // Load user profile details
  const profRes = await api('/api/emergency/profile');
  if (profRes && profRes.profile) {
    const p = profRes.profile;
    const nameEl = document.getElementById('em-contact-name');
    const phoneEl = document.getElementById('em-contact-phone');
    const relEl = document.getElementById('em-contact-relation');
    const bgEl = document.getElementById('em-blood-group');
    const addrEl = document.getElementById('em-home-address');
    const notesEl = document.getElementById('em-alert-notes');

    if (nameEl) nameEl.value = p.emergency_contact_name || '';
    if (phoneEl) phoneEl.value = p.emergency_contact_phone || '';
    if (relEl && p.emergency_contact_relation) relEl.value = p.emergency_contact_relation;
    if (bgEl && p.blood_group) bgEl.value = p.blood_group;
    if (addrEl) addrEl.value = p.home_address || '';
    if (notesEl) notesEl.value = p.medical_alert_notes || '';
  }
}

async function saveEmergencyProfile() {
  const name = document.getElementById('em-contact-name')?.value.trim();
  const phone = document.getElementById('em-contact-phone')?.value.trim();
  const relation = document.getElementById('em-contact-relation')?.value;
  const bloodGroup = document.getElementById('em-blood-group')?.value;
  const address = document.getElementById('em-home-address')?.value.trim();
  const alertNotes = document.getElementById('em-alert-notes')?.value.trim();

  if (!phone) {
    toast('⚠️ Please enter an emergency contact phone number.', 'error');
    return;
  }

  showLoader('Saving emergency profile...');
  const res = await api('/api/emergency/profile', {
    method: 'POST',
    body: {
      emergency_contact_name: name,
      emergency_contact_phone: phone,
      emergency_contact_relation: relation,
      blood_group: bloodGroup,
      home_address: address,
      medical_alert_notes: alertNotes,
    }
  });
  hideLoader();

  if (res.error) {
    toast(`❌ ${res.error}`, 'error');
    return;
  }

  toast('✅ Emergency profile & address saved successfully!', 'success');
}

async function triggerSOSAlert() {
  const resDiv = document.getElementById('sos-dispatch-result');
  if (!resDiv) return;

  showLoader('Dispatching emergency SOS alert...');
  const res = await api('/api/emergency/sos', { method: 'POST' });
  hideLoader();

  if (res.error) {
    toast(`❌ ${res.error}`, 'error');
    return;
  }

  resDiv.innerHTML = `
    <div class="glass-card animate-in" style="background:rgba(239,68,68,0.15);border:1px solid var(--red);margin-top:12px">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
        <strong style="color:var(--red);font-size:1.1rem">🚨 EMERGENCY SOS DISPATCH ACTIVE</strong>
        <span class="badge badge-red">Active Incident</span>
      </div>
      <div class="grid-2" style="gap:10px;font-size:0.85rem">
        <div><strong>Patient:</strong> ${res.patient}</div>
        <div><strong>Emergency Contact:</strong> <a href="tel:${res.contact_phone}" style="color:var(--accent);font-weight:700">${res.contact_phone}</a></div>
        <div><strong>Blood Group:</strong> ${res.blood_group}</div>
        <div><strong>Allergies:</strong> ${res.allergies}</div>
        <div style="grid-column:span 2"><strong>Dispatch Address:</strong> ${res.home_address}</div>
      </div>
      <div style="margin-top:10px;display:flex;gap:10px;flex-wrap:wrap">
        <a href="tel:112" class="btn btn-danger btn-sm">📞 Call National Paramedics (112)</a>
        <a href="tel:102" class="btn btn-danger btn-sm">🚑 Call Free Ambulance (102)</a>
        ${res.contact_phone && res.contact_phone !== '112' ? `<a href="tel:${res.contact_phone}" class="btn btn-primary btn-sm">📞 Call Family Contact</a>` : ''}
      </div>
    </div>
  `;

  toast('🚨 Emergency SOS alert triggered & notifications dispatched!', 'error', 6000);
}

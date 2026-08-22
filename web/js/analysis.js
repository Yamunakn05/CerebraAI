// ============================================================
// analysis.js — AI Analysis Pipeline + Results Display
// ============================================================

const ANALYSIS_STEPS = [
  { icon: '🧠', label: 'Classifying tumor type...' },
  { icon: '✂️', label: 'Segmenting tumor region...' },
  { icon: '🗺️', label: 'Mapping brain region...' },
  { icon: '📊', label: 'Calculating severity...' },
  { icon: '📐', label: 'Estimating dimensions...' },
  { icon: '✅', label: 'Analysis complete!' },
];

const REGION_DATA = {
  'Frontal Lobe':   { fn: 'Executive function, movement, personality.',  access: 'High - Generally accessible for surgical resection.', symptoms: ['Personality changes','Motor weakness','Executive dysfunction'] },
  'Temporal Lobe':  { fn: 'Memory, language, auditory perception.',       access: 'Moderate - Deep structures can be sensitive.',         symptoms: ['Memory loss','Language difficulties','Auditory hallucinations'] },
  'Occipital Lobe': { fn: 'Primary visual processing.',                  access: 'Moderate - Proximity to visual cortex.',               symptoms: ['Visual field defects','Hallucinations','Object recognition issues'] },
  'Parietal Lobe':  { fn: 'Sensory perception, spatial awareness.',       access: 'Moderate - Careful navigation of sensory pathways.',   symptoms: ['Sensory loss','Spatial confusion','Coordination issues'] },
  'Cerebellum':     { fn: 'Balance, coordination, fine motor control.',   access: 'Low - Critical structures; high surgical risk.',       symptoms: ['Ataxia (balance loss)','Dizziness','Fine motor tremors'] },
  'Brain Stem':     { fn: 'Breathing, heart rate, sleep, consciousness.', access: 'Inoperable / Extremely High Risk.',                   symptoms: ['Respiratory depression','Cranial nerve deficits','Vital sign instability'] },
};

const TREATMENTS_DATA = {
  glioma: [
    { name: 'Surgical Resection', desc: 'Removal of as much tumor tissue as possible.' },
    { name: 'Radiation Therapy', desc: 'High-energy rays to kill remaining tumor cells.' },
    { name: 'Chemotherapy', desc: 'Temozolomide is commonly used for glioblastoma.' },
    { name: 'Targeted Therapy', desc: 'Bevacizumab may be used for recurrent glioma.' },
  ],
  meningioma: [
    { name: 'Active Surveillance', desc: 'Monitoring with periodic MRI for slow-growing tumors.' },
    { name: 'Surgical Removal', desc: 'Primary treatment for symptomatic meningiomas.' },
    { name: 'Radiation Therapy', desc: 'Stereotactic radiosurgery for inoperable cases.' },
  ],
  pituitary: [
    { name: 'Medical Management', desc: 'Dopamine agonists or somatostatin analogues for hormonal tumors.' },
    { name: 'Transsphenoidal Surgery', desc: 'Minimally invasive surgery through the nasal passage.' },
    { name: 'Radiation Therapy', desc: 'Used when surgery is not feasible or incomplete.' },
  ],
  notumor: [],
};

function renderAnalysisPage(container) {
  const role = App.user?.role?.toLowerCase() || 'patient';
  if (['receptionist', 'admin'].includes(role)) {
    container.innerHTML = `
      <div class="page-header"><h1>🔬 AI Analysis Pipeline</h1></div>
      <div class="glass-card" style="text-align:center;padding:40px">
        <div style="font-size:3.5rem;margin-bottom:12px">🚫</div>
        <h2 style="color:var(--red);margin-bottom:8px">Access Restricted</h2>
        <p style="color:var(--text-dim)"><strong style="color:var(--text-primary)">${role.charAt(0).toUpperCase()+role.slice(1)}</strong> role cannot access AI Analysis.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="page-header">
      <h1>🔬 AI Analysis Pipeline</h1>
      <p>Complete tumor detection, segmentation, Grad-CAM explanation, severity assessment, and surgical risk mapping.</p>
    </div>

    <!-- Run button -->
    <div style="margin-bottom:24px;display:flex;align-items:center;gap:14px;flex-wrap:wrap">
      <button class="btn btn-primary btn-lg" id="run-analysis-btn" onclick="runAnalysis()">
        🚀 Run Full AI Analysis
      </button>
      <div id="mri-status"></div>
    </div>

    <!-- Progress area -->
    <div id="analysis-progress" class="hidden glass-card" style="margin-bottom:24px">
      <p style="font-weight:700;margin-bottom:14px;color:var(--accent)">⚡ Analysis in Progress</p>
      <div id="steps-container"></div>
      <div class="progress-bar" style="margin-top:16px">
        <div class="progress-fill" id="main-progress" style="width:0%"></div>
      </div>
    </div>

    <!-- Results area -->
    <div id="analysis-results" class="hidden"></div>
  `;

  const statusEl = document.getElementById('mri-status');
  if (!App.uploadedImage) {
    statusEl.innerHTML = `
      <div class="alert alert-warning" style="margin:0">
        ⚠️ No MRI uploaded.
        <button class="btn btn-sm btn-secondary" style="margin-left:10px" onclick="App.navigate('upload')">
          📤 Upload MRI
        </button>
      </div>
    `;
    document.getElementById('run-analysis-btn').disabled = true;
  } else {
    statusEl.innerHTML = `
      <div class="badge badge-green">✅ MRI Ready: ${App.uploadedImage.filename}</div>
    `;
  }

  if (App.analysisResult) {
    if (App.uploadedImage && App.analysisResult.upload_id !== App.uploadedImage.upload_id) {
      App.analysisResult = null;
    } else {
      renderResults(App.analysisResult);
    }
  }
}

async function runAnalysis() {
  if (!App.uploadedImage) {
    toast('⚠️ Please upload an MRI scan first.', 'error');
    return;
  }

  const btn = document.getElementById('run-analysis-btn');
  const uploadId = App.uploadedImage.upload_id;
  const analysisVersion = ++App.analysisVersion;
  App.analysisAbortController?.abort();
  const controller = new AbortController();
  App.analysisAbortController = controller;
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-sm"></span> Running...';

  const progressDiv = document.getElementById('analysis-progress');
  progressDiv.classList.remove('hidden');
  const stepsEl = document.getElementById('steps-container');
  stepsEl.innerHTML = '';

  ANALYSIS_STEPS.forEach((s, i) => {
    const div = document.createElement('div');
    div.className = 'analysis-step';
    div.id = `step-${i}`;
    div.innerHTML = `<span class="step-icon">${s.icon}</span><span class="step-label">${s.label}</span><span class="step-status" id="step-status-${i}">⏳</span>`;
    stepsEl.appendChild(div);
  });

  let stepIdx = 0;
  const stepInterval = setInterval(() => {
    if (stepIdx > 0) {
      const prevStep = document.getElementById(`step-${stepIdx - 1}`);
      if (prevStep) { prevStep.classList.remove('active'); prevStep.classList.add('done'); }
      document.getElementById(`step-status-${stepIdx - 1}`).textContent = '✅';
    }
    if (stepIdx < ANALYSIS_STEPS.length - 1) {
      const curStep = document.getElementById(`step-${stepIdx}`);
      if (curStep) curStep.classList.add('active');
      document.getElementById(`step-status-${stepIdx}`).textContent = '⚡';
      const pct = Math.round((stepIdx + 1) / ANALYSIS_STEPS.length * 85);
      document.getElementById('main-progress').style.width = pct + '%';
    }
    stepIdx++;
    if (stepIdx >= ANALYSIS_STEPS.length) clearInterval(stepInterval);
  }, 120);

  let res;
  try {
    res = await api('/api/analyze', { method: 'POST', body: { upload_id: uploadId }, signal: controller.signal });
  } catch (err) {
    if (err.name === 'AbortError') return;
    res = { error: 'Analysis request failed. Please try again.' };
  }

  // Do not let an earlier image's response alter the current image's page.
  if (analysisVersion !== App.analysisVersion || App.uploadedImage?.upload_id !== uploadId) return;

  clearInterval(stepInterval);
  ANALYSIS_STEPS.forEach((_, i) => {
    const s = document.getElementById(`step-${i}`);
    if (s) { s.classList.remove('active'); s.classList.add('done'); }
    const ss = document.getElementById(`step-status-${i}`);
    if (ss) ss.textContent = '✅';
  });
  document.getElementById('main-progress').style.width = '100%';

  btn.disabled = false;
  btn.innerHTML = '🔄 Re-run Analysis';

  const resultsEl = document.getElementById('analysis-results');

  if (res.error) {
    toast(`❌ ${res.error}`, 'error');
    if (resultsEl) {
      resultsEl.classList.remove('hidden');
      resultsEl.innerHTML = `
        <div class="glass-card" style="text-align:center;padding:32px;border:1px solid var(--red);margin-top:20px">
          <div style="font-size:2.5rem;margin-bottom:10px">⚠️</div>
          <h3 style="color:var(--red);margin-bottom:8px">Analysis Error</h3>
          <p style="color:var(--text-dim);margin-bottom:16px">${escapeHtml(res.error)}</p>
          <button class="btn btn-primary" onclick="runAnalysis()">🚀 Retry Analysis</button>
        </div>
      `;
      resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    return;
  }

  App.analysisResult = res;
  toast('✅ Analysis complete! Results saved.', 'success');
  renderResults(res);
  if (resultsEl) {
    resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

function renderResults(r) {
  const el = document.getElementById('analysis-results');
  if (!el) return;
  el.classList.remove('hidden');

  const sevColor = severityColor(r.severity_level);

  el.innerHTML = `
    <!-- Hero result card -->
    <div class="result-hero animate-in" style="margin-bottom:24px">
      <div class="grid-3" style="align-items:center;text-align:center;gap:16px">
        <div style="padding:12px;border-right:1px solid var(--border)">
          <div style="font-size:.75rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px">Detected Type</div>
          <div class="result-type" style="font-size:1.8rem;font-weight:900;color:var(--text-primary);line-height:1.2">${r.display_label || 'N/A'}</div>
          <div style="color:var(--accent);font-size:.9rem;font-weight:700;margin-top:6px">Confidence: ${((r.confidence || 0) > 1 ? (r.confidence || 0) : (r.confidence || 0) * 100).toFixed(2)}%</div>
        </div>

        <div style="padding:12px;border-right:1px solid var(--border)">
          <div style="font-size:.75rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px">Severity</div>
          <div style="font-size:1.8rem;font-weight:800;color:${sevColor};line-height:1.2">${r.severity_emoji || ''} ${r.severity_level || 'N/A'}</div>
          <div style="color:var(--text-muted);font-size:.85rem;margin-top:6px">Score: <strong>${parseFloat(r.severity_score||0).toFixed(1)}/100</strong></div>
        </div>

        <div style="padding:12px">
          <div style="font-size:.75rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px">Region</div>
          <div style="font-size:1.5rem;font-weight:700;color:var(--text-primary);line-height:1.2">🗺️ ${r.brain_region || 'N/A'}</div>
          <div style="color:var(--text-muted);font-size:.85rem;margin-top:6px">Area: <strong>${(r.tumor_area_pct||0).toFixed(2)}%</strong></div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs" id="result-tabs">
      <button class="tab-btn active" onclick="switchTab('overview')">📊 Overview</button>
      <button class="tab-btn" onclick="switchTab('classification')">🔬 Classification</button>
      <button class="tab-btn" onclick="switchTab('segmentation')">✂️ Segmentation</button>
      <button class="tab-btn" onclick="switchTab('region')">🗺️ Brain Region</button>
      <button class="tab-btn" onclick="switchTab('severity')">🚨 Severity & Treatment</button>
      <button class="tab-btn" onclick="switchTab('view3d')">🌐 3D View</button>
      <button class="tab-btn" onclick="switchTab('surgical')">🎯 Surgical Risk Map</button>
      <button class="tab-btn" onclick="switchTab('reports')">📋 Reports</button>
    </div>

    <div id="tab-overview" class="tab-pane active">${_buildOverviewTab(r)}</div>
    <div id="tab-classification" class="tab-pane">${_buildClassificationTab(r)}</div>
    <div id="tab-segmentation" class="tab-pane">${_buildSegmentationTab(r)}</div>
    <div id="tab-region" class="tab-pane">${_buildRegionTab(r)}</div>
    <div id="tab-severity" class="tab-pane">${_buildSeverityTab(r)}</div>
    <div id="tab-view3d" class="tab-pane">${_build3DViewTab(r)}</div>
    <div id="tab-surgical" class="tab-pane">${_buildSurgicalRiskTab(r)}</div>
    <div id="tab-reports" class="tab-pane">${_buildReportsTab()}</div>
  `;

  _loadVisualImages(r);
}

function switchTab(name) {
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  const pane = document.getElementById(`tab-${name}`);
  if (pane) pane.classList.add('active');
  const btn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick')?.includes(`'${name}'`));
  if (btn) btn.classList.add('active');

  if (name === 'surgical') _renderSurgicalRiskCanvas();
  if (name === 'view3d') _render3DCanvas();
}

function _buildOverviewTab(r) {
  const seg = r.segmentation || {};
  const dims = r.dimensions || {};
  const cls  = r.classification || {};
  return `
    <div class="grid-2" style="gap:18px;margin-bottom:20px">
      <div class="glass-card">
        <div style="font-size:.8rem;color:var(--text-dim);margin-bottom:4px">Detected Tumor</div>
        <div style="font-size:1.3rem;font-weight:700">${cls.display_label || r.display_label || 'N/A'}</div>
      </div>
      <div class="glass-card">
        <div style="font-size:.8rem;color:var(--text-dim);margin-bottom:4px">Tumor Dimensions</div>
        <div style="font-size:1.3rem;font-weight:700">${(dims.width_mm||0).toFixed(2)}mm × ${(dims.height_mm||0).toFixed(2)}mm</div>
      </div>
    </div>
    <div class="glass-card" style="margin-bottom:20px">
      <div style="font-size:.8rem;color:var(--text-dim);margin-bottom:8px">Tumor Area Coverage</div>
      <div style="font-size:1.2rem;font-weight:700;margin-bottom:8px">${(seg.tumor_area_pct||r.tumor_area_pct||0).toFixed(2)}% of brain scan</div>
      <div class="progress-bar"><div class="progress-fill" style="width:${Math.min(seg.tumor_area_pct||r.tumor_area_pct||0,100)}%"></div></div>
    </div>
    <div id="comparison-grid" style="margin-top:20px"></div>
  `;
}

function _buildClassificationTab(r) {
  const cls = r.classification || {};
  const probs = cls.all_probabilities || r.all_probabilities || {};
  const probRows = Object.entries(probs).map(([k, v]) => {
    const rawNum = typeof v === 'number' ? v : parseFloat(v) || 0;
    const pctVal = rawNum > 1 ? rawNum : rawNum * 100;
    const formatted = pctVal.toFixed(2);
    const widthPct = Math.min(Math.max(pctVal, 0), 100).toFixed(2);
    return `
    <div style="margin-bottom:10px">
      <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:.82rem">
        <span style="color:var(--text-muted)">${k.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}</span>
        <span style="color:var(--text-primary);font-weight:700">${formatted}%</span>
      </div>
      <div class="progress-bar"><div class="progress-fill" style="width:${widthPct}%"></div></div>
    </div>
  `;
  }).join('');

  const confRaw = cls.confidence || r.confidence || 0;
  const confNum = typeof confRaw === 'number' ? confRaw : parseFloat(confRaw) || 0;
  const confVal = confNum > 1 ? confNum : confNum * 100;
  const confFormatted = confVal.toFixed(2);

  return `
    <div class="glass-card" style="margin-bottom:18px">
      <div style="font-size:.8rem;color:var(--text-dim);margin-bottom:4px">Predicted Type</div>
      <div style="font-size:1.6rem;font-weight:700;margin-bottom:8px">${cls.display_label || r.display_label || 'N/A'}</div>
      <div style="font-size:.8rem;color:var(--text-dim);margin-bottom:4px">Confidence</div>
      <div style="font-size:1.6rem;font-weight:700;color:var(--accent)">${confFormatted}%</div>
    </div>
    <div class="glass-card" style="margin-bottom:18px">
      <p style="font-weight:700;margin-bottom:14px">📊 Probability Distribution</p>
      ${probRows}
    </div>
    <div class="glass-card">
      <p style="font-weight:700;margin-bottom:12px">🎯 Grad-CAM Explanation (AI Focus Area)</p>
      <p style="color:var(--text-dim);font-size:.82rem;margin-bottom:14px">Areas highlighted by the AI as most relevant to its prediction</p>
      <img id="gradcam-img" src="" alt="Grad-CAM" style="width:100%;max-width:600px;display:block;margin:0 auto;border-radius:var(--radius-sm);border:1px solid var(--border);display:none" />
      <div id="gradcam-loader" class="alert alert-info">⏳ Loading Grad-CAM visualization...</div>
    </div>
  `;
}

function _buildSegmentationTab(r) {
  const seg  = r.segmentation || {};
  const dims = r.dimensions || {};
  return `
    <div class="glass-card" style="margin-bottom:18px">
      <div class="grid-2">
        <div>
          <div style="font-size:.8rem;color:var(--text-dim);margin-bottom:4px">Tumor Area</div>
          <div style="font-size:1.5rem;font-weight:700">${(seg.tumor_area_pct||r.tumor_area_pct||0).toFixed(2)}% of brain</div>
        </div>
        <div>
          <div style="font-size:.8rem;color:var(--text-dim);margin-bottom:4px">Estimated Dimensions</div>
          <div style="font-size:1.5rem;font-weight:700;color:var(--accent)">${(dims.width_mm||0).toFixed(2)}mm × ${(dims.height_mm||0).toFixed(2)}mm</div>
        </div>
      </div>
    </div>
    <div class="comparison-grid">
      <div class="comparison-img-wrap">
        <p style="font-weight:700;margin-bottom:10px;font-size:.88rem">🎯 Segmented Tumor Contour</p>
        <img id="contour-img" src="" alt="Contour" style="width:100%;border-radius:var(--radius-sm);border:1px solid var(--border);display:none"/>
        <div id="contour-loader" class="alert alert-info" style="font-size:.82rem">⏳ Loading contour...</div>
      </div>
      <div class="comparison-img-wrap">
        <p style="font-weight:700;margin-bottom:10px;font-size:.88rem">🩹 Raw Segmentation Mask</p>
        <img id="mask-img" src="" alt="Mask" style="width:100%;border-radius:var(--radius-sm);border:1px solid var(--border);display:none"/>
        <div id="mask-loader" class="alert alert-info" style="font-size:.82rem">⏳ Loading mask...</div>
      </div>
    </div>
  `;
}

function _buildRegionTab(r) {
  const reg = r.region || {};
  const regName = r.brain_region || reg.region || 'N/A';
  const rd = REGION_DATA[regName] || {};
  const symptoms = rd.symptoms || ['Monitor for localized neurological deficits.'];
  return `
    <div class="glass-card" style="margin-bottom:18px">
      <h3 style="color:var(--accent);margin-bottom:12px">🗺️ Anatomical Summary: ${regName}</h3>
      <p style="color:var(--text-muted);font-size:.85rem;margin-bottom:8px"><strong>Primary Function:</strong> ${rd.fn || 'General neurological integration.'}</p>
      <p style="color:var(--text-muted);font-size:.85rem;margin-bottom:8px"><strong>Surgical Accessibility:</strong> ${rd.access || 'Consult neurosurgical specialist.'}</p>
      <p style="color:var(--text-muted);font-size:.85rem"><strong>Region Confidence:</strong> ${r.region_confidence || reg.confidence || 'N/A'}</p>
    </div>
    <div class="glass-card" style="margin-bottom:18px">
      <p style="font-weight:700;margin-bottom:12px">⚠️ Predicted Symptom Correlation</p>
      ${symptoms.map(s => `<div style="padding:8px 0;border-bottom:1px solid var(--border);font-size:.85rem;color:var(--text-muted)">
        ⚠️ <strong style="color:var(--text-primary)">${s}</strong>: <em>Clinical observation recommended.</em>
      </div>`).join('')}
    </div>
    <div class="glass-card">
      <p style="font-weight:700;margin-bottom:8px"> Detailed Impact Narrative</p>
      <p style="color:var(--text-muted);font-size:.85rem;line-height:1.7">${r.region_impact || reg.impact || 'Detailed functional impact assessment available after clinical review.'}</p>
    </div>
  `;
}

function _buildSeverityTab(r) {
  const sev = r.severity || {};
  const level = r.severity_level || sev.level || 'N/A';
  const score = parseFloat(r.severity_score || sev.score || 0);
  const color = severityColor(level);
  const factors = r.severity_factors || sev.factors || {};

  const tumorKey = (r.label || '').toLowerCase();
  const treatments = TREATMENTS_DATA[tumorKey] || [];

  const factorsHtml = Object.entries(factors).map(([k, v]) =>
    `<div style="padding:6px 0;font-size:.82rem;border-bottom:1px solid var(--border);color:var(--text-muted)">
      <strong style="color:var(--text-primary)">${k.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}:</strong> ${v}
    </div>`).join('');

  return `
    <div class="glass-card" style="margin-bottom:18px;border-color:${color}40">
      <div class="grid-2">
        <div>
          <div style="font-size:.8rem;color:var(--text-dim);margin-bottom:4px">Overall Severity</div>
          <div style="font-size:2rem;font-weight:800;color:${color}">${r.severity_emoji||''} ${level}</div>
        </div>
        <div>
          <div style="font-size:.8rem;color:var(--text-dim);margin-bottom:4px">Severity Score</div>
          <div style="font-size:2rem;font-weight:800;color:${color}">${score.toFixed(1)}<span style="font-size:1rem;color:var(--text-dim)">/100</span></div>
        </div>
      </div>
    </div>

    <!-- Severity bar -->
    <div class="glass-card" style="margin-bottom:18px">
      <p style="font-size:.78rem;color:var(--text-dim);margin-bottom:10px;text-transform:uppercase;letter-spacing:.06em">Severity Scale</p>
      <div class="severity-bar-bg">
        <div class="severity-needle" style="left:${score}%"></div>
      </div>
      <div style="display:flex;justify-content:space-between;margin-top:6px;font-size:.7rem;color:var(--text-dim)">
        <span>Low</span><span>Moderate</span><span>High</span><span>Critical</span>
      </div>
    </div>

    <!-- Explanation & Factors -->
    <div class="grid-2" style="gap:18px;margin-bottom:20px">
      <div class="glass-card">
        <p style="font-weight:700;margin-bottom:8px">📝 Severity Explanation</p>
        <p style="color:var(--text-muted);font-size:.85rem;line-height:1.7">${r.severity_explanation || sev.explanation || 'Severity assessment based on tumor type, area, and brain location.'}</p>
      </div>
      <div class="glass-card">
        <p style="font-weight:700;margin-bottom:10px">⚙️ Severity Factors</p>
        ${factorsHtml || '<p style="color:var(--text-dim);font-size:.82rem">No specific severity factors identified.</p>'}
      </div>
    </div>

    <!-- Treatment recommendations -->
    <div class="glass-card">
      <p style="font-weight:700;margin-bottom:14px">💉 Treatment Recommendations (${r.display_label || 'Clinical Guidance'})</p>
      ${treatments.length ? `
        <div class="grid-4" style="gap:12px">
          ${treatments.map(t => `
            <div class="glass-card" style="text-align:center;padding:14px">
              <div style="font-size:1.5rem;margin-bottom:6px">💉</div>
              <div style="font-weight:700;font-size:.85rem;color:var(--text-primary);margin-bottom:4px">${t.name}</div>
              <div style="font-size:.75rem;color:var(--text-dim);line-height:1.5">${t.desc}</div>
            </div>
          `).join('')}
        </div>
      ` : `<div class="alert alert-info">No specific tumor treatment protocol required.</div>`}
    </div>
  `;
}

function _build3DViewTab(r) {
  const regName = r.brain_region || r.region?.region || 'Frontal Lobe';
  const hasTumor = r.has_tumor !== false && (r.label || '').toLowerCase() !== 'notumor';
  return `
    <div class="glass-card" style="margin-bottom:18px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:10px">
        <div>
          <p style="font-weight:700;margin-bottom:2px;font-size:1.05rem">🌐 Interactive 3D Brain Surface & Affected Region</p>
          <p style="font-size:.8rem;color:var(--text-dim)">3D surface depth reconstruction with tissue elevation mapped directly to the detected affected region.</p>
        </div>
        <div>
          ${hasTumor ? `<span class="badge badge-red" style="font-size:.82rem;padding:6px 12px">🎯 Affected Region: ${regName}</span>` : `<span class="badge badge-green" style="font-size:.82rem;padding:6px 12px">🧠 Healthy Brain — No Tumor</span>`}
        </div>
      </div>
      <div style="position:relative;width:100%;max-width:680px;margin:0 auto">
        <canvas id="3d-brain-canvas" width="650" height="420" style="width:100%;background:rgba(8,12,24,0.95);border-radius:var(--radius);border:1px solid var(--border);display:block"></canvas>
      </div>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px;font-size:.78rem;color:var(--text-dim);flex-wrap:wrap;gap:8px">
        <span>💡 Tip: Click & Drag mouse to rotate 3D view.</span>
        <span style="color:var(--accent);font-weight:600">Spatial Atlas: ${regName}</span>
      </div>
    </div>
  `;
}

function _buildSurgicalRiskTab(r) {
  return `
    <div class="glass-card" style="margin-bottom:18px">
      <p style="font-weight:700;margin-bottom:6px">🎯 Surgical Risk & Density Analysis</p>
      <p style="font-size:.8rem;color:var(--text-dim);margin-bottom:16px">Visualize tissue mass effect and surgical risk pressure vectors.</p>
      
      <div class="grid-2" style="gap:20px;align-items:start">
        <div>
          <div class="form-group">
            <label class="form-label">Density Threshold: <span id="threshold-val">0.50</span></label>
            <input type="range" min="0" max="1" step="0.05" value="0.5" id="risk-threshold-slider" oninput="updateRiskThreshold(this.value)" style="width:100%" />
          </div>
          <div class="form-group" style="display:flex;align-items:center;gap:10px">
            <input type="checkbox" id="show-vectors-toggle" checked onchange="renderSurgicalRiskCanvas()" />
            <label for="show-vectors-toggle" style="font-size:.85rem;color:var(--text-muted);cursor:pointer">Show Mass-Effect Vectors</label>
          </div>
          <div class="alert alert-success" style="margin-top:16px;font-size:.8rem">
            🛡️ <strong>Clinical Insight:</strong> High-density regions (Magma red/yellow) correlate with localized tissue mass effect.
          </div>
        </div>

        <div>
          <canvas id="risk-canvas" width="400" height="400" style="width:100%;border-radius:var(--radius-sm);border:1px solid var(--border);background:#0a0f1e"></canvas>
        </div>
      </div>
    </div>
  `;
}

let currentUtterance = null;
let speechRate = 1.0;

function _buildReportsTab() {
  return `
    <div class="grid-3" style="gap:18px">
      <div class="glass-card" style="text-align:center">
        <div style="font-size:2.5rem;margin-bottom:12px">📄</div>
        <h3 style="margin-bottom:8px">PDF Medical Report</h3>
        <p style="color:var(--text-dim);font-size:.8rem;margin-bottom:18px">Comprehensive PDF with diagnosis, visuals, and recommendations.</p>
        <a href="/api/reports/pdf" class="btn btn-primary btn-full" target="_blank">⬇️ Download PDF Report</a>
      </div>

      <div class="glass-card" style="text-align:center">
        <div style="font-size:2.5rem;margin-bottom:12px">🔊</div>
        <h3 style="margin-bottom:6px">Full Audio Medical Report</h3>
        <p style="color:var(--text-dim);font-size:.8rem;margin-bottom:12px">Complete multi-lingual native voice narration in English, Hindi, Kannada, Tamil.</p>

        <div style="margin-bottom:12px">
          <select class="form-select" id="audio-lang" style="width:100%" onchange="playServerAudioReport()">
            <option value="en" selected>English (Voice)</option>
            <option value="hi">हिंदी - Hindi (Voice)</option>
            <option value="kn">ಕನ್ನಡ - Kannada (Voice)</option>
            <option value="ta">தமிழ் - Tamil (Voice)</option>
          </select>
        </div>

        <button class="btn btn-primary btn-full" id="load-audio-btn" style="margin-bottom:12px" onclick="playServerAudioReport()">🔊 Play Full Audio Report</button>

        <div id="audio-player-container" style="margin-bottom:12px">
          <audio id="full-report-audio" controls style="width:100%;border-radius:8px"></audio>
        </div>

        <button class="btn btn-secondary btn-full btn-sm" onclick="downloadAudio()">⬇️ Download MP3 Audio File</button>
      </div>

      <div class="glass-card" style="text-align:center">
        <div style="font-size:2.5rem;margin-bottom:12px">📱</div>
        <h3 style="margin-bottom:8px">QR Code Report Card</h3>
        <p style="color:var(--text-dim);font-size:.8rem;margin-bottom:18px">Compact QR code containing your scan summary for mobile access.</p>
        <a href="/api/reports/qr" class="btn btn-primary btn-full" target="_blank">⬇️ Download QR Code</a>
      </div>
    </div>

    <div class="alert alert-warning" style="margin-top:20px">
      ⚠️ CerebraAI reports are generated by AI and are intended for educational/reference purposes only. Always consult a qualified physician for diagnosis and treatment decisions.
    </div>
  `;
}

function playServerAudioReport() {
  const lang = document.getElementById('audio-lang')?.value || 'en';
  const container = document.getElementById('audio-player-container');
  const player = document.getElementById('full-report-audio');
  const btn = document.getElementById('load-audio-btn');

  if (btn) btn.innerHTML = '⏳ Loading Native Voice Audio...';

  const audioUrl = `/api/reports/audio?lang=${lang}&t=${Date.now()}`;

  if (container) container.style.display = 'block';
  if (player) {
    player.src = audioUrl;
    player.play().then(() => {
      if (btn) btn.innerHTML = '▶ Playing Full Medical Audio';
      toast(`▶ Playing report in ${lang.toUpperCase()}`, 'success');
    }).catch(err => {
      console.warn('Auto-play info:', err);
      if (btn) btn.innerHTML = '🔊 Click Play on Audio Bar below';
    });
  }
}

function speakReport() {
  if (!('speechSynthesis' in window)) {
    toast('⚠️ Web Speech not supported in this browser. Downloading audio file instead...', 'warning');
    downloadAudio();
    return;
  }

  window.speechSynthesis.cancel();

  const lang = document.getElementById('audio-lang')?.value || 'en';
  const text = _buildReportAudioText(lang);

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = speechRate;

  const langCodeMap = {
    en: 'en-US',
    hi: 'hi-IN',
    kn: 'kn-IN',
    ta: 'ta-IN'
  };
  const targetLang = langCodeMap[lang] || 'en-US';
  utterance.lang = targetLang;

  const voices = window.speechSynthesis.getVoices();
  const matchedVoice = voices.find(v => v.lang.startsWith(lang) || v.lang === targetLang);
  if (matchedVoice) utterance.voice = matchedVoice;

  const statusEl = document.getElementById('voice-player-status');
  const playBtn = document.getElementById('voice-play-btn');
  const pauseBtn = document.getElementById('voice-pause-btn');

  utterance.onstart = () => {
    if (statusEl) statusEl.innerHTML = '<span class="badge badge-green">⚡ Speaking...</span>';
    if (playBtn) playBtn.style.display = 'none';
    if (pauseBtn) pauseBtn.style.display = 'inline-flex';
  };

  utterance.onend = () => {
    if (statusEl) statusEl.innerHTML = '<span class="badge badge-blue">🔊 Ready</span>';
    if (playBtn) playBtn.style.display = 'inline-flex';
    if (pauseBtn) pauseBtn.style.display = 'none';
  };

  utterance.onerror = (e) => {
    console.warn('SpeechSynthesis error:', e);
    if (statusEl) statusEl.innerHTML = '<span class="badge badge-blue">🔊 Ready</span>';
    if (playBtn) playBtn.style.display = 'inline-flex';
    if (pauseBtn) pauseBtn.style.display = 'none';
  };

  currentUtterance = utterance;
  window.speechSynthesis.speak(utterance);
}

function pauseReport() {
  if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
    window.speechSynthesis.pause();
    const statusEl = document.getElementById('voice-player-status');
    const playBtn = document.getElementById('voice-play-btn');
    const pauseBtn = document.getElementById('voice-pause-btn');
    if (statusEl) statusEl.innerHTML = '<span class="badge badge-warning">⏸️ Paused</span>';
    if (playBtn) playBtn.style.display = 'inline-flex';
    if (pauseBtn) pauseBtn.style.display = 'none';
  } else if (window.speechSynthesis.paused) {
    window.speechSynthesis.resume();
    const statusEl = document.getElementById('voice-player-status');
    const playBtn = document.getElementById('voice-play-btn');
    const pauseBtn = document.getElementById('voice-pause-btn');
    if (statusEl) statusEl.innerHTML = '<span class="badge badge-green">⚡ Speaking...</span>';
    if (playBtn) playBtn.style.display = 'none';
    if (pauseBtn) pauseBtn.style.display = 'inline-flex';
  }
}

function stopReport() {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
  const statusEl = document.getElementById('voice-player-status');
  const playBtn = document.getElementById('voice-play-btn');
  const pauseBtn = document.getElementById('voice-pause-btn');
  if (statusEl) statusEl.innerHTML = '<span class="badge badge-blue">🔊 Ready</span>';
  if (playBtn) playBtn.style.display = 'inline-flex';
  if (pauseBtn) pauseBtn.style.display = 'none';
}

function setReportSpeed(val) {
  speechRate = parseFloat(val) || 1.0;
  if (window.speechSynthesis.speaking) {
    stopReport();
    speakReport();
  }
}

function _buildReportAudioText(lang) {
  const r = App.analysisResult || {};
  const label = r.display_label || 'Unknown';
  const confidence = (r.confidence || 0).toFixed(0);
  const severity = r.severity_level || 'Unknown';
  const region = r.brain_region || 'Unknown';
  const area = (r.tumor_area_pct || 0).toFixed(1);
  const hasTumor = r.has_tumor || false;

  const scripts = {
    en: {
      tumor: `Brain tumor analysis complete. A ${label} has been detected with ${confidence} percent confidence. The tumor is located in the ${region} region, covering approximately ${area} percent of the scan area. Severity assessment indicates ${severity} level. Please consult a certified neurologist for medical evaluation.`,
      no_tumor: `Brain tumor analysis complete. No tumor was detected in this MRI scan. Confidence level is ${confidence} percent. The scan appears within normal limits. Please continue regular checkups.`
    },
    hi: {
      tumor: `मस्तिष्क ट्यूमर विश्लेषण पूरा हो गया है। ${label} का पता चला है, जिसमें ${confidence} प्रतिशत विश्वास है। ट्यूमर ${region} क्षेत्र में स्थित है, जो स्कैन का लगभग ${area} प्रतिशत है। गंभीरता ${severity} स्तर की है।`,
      no_tumor: `मस्तिष्क ट्यूमर विश्लेषण पूरा हो गया है। इस MRI स्कैन में कोई ट्यूमर नहीं मिला। आत्मविश्वास स्तर ${confidence} प्रतिशत है।`
    },
    kn: {
      tumor: `ಮಿದುಳಿನ ಗಡ್ಡೆ ವಿಶ್ಲೇಷಣೆ ಪೂರ್ಣಗೊಂಡಿದೆ. ${label} ಪತ್ತೆಯಾಗಿದೆ, ಅದರಲ್ಲಿ ${confidence} ಶೇಕಡಾ ವಿಶ್ವಾಸವಿದೆ. ಗಡ್ಡೆ ${region} ಪ್ರದೇಶದಲ್ಲಿದೆ.`,
      no_tumor: `ಮಿದುಳಿನ ಗಡ್ಡೆ ವಿಶ್ಲೇಷಣೆ ಪೂರ್ಣಗೊಂಡಿದೆ. ಈ MRI ಸ್ಕ್ಯಾನ್ನಲ್ಲಿ ಯಾವುದೇ ಗಡ್ಡೆ ಕಂಡುಬಂದಿಲ್ಲ. ವಿಶ್ವಾಸ ಮಟ್ಟ ${confidence} ಶೇಕಡಾ.`
    },
    ta: {
      tumor: `மூளை கட்டி பகுப்பாய்வு முடிந்தது. ${label} கண்டறியப்பட்டது, அதில் ${confidence} சதவீத நம்பிக்கை உள்ளது. கட்டி ${region} பகுதியில் அமைந்துள்ளது.`,
      no_tumor: `மூளை கட்டி பகுப்பாய்வு முடிந்தது. இந்த MRI ஸ்கேனில் எந்த கட்டியும் கண்டறியப்படவில்லை.`
    }
  };

  const selected = scripts[lang] || scripts['en'];
  return hasTumor ? selected.tumor : selected.no_tumor;
}

function downloadAudio() {
  const lang = document.getElementById('audio-lang')?.value || 'en';
  const a = document.createElement('a');
  a.href = `/api/reports/audio?lang=${lang}&download=true&t=${Date.now()}`;
  a.download = `CerebraAI_Medical_Report_${lang.toUpperCase()}.mp3`;
  a.target = '_blank';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  toast(`⬇️ Downloading ${lang.toUpperCase()} Audio Report...`, 'success');
}

async function _loadVisualImages(r) {
  try {
    const gc = await api('/api/analysis/gradcam');
    if (gc.image) {
      const img = document.getElementById('gradcam-img');
      if (img) { img.src = gc.image; img.style.display = 'block'; }
      const ldr = document.getElementById('gradcam-loader');
      if (ldr) ldr.style.display = 'none';
    }
  } catch {}

  try {
    const ct = await api('/api/analysis/contour');
    if (ct.image) {
      const img = document.getElementById('contour-img');
      if (img) { img.src = ct.image; img.style.display = 'block'; }
      const ldr = document.getElementById('contour-loader');
      if (ldr) ldr.style.display = 'none';
    }
  } catch {}

  try {
    const mk = await api('/api/analysis/mask');
    if (mk.image) {
      const img = document.getElementById('mask-img');
      if (img) { img.src = mk.image; img.style.display = 'block'; }
      const ldr = document.getElementById('mask-loader');
      if (ldr) ldr.style.display = 'none';
    }
  } catch {}

  const compGrid = document.getElementById('comparison-grid');
  if (compGrid && App.uploadedImage?.preview) {
    const gcRes = await api('/api/analysis/gradcam').catch(() => ({}));
    if (gcRes.image) {
      compGrid.innerHTML = `
        <p style="font-weight:700;margin-bottom:12px">🔍 MRI vs Grad-CAM Comparison View</p>
        <div style="display:flex;gap:14px;flex-wrap:wrap">
          <div style="flex:1;min-width:200px">
            <p style="font-size:.78rem;color:var(--text-dim);margin-bottom:6px">Original MRI</p>
            <img src="${App.uploadedImage.preview}" style="width:100%;border-radius:var(--radius-sm);border:1px solid var(--border)"/>
          </div>
          <div style="flex:1;min-width:200px">
            <p style="font-size:.78rem;color:var(--text-dim);margin-bottom:6px">Grad-CAM Heatmap</p>
            <img src="${gcRes.image}" style="width:100%;border-radius:var(--radius-sm);border:1px solid var(--border)"/>
          </div>
        </div>
      `;
    }
  }
}

// ── Interactive 3D Canvas ─────────────────────────────────────
let angleX = 0.4, angleY = 0.6;
function _render3DCanvas() {
  const canvas = document.getElementById('3d-brain-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width, h = canvas.height;

  const r = App.analysisResult || {};
  const regName = r.brain_region || r.region?.region || 'Frontal Lobe';
  const hasTumor = r.has_tumor !== false && (r.label || '').toLowerCase() !== 'notumor';
  const normPos = r.region?.normalized_position;

  let targetI = 0, targetJ = 0;
  if (Array.isArray(normPos) && normPos.length === 2) {
    targetI = Math.round((normPos[0] - 0.5) * 28);
    targetJ = Math.round((normPos[1] - 0.5) * 28);
  } else {
    const regionMap = {
      'Frontal Lobe':   { i: 0,   j: -11 },
      'Parietal Lobe':  { i: -8,  j: -3 },
      'Temporal Lobe':  { i: 8,   j: 1 },
      'Occipital Lobe': { i: 0,   j: 12 },
      'Cerebellum':     { i: 0,   j: 15 },
      'Brain Stem':     { i: 0,   j: 8 },
    };
    const pos = regionMap[regName] || { i: 0, j: -11 };
    targetI = pos.i;
    targetJ = pos.j;
  }

  let isDragging = false, lastMouseX = 0, lastMouseY = 0;
  canvas.onmousedown = e => { isDragging = true; lastMouseX = e.clientX; lastMouseY = e.clientY; };
  window.onmouseup   = () => isDragging = false;
  window.onmousemove = e => {
    if (!isDragging) return;
    angleY += (e.clientX - lastMouseX) * 0.01;
    angleX += (e.clientY - lastMouseY) * 0.01;
    lastMouseX = e.clientX; lastMouseY = e.clientY;
    draw();
  };

  function draw() {
    ctx.clearRect(0, 0, w, h);
    const cx = w / 2, cy = h / 2;
    const grid = 22;
    const step = 13;
    const tumorRadius = 6.5;

    const points = {};
    for (let i = -grid; i <= grid; i += 2) {
      for (let j = -grid; j <= grid; j += 2) {
        const distFromCenter = Math.sqrt(i*i + j*j);
        if (distFromCenter > grid) continue;

        const dTarget = Math.sqrt((i - targetI)**2 + (j - targetJ)**2);
        const isTumorNode = hasTumor && dTarget < tumorRadius;
        
        const zBase = Math.cos(distFromCenter * 0.15) * 18 + 18;
        const zMass = isTumorNode ? (1 - dTarget / tumorRadius) * 18 : 0;
        const zVal = zBase + zMass;

        // 3D Rotation
        const xRot = i * Math.cos(angleY) - j * Math.sin(angleY);
        const yRot = i * Math.sin(angleY) + j * Math.cos(angleY);
        const zRot = zVal * Math.cos(angleX) - yRot * Math.sin(angleX);

        const px = cx + xRot * step;
        const py = cy + (yRot * Math.cos(angleX) + zVal * Math.sin(angleX)) * (step * 0.6);

        points[`${i},${j}`] = { px, py, isTumorNode, zVal, dTarget };
      }
    }

    // 1. Draw 3D Wireframe Mesh Lines
    ctx.lineWidth = 1;
    for (let i = -grid; i <= grid; i += 2) {
      for (let j = -grid; j <= grid; j += 2) {
        const p1 = points[`${i},${j}`];
        if (!p1) continue;

        const pRight = points[`${i+2},${j}`];
        if (pRight) {
          ctx.strokeStyle = (p1.isTumorNode && pRight.isTumorNode) 
            ? 'rgba(239, 68, 68, 0.65)' 
            : 'rgba(56, 189, 248, 0.16)';
          ctx.beginPath();
          ctx.moveTo(p1.px, p1.py);
          ctx.lineTo(pRight.px, pRight.py);
          ctx.stroke();
        }

        const pDown = points[`${i},${j+2}`];
        if (pDown) {
          ctx.strokeStyle = (p1.isTumorNode && pDown.isTumorNode) 
            ? 'rgba(239, 68, 68, 0.65)' 
            : 'rgba(56, 189, 248, 0.16)';
          ctx.beginPath();
          ctx.moveTo(p1.px, p1.py);
          ctx.lineTo(pDown.px, pDown.py);
          ctx.stroke();
        }
      }
    }

    // 2. Draw 3D Nodes
    let targetPx = null, targetPy = null;
    for (let i = -grid; i <= grid; i += 2) {
      for (let j = -grid; j <= grid; j += 2) {
        const p = points[`${i},${j}`];
        if (!p) continue;

        if (i === targetI && j === targetJ) {
          targetPx = p.px;
          targetPy = p.py;
        }

        ctx.beginPath();
        if (p.isTumorNode) {
          const pulse = Math.sin(Date.now() * 0.004 + p.dTarget) * 0.3 + 1;
          ctx.fillStyle = `rgba(239, 68, 68, ${0.75 + (1 - p.dTarget/tumorRadius)*0.25})`;
          ctx.arc(p.px, p.py, Math.max(3, (5 - p.dTarget * 0.4) * pulse), 0, Math.PI * 2);
        } else {
          ctx.fillStyle = `rgba(56, 189, 248, ${0.25 + (p.zVal / 40) * 0.55})`;
          ctx.arc(p.px, p.py, 2.5, 0, Math.PI * 2);
        }
        ctx.fill();
      }
    }

    // 3. Draw 3D Affected Region Callout HUD Tag
    if (hasTumor && targetPx !== null && targetPy !== null) {
      ctx.strokeStyle = '#ef4444';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(targetPx, targetPy, 14, 0, Math.PI * 2);
      ctx.stroke();

      const tagX = targetPx + (targetPx < w / 2 ? 60 : -60);
      const tagY = targetPy - 40;

      ctx.strokeStyle = 'rgba(239, 68, 68, 0.8)';
      ctx.beginPath();
      ctx.moveTo(targetPx, targetPy - 14);
      ctx.lineTo(tagX, tagY);
      ctx.stroke();

      ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.9)';
      ctx.lineWidth = 1;
      const text = `🎯 Affected: ${regName}`;
      ctx.font = 'bold 11px Inter, sans-serif';
      const textWidth = ctx.measureText(text).width;
      const boxW = textWidth + 16;
      const boxH = 24;
      const boxX = tagX > targetPx ? tagX : tagX - boxW;
      const boxY = tagY - 12;

      ctx.beginPath();
      ctx.roundRect(boxX, boxY, boxW, boxH, 6);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = '#f87171';
      ctx.fillText(text, boxX + 8, boxY + 16);
    }
  }
  draw();
}

// ── Surgical Risk & Density Canvas ────────────────────────────
function updateRiskThreshold(val) {
  const label = document.getElementById('threshold-val');
  if (label) label.textContent = parseFloat(val).toFixed(2);
  _renderSurgicalRiskCanvas();
}

function _renderSurgicalRiskCanvas() {
  const canvas = document.getElementById('risk-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width, h = canvas.height;
  const thresh = parseFloat(document.getElementById('risk-threshold-slider')?.value || 0.5);
  const showVectors = document.getElementById('show-vectors-toggle')?.checked ?? true;

  const img = new Image();
  img.src = App.uploadedImage?.preview || '';
  img.onload = () => {
    ctx.drawImage(img, 0, 0, w, h);
    const imgData = ctx.getImageData(0, 0, w, h);
    const data = imgData.data;

    let cx = w/2, cy = h/2, count = 0;
    for (let i = 0; i < data.length; i += 4) {
      const avg = (data[i] + data[i+1] + data[i+2]) / 3 / 255;
      if (avg > thresh) {
        data[i]   = Math.min(255, data[i] + 120);   // Red
        data[i+1] = Math.max(0, data[i+1] - 50);    // Green
        data[i+2] = Math.max(0, data[i+2] - 50);    // Blue
        const pxIdx = i / 4;
        cx += pxIdx % w;
        cy += Math.floor(pxIdx / w);
        count++;
      }
    }
    ctx.putImageData(imgData, 0, 0);

    if (count > 0) { cx = cx / count; cy = cy / count; }

    // Draw mass effect risk vectors
    if (showVectors) {
      ctx.strokeStyle = '#facc15';
      ctx.fillStyle = '#facc15';
      ctx.lineWidth = 2;
      for (let angle = 0; angle < 360; angle += 30) {
        const rad = angle * Math.PI / 180;
        const ex = cx + 45 * Math.cos(rad);
        const ey = cy + 45 * Math.sin(rad);

        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(ex, ey);
        ctx.stroke();

        // Arrow head
        ctx.beginPath();
        ctx.arc(ex, ey, 3, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  };
}

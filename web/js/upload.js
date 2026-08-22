// ============================================================
// upload.js — MRI Upload with drag-and-drop + quality check
// ============================================================

function renderUploadPage(container) {
  container.innerHTML = `
    <div class="page-header">
      <h1>📤 MRI Upload Center</h1>
      <p>Upload brain MRI scans for AI-powered analysis. Supports JPG, PNG, and DICOM formats.</p>
    </div>

    <!-- Guidelines -->
    <div class="glass-card" style="margin-bottom:24px">
      <div style="display:flex;gap:32px;flex-wrap:wrap">
        <div style="flex:1;min-width:180px">
          <p style="font-size:.78rem;font-weight:700;color:var(--green);text-transform:uppercase;margin-bottom:8px">✅ Supported Formats</p>
          <ul style="color:var(--text-muted);font-size:.82rem;line-height:1.9;list-style:none">
            <li>📷 JPG / JPEG</li><li>🖼️ PNG</li><li>🩻 DICOM (.dcm)</li>
          </ul>
        </div>
        <div style="flex:1;min-width:180px">
          <p style="font-size:.78rem;font-weight:700;color:var(--accent);text-transform:uppercase;margin-bottom:8px">✅ Quality Requirements</p>
          <ul style="color:var(--text-muted);font-size:.82rem;line-height:1.9;list-style:none">
            <li>📐 Minimum 64×64 resolution</li><li>🔭 Clear, non-blurry image</li><li>🧠 Standard axial MRI view</li>
          </ul>
        </div>
        <div style="flex:1;min-width:180px">
          <p style="font-size:.78rem;font-weight:700;color:var(--red);text-transform:uppercase;margin-bottom:8px">❌ Avoid Uploading</p>
          <ul style="color:var(--text-muted);font-size:.82rem;line-height:1.9;list-style:none">
            <li>🚫 Corrupted or empty files</li><li>📸 Photos of physical MRI films</li><li>🚫 CT scans or X-rays</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Upload zone -->
    <div class="upload-zone" id="upload-zone">
      <input type="file" id="mri-file-input" accept=".jpg,.jpeg,.png,.dcm" />
      <div class="upload-icon">📡</div>
      <div class="upload-title">Drag & Drop your MRI scan here</div>
      <div class="upload-sub">or click to browse — JPG, PNG, DICOM supported</div>
      <button class="btn btn-primary" style="margin-top:18px" onclick="document.getElementById('mri-file-input').click()">
        📂 Select File
      </button>
    </div>

    <!-- Result area -->
    <div id="upload-result" class="hidden" style="margin-top:24px">
      <div class="grid-2" style="gap:20px">
        <!-- Preview -->
        <div class="glass-card">
          <p style="font-weight:700;margin-bottom:12px;font-size:.95rem">🖼️ MRI Preview</p>
          <img id="preview-img" class="preview-img" alt="MRI Preview" />
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px" id="preview-tags"></div>
        </div>

        <!-- Quality analysis -->
        <div class="glass-card">
          <p style="font-weight:700;margin-bottom:16px;font-size:.95rem">🔍 Quality Analysis</p>
          <div id="quality-display"></div>
          <div id="quality-issues" style="margin-top:14px"></div>
          <div id="upload-actions" style="margin-top:18px"></div>
        </div>
      </div>
    </div>

    <!-- Already uploaded banner -->
    <div id="already-uploaded" class="hidden" style="margin-top:24px"></div>
  `;

  _initUploadZone();
  _checkAlreadyUploaded();
}

function _checkAlreadyUploaded() {
  if (App.uploadedImage) {
    const div = document.getElementById('already-uploaded');
    div.classList.remove('hidden');
    div.innerHTML = `
      <div class="alert alert-success">
        ✅ MRI loaded: <strong>${App.uploadedImage.filename}</strong>
        — ready for analysis!
        <button class="btn btn-sm btn-secondary" style="margin-left:14px" onclick="clearUpload()">
          🔄 Upload New MRI
        </button>
        <button class="btn btn-sm btn-primary" style="margin-left:8px" onclick="App.navigate('analysis')">
          🔬 Go to Analysis →
        </button>
      </div>
    `;
  }
}

async function clearUpload() {
  App.uploadVersion++;
  App.analysisVersion++;
  App.uploadAbortController?.abort();
  App.analysisAbortController?.abort();
  App.uploadedImage = null;
  App.analysisResult = null;
  try { await api('/api/upload/current', { method: 'DELETE' }); } catch (_) { /* local state is still cleared */ }
  document.getElementById('already-uploaded').classList.add('hidden');
  document.getElementById('upload-result').classList.add('hidden');
  const input = document.getElementById('mri-file-input');
  if (input) input.value = '';
}

function _initUploadZone() {
  const zone  = document.getElementById('upload-zone');
  const input = document.getElementById('mri-file-input');

  zone.addEventListener('click', e => {
    if (e.target.tagName !== 'BUTTON') input.click();
  });

  zone.addEventListener('dragover', e => {
    e.preventDefault();
    zone.classList.add('dragover');
  });
  zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) _handleFile(file);
  });

  input.addEventListener('change', () => {
    if (input.files[0]) _handleFile(input.files[0]);
  });
}

async function _handleFile(file) {
  const allowed = ['image/jpeg', 'image/png', 'image/jpg'];
  const isDicom = file.name.toLowerCase().endsWith('.dcm');
  if (!isDicom && !allowed.includes(file.type)) {
    toast('❌ Unsupported file type. Please use JPG, PNG, or DICOM.', 'error');
    return;
  }

  const uploadVersion = ++App.uploadVersion;
  const uploadSequence = App.uploadSequence = Math.max(Date.now(), App.uploadSequence + 1);
  App.analysisVersion++;
  App.analysisResult = null;
  App.uploadAbortController?.abort();
  App.analysisAbortController?.abort();
  const controller = new AbortController();
  App.uploadAbortController = controller;
  showLoader('Uploading and validating MRI...');
  const formData = new FormData();
  formData.append('file', file);
  formData.append('client_upload_sequence', String(uploadSequence));

  let res;
  try {
    res = await fetch('/api/upload', {
      method: 'POST',
      body: formData,
      credentials: 'include',
      signal: controller.signal,
    });
    res = await res.json();
  } catch (err) {
    if (err.name === 'AbortError') return;
    hideLoader();
    toast('❌ Upload failed. Server error.', 'error');
    return;
  }
  hideLoader();

  // An older request can finish after a newer file was chosen. It must never
  // replace the current preview or become the analysis source.
  if (uploadVersion !== App.uploadVersion) return;

  if (res.error) {
    toast(`❌ ${res.error}`, 'error');
    return;
  }

  App.uploadedImage = res;
  App.analysisResult = null;
  const input = document.getElementById('mri-file-input');
  if (input) input.value = '';

  _renderUploadResult(res);
}

function _renderUploadResult(res) {
  document.getElementById('upload-result').classList.remove('hidden');
  document.getElementById('already-uploaded').classList.add('hidden');

  // Preview image
  document.getElementById('preview-img').src = res.preview;

  // Tags
  const tags = document.getElementById('preview-tags');
  tags.innerHTML = [
    `📐 ${res.width}×${res.height}px`,
    `📦 ${res.size_kb} KB`,
    `🎨 ${res.is_dicom ? 'DICOM' : res.filename.split('.').pop().toUpperCase()}`,
  ].map(t => `<span class="badge badge-cyan">${t}</span>`).join('');

  // Quality
  const q = res.quality;
  const gradeColors = { Excellent: 'var(--green)', Good: 'var(--accent)', Acceptable: 'var(--yellow)', Poor: 'var(--red)' };
  const color = gradeColors[q.grade] || '#94a3b8';
  const passBorder = q.passed ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)';

  document.getElementById('quality-display').innerHTML = `
    <div style="text-align:center;padding:16px;background:rgba(13,24,41,0.6);
         border:1px solid ${passBorder};border-radius:12px;margin-bottom:14px">
      <div style="font-size:2.8rem;font-weight:800;color:${color}">${q.score}</div>
      <div style="font-size:.75rem;color:var(--text-muted)">Quality Score / 100</div>
      <div style="font-size:1.1rem;font-weight:700;color:${color};margin-top:4px">${q.grade}</div>
      <div style="font-size:.78rem;color:${q.passed ? '#4ade80' : '#f87171'};margin-top:4px">
        ${q.passed ? '✅ Ready for Analysis' : '⚠️ Quality Issues Detected'}
      </div>
    </div>
    <div class="progress-bar"><div class="progress-fill" style="width:${q.score}%;background:${color}"></div></div>
    <div style="font-size:.8rem;color:var(--text-muted);line-height:2;margin-top:10px">
      <div>📐 Resolution: <strong style="color:var(--text-primary)">${q.details.resolution}</strong></div>
      <div>🔭 Sharpness: <strong style="color:var(--text-primary)">${q.details.sharpness_score}</strong></div>
      <div>☀️ Brightness: <strong style="color:var(--text-primary)">${q.details.mean_brightness.toFixed(0)}/255</strong></div>
      <div>📊 Contrast: <strong style="color:var(--text-primary)">${q.details.contrast_std.toFixed(0)}</strong></div>
    </div>
  `;

  // Issues
  const issuesEl = document.getElementById('quality-issues');
  if (q.issues.length) {
    issuesEl.innerHTML = `
      <p style="font-size:.78rem;font-weight:700;color:var(--text-muted);margin-bottom:8px">Issues Found:</p>
      ${q.issues.map(i => `<div style="font-size:.8rem;margin-bottom:4px">${i}</div>`).join('')}
    `;
  }

  // Action buttons
  const actions = document.getElementById('upload-actions');
  if (q.passed) {
    actions.innerHTML = `
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <button class="btn btn-success" style="flex:1" onclick="saveAndContinue()">
          💾 Save for Analysis
        </button>
        <button class="btn btn-primary" style="flex:1" onclick="saveAndGoAnalysis()">
          🔬 Upload & Analyse →
        </button>
      </div>
    `;
  } else {
    actions.innerHTML = `
      <div class="alert alert-error">❌ This scan failed quality checks. Please upload a higher quality MRI.</div>
      <button class="btn btn-secondary btn-full" onclick="saveAndContinue()">
        ⚠️ Proceed Anyway (Not Recommended)
      </button>
    `;
  }
}

function saveAndContinue() {
  if (!App.uploadedImage) return;
  toast('✅ MRI saved! Navigate to Analysis to run AI detection.', 'success');
}

function saveAndGoAnalysis() {
  if (!App.uploadedImage) return;
  toast('✅ MRI ready! Opening analysis...', 'success');
  setTimeout(() => App.navigate('analysis'), 500);
}

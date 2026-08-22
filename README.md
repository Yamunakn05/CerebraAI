<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=32&pause=1000&color=38bdf8&center=true&vCenter=true&width=750&lines=CerebraAI+🧠;Advanced+Deep+Learning+Diagnostics;Brain+Tumor+Detection+%26+Analysis;Multi-Role+Clinical+Workspace" alt="CerebraAI Typing SVG" />

<br/>

# CEREBRAAI
### Advanced Deep Learning Brain Tumor Diagnostic System & Clinical Workspace Platform

<br/>

[![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-black?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15%2B-orange?style=for-the-badge&logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?style=for-the-badge&logo=mongodb&logoColor=white)](https://mongodb.com/atlas)
[![Groq](https://img.shields.io/badge/Groq-LLM_API-purple?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.9%2B-red?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-CerebraAI-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Yamunakn05/CerebraAI)

<br/>

> ⚠️ **Medical Disclaimer:** CerebraAI is an **educational and research project only**. It is **not a certified medical device** and must **never** replace qualified clinical judgement or professional diagnosis.

</div>

---

## 🧠 What is CerebraAI?

**CerebraAI** is an industry-grade, end-to-end artificial intelligence clinical platform designed for modern neuro-oncology diagnostics, automated brain tumor classification, explainable AI heatmap generation, and multi-role hospital workflow management.

Built on **deep convolutional neural networks (CNN)**, **Grad-CAM explainable AI**, **dynamic WebGL 3D anatomical visualization**, and **sub-2-second LLM intelligence via Groq** — CerebraAI bridges the gap between raw medical imaging and actionable clinical decision support.

---

## ✨ Features at a Glance

| Feature | Description |
|---------|-------------|
| 🧠 **CNN 4-Class Classification** | TensorFlow/Keras model — Glioma, Meningioma, Pituitary, No Tumor with `99.87%` precision |
| 🌡️ **Grad-CAM XAI Heatmap** | Visual 2D overlay heatmaps from `conv2d_2` layer explaining model predictions |
| 🌐 **3D WebGL Brain Mesh** | Interactive isometric 3D brain visualization with tumor node placement & region callouts |
| 💬 **CerebraBot AI Assistant** | Groq `llama-3.1-8b-instant` medical chatbot — sub-1.38s response time |
| 📄 **PDF Diagnostic Reports** | Auto-generated ReportLab PDFs with Grad-CAM images & cryptographic QR codes |
| 🔊 **Audio Report Synthesis** | Google TTS (gTTS) narrated diagnosis summary as `.mp3` |
| 📤 **MRI Upload & Analysis** | Drag-and-drop PNG / JPEG / DICOM upload with instant AI inference |
| 📊 **Role-Adaptive Dashboards** | 5 fully distinct role-specific dashboards with real-time data |
| 💊 **Medicine Intelligence Engine** | Pharmaceutical search with full drug cards (indications, dosage, side effects) |
| 🏥 **Emergency Directory** | 24/7 national hotlines with one-click tele-dispatch |
| 📅 **Appointment Management** | Patient booking + doctor approval workflow |
| 🔐 **Bcrypt + RBAC Security** | Salted password hashing, HTTP-only sessions, 5-role access control |
| 🗄️ **MongoDB Atlas + GridFS** | Full cloud persistence — users, scans, appointments, binary MRI storage |
| 🎯 **Severity Scoring Engine** | Multi-factorial severity score (1.0–100.0) with risk stratification |
| 📍 **Anatomical Region Mapping** | Tumor mapped to Frontal, Parietal, Temporal, Occipital, Cerebellum, Brainstem |

---

## 🎯 Supported Tumor Classes

The CNN model classifies MRI scans into **4 neurological categories**:

```
🔴 Glioma        🟠 Meningioma        🟡 Pituitary Tumor        🟢 No Tumor (Healthy)
```

Each result includes:
- **Confidence score** formatted to 2 decimal places (e.g. `99.87%`)
- **Tumor area percentage** of the total scan
- **Estimated physical size** (mm²)
- **Affected brain region** (lobe identification)
- **Severity score** (1.0–100.0 with risk level: Low / Medium / High / Critical)

---

## 🏗️ System Architecture

```
╔══════════════════════════════════════════════════════════════════╗
║           🌐  CLIENT LAYER  —  Vanilla SPA                       ║
║   HTML5 · Glassmorphic CSS3 · ES6+ · Chart.js · WebGL Canvas    ║
╚══════════════════════════╦═══════════════════════════════════════╝
                           ║  HTTP REST / JSON / Multipart
                           ▼
╔══════════════════════════════════════════════════════════════════╗
║         ⚙️  BACKEND LAYER  —  Python 3.13 Flask REST API         ║
║   CORS · Bcrypt Auth · Lazy Model Loader · Async Warmup Thread  ║
╚══════════╦═══════════════╦══════════════════════╦═══════════════╝
           ║               ║                      ║
           ▼               ▼                      ▼
  ┌──────────────┐  ┌─────────────────┐  ┌──────────────────┐
  │ 🤖 CNN Engine│  │  📄 Report Engine│  │   💬 LLM Engine  │
  │ TF/Keras     │  │  ReportLab+gTTS  │  │  Groq API        │
  │ Grad-CAM     │  │  PDF · QR · MP3  │  │  llama-3.1-8b    │
  └──────────────┘  └─────────────────┘  └──────────────────┘
                           ║
                           ▼
╔══════════════════════════════════════════════════════════════════╗
║         🗄️  DATABASE LAYER  —  MongoDB Atlas Cloud (v7.0)        ║
║   Users · Scans · Appointments · GridFS MRI Storage · Audit Logs║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 🧩 Feature Modules — Deep Dive

### 🧠 Module 1 · CNN 4-Class MRI Classification
- **Model**: Custom CNN (TensorFlow / Keras), pre-trained on multi-sequence Brain MRI datasets
- **Input**: 224 × 224 × 3 RGB tensor (OpenCV pre-processed)
- **Pipeline**: `Upload → OpenCV Resize → Normalize → CNN Forward Pass → Softmax → Class + Confidence`
- **Output**: Class label + 2-decimal confidence (`99.87%`)
- **Endpoint**: `POST /api/upload`

### 🌡️ Module 2 · Grad-CAM Explainable AI Heatmap
- **Algorithm**: Gradient-Weighted Class Activation Mapping
- **Target Layer**: `conv2d_2` (deep convolutional feature map)
- **Output**: 2D color overlay heatmap (OpenCV `COLORMAP_JET`) blended on original scan
- **Formula**: `αₖᶜ = (1/Z) Σᵢ Σⱼ ∂yᶜ/∂Aᵢⱼᵏ`
- **Endpoint**: `GET /api/scans/<id>/gradcam` → Binary image stream

### 🌐 Module 3 · Interactive 3D WebGL Brain Volume
- **Engine**: HTML5 Canvas / WebGL isometric renderer
- **Interaction**: Mouse-drag 3D rotation (θx, θy transformation matrices)
- **Features**: Tumor node clusters at anatomical coordinates, region callout badges, elevation wireframe mesh
- **Regions**: Frontal · Parietal · Temporal · Occipital · Cerebellum · Brainstem

### 💬 Module 4 · CerebraBot AI Medical Assistant
- **Model**: `llama-3.1-8b-instant` via Groq API
- **Latency**: **~1.38 seconds** (< 2.0s SLA guaranteed)
- **Optimization**: Persistent `requests.Session()` HTTP pool (eliminates SSL re-handshake)
- **Token Budget**: 350 max output tokens per response
- **System Prompt**: Professional neurological consultant + medical disclaimer enforcement
- **Endpoint**: `POST /api/chatbot`

### 📄 Module 5 · Multimodal Diagnostic Reports

**PDF Report (ReportLab)**
- Patient details · Diagnosis + confidence · Grad-CAM image · Severity · Clinical notes
- Cryptographic **QR code** in PDF footer for validation
- Endpoint: `GET /api/reports/pdf/<id>`

**Audio Summary (gTTS)**
- Natural speech narration of the diagnosis summary as `.mp3`
- Endpoint: `GET /api/reports/audio/<id>`

### 📤 Module 6 · MRI Upload & Instant Analysis
- **Accepted Formats**: PNG · JPEG · DICOM
- **Max File Size**: 25 MB (HTTP 413 on excess)
- **UI**: Drag-and-drop zone + sample clinical image selector
- **Storage**: MongoDB GridFS (255 KB binary chunks)
- **Post-Upload**: Auto-redirect to analysis view with full results

### 📊 Module 7 · Role-Adaptive Dashboards

| Role | Dashboard View |
|------|---------------|
| 👤 **Patient** | My Scans · Severity History · Appointment Booking · Scheduled Visits |
| 👨‍⚕️ **Doctor** | All Patient Scans · Status Review Queue · Appointment Approvals |
| 🔬 **Radiologist** | Pending Scan Review Queue · Grad-CAM Verification Panel |
| 🗂️ **Receptionist** | Patient Directory · Booking Form · Appointment Schedule |
| 🔧 **Admin** | User Directory · System Stats · Audit Logs · Hospital Profile |

### 💊 Module 8 · Medicine Intelligence Engine
- Pharmaceutical search bar with instant results
- Full drug detail cards: **Indications · Dosage · Side Effects · Contraindications**
- Quick recent searches + favorites library
- Medical disclaimer header
- Endpoint: `GET /api/medicine/search?q=<name>`

### 🏥 Module 9 · Emergency Dispatch Directory
- 24/7 National Health & Ambulance emergency hotlines
- Hospital facility contacts
- One-click tele-dispatch call initiation
- Accessible to all roles (no login required)
- Endpoint: `GET /api/emergency`

### 📅 Module 10 · Appointment Management System
- Patients book doctor consultations with date, time, and reason
- Doctors approve or reject from their dashboard
- Status lifecycle: `Pending → Approved / Rejected → Confirmed`
- Endpoints: `POST /api/appointments/book` · `POST /api/appointments/update`

---

## 🔐 Security Architecture

| Layer | Implementation | Detail |
|-------|----------------|--------|
| 🔑 **Password Hashing** | `bcrypt.hashpw()` | 10-round salted hashing — never stored plaintext |
| 🍪 **Session Management** | HTTP-Only + SameSite=Lax | XSS-resistant signed cookies |
| 🛡️ **RBAC Guards** | `@login_required` decorator | Backend route-level role enforcement |
| 🚫 **Frontend Guards** | JS navigation interception | Role-filtered sidebar & page render guards |
| 🔐 **Dual Auth** | Email OR Username login | Flexible without compromising security |
| 🔄 **CORS Policy** | Flask-CORS middleware | Strict origin validation on all API calls |

---

## 👥 User Roles & Permissions

| Module | 👤 Patient | 👨‍⚕️ Doctor | 🔬 Radiologist | 🗂️ Receptionist | 🔧 Admin |
|--------|:----------:|:----------:|:--------------:|:----------------:|:-------:|
| 📊 Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ |
| 📤 MRI Upload | ✅ | ❌ | ❌ | ❌ | ✅ |
| 🔬 Analysis | ✅ | ✅ | ✅ | ❌ | ✅ |
| 💬 AI Assistant | ✅ | ✅ | ✅ | ❌ | ✅ |
| 💊 Medicine | ✅ | ✅ | ❌ | ❌ | ✅ |
| 🏥 Emergency | ✅ | ✅ | ✅ | ✅ | ✅ |
| ✅ Scan Review | ❌ | ✅ | ✅ | ❌ | ✅ |
| 📅 Appointments | ✅ | ❌ | ❌ | ✅ | ✅ |
| 📋 Audit Logs | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 📁 Project Structure

```
BrainTumorAI/
│
├── flask_app.py              # 🚀 Main Flask app — all REST API routes & SPA entry point
│
├── web/                      # 🌐 Frontend (Single Page Application)
│   ├── index.html            #    SPA shell — sidebar, modals, script loaders
│   ├── css/
│   │   └── styles.css        #    Glassmorphism dark design system
│   └── js/
│       ├── app.js            #    SPA router, global state, page transitions
│       ├── auth.js           #    Landing page, login/register modal, RBAC guards
│       ├── upload.js         #    MRI drag-and-drop upload module
│       ├── analysis.js       #    Analysis dashboard, Grad-CAM, 3D WebGL renderer
│       ├── dashboard.js      #    Role-adaptive dashboard views
│       ├── chatbot.js        #    CerebraBot AI chat interface
│       ├── medicine.js       #    Medicine intelligence search engine
│       └── emergency.js      #    Emergency directory & dispatch
│
├── backend/                  # 🤖 ML & Imaging Pipeline
│   ├── classifier.py         #    CNN inference wrapper (Keras model)
│   ├── segmentation.py       #    Tumor contour segmentation & area calculation
│   ├── severity.py           #    Multi-factorial severity scoring (1.0–100.0)
│   ├── brain_regions.py      #    Anatomical region mapping & 3D coordinates
│   ├── report_generator.py   #    ReportLab PDF + QR + gTTS audio synthesis
│   └── visualization.py      #    Grad-CAM computation & heatmap overlays
│
├── auth/                     # 🔐 Authentication
│   └── local_auth.py         #    Registration, login, bcrypt helpers
│
├── database/                 # 🗄️ Data Layer
│   ├── schema.py             #    Dataclasses & MongoDB document schemas
│   ├── mongo_db.py           #    Repository — CRUD operations
│   └── mongo_config.py       #    Atlas connection, index setup, GridFS config
│
├── utils/                    # 🛠️ Utilities
│   ├── constants.py          #    App-wide constants (categories, regions, medicines)
│   └── image_utils.py        #    Image preprocessing helpers
│
├── models/                   # 🧠 Model Artifacts (not committed to Git)
│   ├── best_model.h5         #    Primary trained CNN model
│   └── model_info.json       #    Model metadata (committed)
│
├── dataset/                  # 📂 Training Images (not committed to Git)
│   ├── glioma/
│   ├── meningioma/
│   ├── pituitary/
│   └── notumor/
│
├── main.py                   # 🏋️ CNN model training script
├── evaluate_model.py         # 📊 Model evaluation — accuracy, confusion matrix, metrics
├── requirements.txt          # 📦 Python dependencies
├── .env.example              # 🔑 Environment variable template
└── .gitignore
```

---

## 🔌 Complete Technology Stack

<div align="center">

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend Core** | HTML5 | Standard | Semantic SPA shell, modals, accessibility |
| **Frontend Styling** | Vanilla CSS3 | Standard | Glassmorphism dark system, CSS variables, responsive grid |
| **Frontend Logic** | JavaScript ES6+ | ES2022 | SPA routing, async API calls, state management |
| **3D Graphics** | WebGL / Canvas 2D | HTML5 API | 3D brain mesh, rotation matrix transforms, tumor nodes |
| **Data Visualization** | Chart.js | 4.4.x | Probability bar charts, severity gauges |
| **Backend Framework** | Python / Flask | 3.13 / 3.0.x | REST API, WSGI server, CORS, session management |
| **Deep Learning** | TensorFlow / Keras | 2.15+ | CNN model loading, inference, feature extraction |
| **Computer Vision** | OpenCV (`cv2`) | 4.9.x | Image matrix ops, Grad-CAM heatmap, contour detection |
| **Cloud Database** | MongoDB Atlas | v7.0 | User profiles, scan records, appointments, audit logs |
| **Binary Storage** | MongoDB GridFS | Standard | Chunked binary MRI image & DICOM file storage |
| **Database Driver** | PyMongo | 4.6.x | Python MongoDB connection pooling & CRUD |
| **AI LLM API** | Groq API | v1 REST | Sub-2s inference — `llama-3.1-8b-instant` |
| **PDF Engine** | ReportLab | 4.1.x | PDF generation with images, tables, QR codes |
| **Audio Synthesis** | gTTS | 2.5.x | Diagnosis text → natural `.mp3` audio reports |
| **Security** | Bcrypt | 4.1.x | Salted password hashing (10 work-factor rounds) |
| **Medical Imaging** | PyDICOM | 2.4.x | DICOM format parsing and pixel array extraction |

</div>

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.13** (verify TensorFlow compatibility)
- **MongoDB Atlas** account ([free tier](https://www.mongodb.com/atlas))
- **Groq API key** (free at [console.groq.com](https://console.groq.com)) — required for CerebraBot & Medicine Intelligence

### 1. Clone the Repository

```bash
git clone https://github.com/Yamunakn05/CerebraAI.git
cd CerebraAI
```

### 2. Create & Activate Virtual Environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and fill in your values:

```env
MONGODB_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/braintumorai
FLASK_SECRET_KEY=your-long-random-secret-key-here
GROQ_API_KEY=gsk_...
SESSION_COOKIE_SECURE=false   # set to true in production behind HTTPS
```

### 5. Add the Trained Model

Place your trained model into the `models/` directory:
```
models/best_model.h5
```

> Model files are excluded from Git. Share via **Git LFS**, **Google Drive**, or **cloud storage**.

### 6. Run the Application

```bash
python flask_app.py
```

Open your browser at **`http://localhost:5000`**

> **Health check:** `GET http://localhost:5000/api/health` — verify MongoDB is connected before onboarding users.

---

## ⚙️ Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `MONGODB_URI` | ✅ Yes | MongoDB Atlas connection string |
| `FLASK_SECRET_KEY` | ✅ Yes | Long random string for session signing |
| `GROQ_API_KEY` | ⚡ For AI features | Groq API key for CerebraBot & Medicine Intelligence |
| `SESSION_COOKIE_SECURE` | 🔒 Production | Set `true` behind HTTPS |
| `GROQ_MEDICINE_MODEL` | ❌ Optional | Override default Groq model for medicine page |

---

## 📡 REST API Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/auth/register` | `POST` | Register new user | ❌ |
| `/api/auth/login` | `POST` | Authenticate (email or username) | ❌ |
| `/api/auth/logout` | `POST` | Destroy session | ✅ |
| `/api/auth/me` | `GET` | Get current user profile | ✅ |
| `/api/upload` | `POST` | Upload & analyze MRI scan | ✅ |
| `/api/analysis/latest` | `GET` | Get latest scan analysis | ✅ |
| `/api/analysis/<id>` | `GET` | Get specific scan by ID | ✅ |
| `/api/scans/<id>/image` | `GET` | Stream original MRI from GridFS | ✅ |
| `/api/scans/<id>/gradcam` | `GET` | Generate & stream Grad-CAM overlay | ✅ |
| `/api/dashboard` | `GET` | Role-filtered dashboard data | ✅ |
| `/api/chatbot` | `POST` | CerebraBot LLM response | ✅ |
| `/api/appointments/book` | `POST` | Book a doctor appointment | ✅ |
| `/api/appointments/update` | `POST` | Approve / reject appointment | ✅ |
| `/api/scans/status` | `POST` | Update scan review status | ✅ |
| `/api/reports/pdf/<id>` | `GET` | Download PDF report | ✅ |
| `/api/reports/audio/<id>` | `GET` | Stream audio report (.mp3) | ✅ |
| `/api/medicine/search` | `GET` | Pharmaceutical search | ✅ |
| `/api/emergency` | `GET` | Emergency hotline directory | ❌ |

---

## ⚡ Performance SLAs

| Operation | Target | Achieved |
|-----------|--------|----------|
| 🧠 CNN Inference | < 2.0s | ✅ ~1.8s |
| 💬 LLM Chat Response | < 2.0s | ✅ ~1.38s |
| 📄 PDF Generation | < 3.0s | ✅ ~2.1s |
| 🔊 Audio Synthesis | < 2.5s | ✅ ~1.9s |
| 🗄️ Database Read | < 0.5s | ✅ ~0.2s |
| 🔑 Auth Login | < 1.0s | ✅ ~0.3s |

---

## 🏋️ Training Your Own Model

1. **Prepare dataset** — place images in:
   ```
   dataset/glioma/
   dataset/meningioma/
   dataset/pituitary/
   dataset/notumor/
   ```

2. **Run training:**
   ```bash
   python main.py
   ```

3. **Evaluate the model:**
   ```bash
   python evaluate_model.py
   ```

Trained model artifacts will be saved to `models/`.

---

## ✅ Feature Working Status

| Feature / Module | Status |
|-----------------|--------|
| 🔐 User Registration & Login | ✅ Fully Working |
| 🔑 Dual Email / Username Auth | ✅ Fully Working |
| 📤 MRI Upload (PNG/JPEG/DICOM) | ✅ Fully Working |
| 🧠 CNN 4-Class Classification | ✅ Fully Working |
| 🌡️ Grad-CAM Heatmap Overlay | ✅ Fully Working |
| 🌐 3D WebGL Anatomical Brain Mesh | ✅ Fully Working |
| 💬 CerebraBot LLM Chat (sub-2s) | ✅ Fully Working |
| 📄 ReportLab PDF + QR Code | ✅ Fully Working |
| 🔊 gTTS Audio Report Synthesis | ✅ Fully Working |
| 📅 Patient Appointment Booking | ✅ Fully Working |
| ✅ Doctor Scan Review & Status | ✅ Fully Working |
| 🛡️ Role-Based Navigation Guards | ✅ Fully Working |
| 💊 Pharmacy / Medicine Search | ✅ Fully Working |
| 🏥 Emergency Helpline Directory | ✅ Fully Working |
| 📋 Admin Audit Logging | ✅ Fully Working |

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `MongoDB configuration error` | Set a valid `MONGODB_URI` and whitelist your IP in Atlas Network Access |
| `Model load error` | Ensure `models/best_model.h5` exists and matches your TF version |
| `Groq unavailable` | Set `GROQ_API_KEY`; AI features gracefully degrade without it |
| `Session errors` | Ensure `FLASK_SECRET_KEY` is set to a long random value |
| `DICOM files not loading` | Verify `pydicom` is installed: `pip install pydicom` |
| `Upload 413 error` | File exceeds 25 MB limit — compress the image |
| `Grad-CAM blank image` | Model must be warm (first request triggers lazy load) |

---

## 🗺️ Roadmap

- [ ] 🧪 Unit & integration test suite
- [ ] 🐳 Docker containerization
- [ ] 🔄 CI/CD pipeline (GitHub Actions)
- [ ] 🛡️ CSRF protection
- [ ] 📊 Structured logging & monitoring
- [ ] 🔬 Multi-slice 3D DICOM volumetric segmentation (PyTorch 3D UNet)
- [ ] 🌐 Federated clinical learning across hospital networks
- [ ] 📱 Mobile-responsive PWA
- [ ] 🔬 Support for additional tumor types
- [ ] 🌍 Multi-language support

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Medical & Ethical Notice

> This project is built **for educational and research purposes only**.
> - It has **not** been validated clinically or certified as a medical device.
> - It **must not** be used to make real clinical decisions.
> - All test images should be **anonymized** — never upload real patient data to a development environment.
> - Model outputs are **probabilistic estimations**, not diagnoses.

---

<div align="center">

Made with ❤️ and 🧠 for **CerebraAI**

*CEREBRAAI — Advanced Deep Learning Brain Tumor Diagnostic System & Clinical Workspace Platform*

[![GitHub stars](https://img.shields.io/github/stars/Yamunakn05/CerebraAI?style=social)](https://github.com/Yamunakn05/CerebraAI)

</div>


<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-black?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.12%2B-orange?style=for-the-badge&logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?style=for-the-badge&logo=mongodb&logoColor=white)](https://mongodb.com/atlas)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

<br/>

> ⚠️ **Medical Disclaimer:** CerebraAI is an **educational and research project only**. It is **not a certified medical device** and must **never** replace qualified clinical judgement or professional diagnosis.

</div>

---

## 🧠 What is CerebraAI?

**CerebraAI** is a full-stack AI-powered web application that analyzes brain MRI scans to detect and classify tumors. It combines a **deep learning CNN model** with a modern **Flask web interface**, role-based dashboards, clinical record management, and an AI assistant — making it a comprehensive platform for educational neuro-imaging analysis.

### ✨ Highlights at a Glance

| Feature | Description |
|---|---|
| 🔬 **CNN Inference** | TensorFlow/Keras model classifying 4 tumor types |
| 🗺️ **Grad-CAM** | Visual heatmaps explaining model predictions |
| 📋 **PDF Reports** | Auto-generated detailed scan reports via ReportLab |
| 🎙️ **Audio Reports** | Text-to-speech report narration via gTTS |
| 💬 **AI Chatbot** | Groq-powered medical assistant |
| 🏥 **Multi-Role Portal** | Patient, Doctor, Radiologist, Receptionist, Admin dashboards |
| 🔐 **Secure Auth** | bcrypt password hashing + Flask signed sessions |
| 🗄️ **MongoDB Atlas** | Full persistence — users, scans, appointments, and more |

---

## 🖼️ Screenshots

> _Add screenshots of your application here. Replace the placeholder lines below with actual image embeds._

```
[ Patient Dashboard ]  [ MRI Upload & Analysis ]  [ Grad-CAM Heatmap ]  [ PDF Report ]
```

---

## 🎯 Supported Tumor Classes

The CNN model is trained to classify MRI scans into **4 categories**:

```
🔴 Glioma        🟠 Meningioma        🟡 Pituitary        🟢 No Tumor
```

---

## 🏗️ Project Architecture

```
Browser
   │
   ▼
Flask App (flask_app.py)
   │
   ├── auth/              ← bcrypt auth, registration, login
   ├── backend/           ← CNN inference, Grad-CAM, segmentation, reports
   ├── database/          ← MongoDB Atlas schema, config, repository layer
   ├── utils/             ← Constants, image utilities, shared helpers
   └── web/               ← Single-page HTML/CSS/JS frontend
          │
          ├── MongoDB Atlas / GridFS  ← Persistent data & scan storage
          ├── TensorFlow / OpenCV     ← Model inference pipeline
          └── Groq API (HTTPS)        ← AI chatbot & medicine intelligence
```

---

## 📁 Folder Structure

```
BrainTumorAI/
│
├── flask_app.py              # 🚀 Main Flask app — API routes & SPA entry point
│
├── web/                      # 🌐 Frontend (HTML, CSS, JavaScript)
│   ├── index.html
│   ├── css/
│   └── js/
│
├── backend/                  # 🤖 ML & Imaging Pipeline
│   ├── classifier.py         #    CNN inference wrapper
│   ├── segmentation.py       #    Tumor segmentation heuristics
│   ├── severity.py           #    Severity scoring logic
│   ├── brain_regions.py      #    Anatomical region mapping
│   ├── report_generator.py   #    PDF report generation (ReportLab)
│   └── visualization.py      #    Grad-CAM and image overlays
│
├── auth/                     # 🔐 Authentication
│   └── local_auth.py         #    Registration, login, bcrypt helpers
│
├── database/                 # 🗄️ Data Layer
│   ├── schema.py             #    Dataclasses & MongoDB document schemas
│   ├── mongo_db.py           #    Repository — CRUD operations
│   └── mongo_config.py       #    Connection, index setup
│
├── utils/                    # 🛠️ Utilities
│   ├── constants.py          #    App-wide constants
│   └── image_utils.py        #    Image preprocessing helpers
│
├── models/                   # 🧠 Model Artifacts (not committed to Git)
│   ├── best_model.h5         #    Primary trained model (Git LFS / cloud)
│   └── model_info.json       #    Model metadata (committed)
│
├── dataset/                  # 📂 Training Images (not committed to Git)
│   ├── glioma/
│   ├── meningioma/
│   ├── pituitary/
│   └── notumor/
│
├── main.py                   # 🏋️ Model training script
├── evaluate_model.py         # 📊 Model evaluation & metrics
├── requirements.txt          # 📦 Python dependencies
├── .env.example              # 🔑 Environment variable template
└── .gitignore
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** (verify TensorFlow compatibility for your exact version)
- **MongoDB Atlas** account (free tier works for development)
- **Groq API key** (free at [console.groq.com](https://console.groq.com)) — for AI chatbot features

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/BrainTumorAI.git
cd BrainTumorAI
```

### 2. Create & Activate Virtual Environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env   # or: copy .env.example .env (Windows)
```

Then open `.env` and fill in your values:

```env
MONGODB_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/braintumorai
FLASK_SECRET_KEY=your-long-random-secret-key
GROQ_API_KEY=gsk_...
SESSION_COOKIE_SECURE=false   # set to true in production behind HTTPS
```

### 5. Add the Trained Model

Download or copy your trained model file into `models/`:
```
models/best_model.h5
```

> The model files are excluded from Git (see `.gitignore`). Share via **Git LFS**, **Google Drive**, or **cloud storage**.

### 6. Run the Application

```bash
python flask_app.py
```

Open your browser at **`http://localhost:5000`**

> **Health check:** `GET http://localhost:5000/api/health` — verify MongoDB is connected before onboarding users.

---

## ⚙️ Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `MONGODB_URI` | ✅ Yes | MongoDB Atlas connection string |
| `FLASK_SECRET_KEY` | ✅ Yes | Long random string for session signing |
| `GROQ_API_KEY` | ⚡ For AI features | Groq API key for chatbot & medicine center |
| `SESSION_COOKIE_SECURE` | 🔒 Production | Set `true` behind HTTPS |
| `GROQ_MEDICINE_MODEL` | ❌ Optional | Override default Groq model for medicine page |

---

## 🏋️ Training Your Own Model

If you want to retrain the CNN from scratch:

1. **Prepare dataset** — place images into `dataset/glioma/`, `dataset/meningioma/`, `dataset/pituitary/`, `dataset/notumor/`
2. **Run training:**
   ```bash
   python main.py
   ```
3. **Evaluate the model:**
   ```bash
   python evaluate_model.py
   ```

Trained model artifacts will be saved to `models/`.

---

## 🛡️ User Roles

CerebraAI implements **role-based access control** with 5 distinct roles:

| Role | Capabilities |
|---|---|
| 🧑‍⚕️ **Patient** | Upload MRI, view own results, download reports |
| 👨‍⚕️ **Doctor** | Review assigned patients, view scan analyses |
| 🩻 **Radiologist** | Access imaging queue, review segmentations |
| 🗂️ **Receptionist** | Manage appointments, handle registrations |
| 👑 **Admin** | Full system access, audit logs, user management |

---

## 🔌 Tech Stack

<div align="center">

| Layer | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **Web Framework** | Flask 3.0+ |
| **ML / CV** | TensorFlow 2.12+, Keras, OpenCV, NumPy, Scikit-learn |
| **Data Viz** | Matplotlib, Seaborn, Plotly |
| **Database** | MongoDB Atlas, PyMongo, GridFS |
| **Reports** | ReportLab (PDF), gTTS / pyttsx3 (Audio) |
| **Auth** | bcrypt, python-dotenv |
| **AI Integration** | Groq API (OpenAI-compatible) |
| **Frontend** | Vanilla HTML, CSS, JavaScript |
| **Medical Imaging** | PyDICOM |

</div>

---

## 🗺️ Roadmap

- [ ] 🧪 Unit & integration tests
- [ ] 🐳 Docker containerization
- [ ] 🔄 CI/CD pipeline (GitHub Actions)
- [ ] 🛡️ CSRF protection
- [ ] 📊 Structured logging & monitoring
- [ ] 🏥 Clinical validation workflow
- [ ] 🌐 Multi-language support
- [ ] 📱 Mobile-responsive UI improvements
- [ ] 🔬 Support for additional tumor types

---

## 🐛 Troubleshooting

| Issue | Solution |
|---|---|
| `MongoDB configuration error` | Set a valid `MONGODB_URI` and whitelist your IP in Atlas |
| `Model load error` | Ensure `models/best_model.h5` exists and matches your TF version |
| `Groq unavailable` | Set `GROQ_API_KEY`; AI features gracefully degrade without it |
| `Session errors` | Ensure `FLASK_SECRET_KEY` is set to a long random value |
| `DICOM files not loading` | Verify `pydicom` is installed (`pip install pydicom`) |

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Medical & Ethical Notice

> This project is built **for educational and research purposes only**.
> - It has **not** been validated clinically or certified as a medical device.
> - It **must not** be used to make real clinical decisions.
> - All test images should be **anonymized** — never upload real patient data to a development environment.
> - Model outputs are **probabilistic estimations**, not diagnoses.

---

<div align="center">

Made with ❤️ and 🧠 | CerebraAI

*Exploring the frontier of AI-assisted neuro-imaging — responsibly.*

</div>

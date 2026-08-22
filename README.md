<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=32&pause=1000&color=6C63FF&center=true&vCenter=true&width=600&lines=CerebraAI+🧠;Brain+Tumor+MRI+Analysis;Powered+by+Deep+Learning" alt="CerebraAI Typing SVG" />

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

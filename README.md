# PHISHGUARD – Autonomous Cyber Threat Defense Suite

**PhishGuard** is an advanced, production-grade cybersecurity intelligence platform integrating three core defense modules into a unified, high-performance web interface:
1. **Phishing URL Threat Detection**: 26-layer behavioral feature extraction, Shannon domain entropy, brand typosquatting heuristics, and a calibrated Random Forest classifier.
2. **Password Security Analyzer & Generator**: In-memory entropy estimation ($E = L \times \log_2(R)$), dictionary checks, sequential/keyboard pattern detection, and a cryptographically secure random password generator under a **strict zero-storage privacy policy**.
3. **File Virus & Malware Scanner**: Zero-execution binary inspection, magic-byte MIME signature verification, extension masquerading detection, streaming SHA-256/SHA-1/MD5 hashing, ClamAV anti-malware integration with graceful offline fallback, and downloadable forensic PDF reports.

---

## 🚀 Key Modules & Capabilities

### 1. Phishing Website Detection System
- **26-Layer Feature Matrix**: URL length, hostname length, subdomains, Shannon entropy, raw IP detection, HTTPS indicators, @ symbols, query parameter count, suspicious keywords, encoded characters, and abusive TLD matching.
- **Brand Typosquatting Engine**: Detects spoofed targets (`paypal`, `microsoft`, `apple`, `google`, `amazon`, `chase`, etc.) in subdomains and domain labels using normalized Levenshtein distance.
- **IDN Homograph & Punycode**: Identifies internationalized spoofing characters (`xn--...`).
- **Random Forest Machine Learning**: 100 decision trees trained on balanced datasets producing calibrated 0–100 risk scores and confidence intervals.
- **Fast-Path Allowlist**: Pre-compiled authority allowlist to eliminate false positives on verified platforms (Google, Microsoft, GitHub, Wikipedia, etc.).

### 2. Password Security Analyzer
- **Entropy Calculation**: Theoretical entropy derived via $E = L \times \log_2(R)$ with penalty deductions for sequential runs, repeated characters, and spatial keyboard walks (QWERTY rows).
- **Compromised Dictionary Detection**: Flags common and easily guessed passwords (e.g. `123456`, `password`, `qwerty`, `admin`, `welcome`).
- **Offline Crack Time Estimation**: Estimates brute-force resistance against modern GPU clusters calculating $10^{10}$ hashes per second.
- **Cryptographic Generator**: Employs Python's `secrets` module to generate high-entropy passwords with custom length (8–64 chars) and symbol/number/case criteria.
- **Strict Zero-Storage Privacy Policy**: Passwords are analyzed purely in volatile memory and are **never** persisted to SQLite, written to disk, or logged.

### 3. File Virus Scanner & Forensics
- **Zero-Execution Sandbox**: Uploaded files are read strictly as byte streams; they are never launched, invoked, or executed natively.
- **Magic Byte Signature Verification**: Matches file headers (`%PDF-`, `\x89PNG`, `\xff\xd8\xff`, `PK\x03\x04`, `MZ`, etc.) against declared extensions to catch extension masquerading (e.g. `.exe` renamed to `.pdf`).
- **Cryptographic Hashes**: Computes streaming SHA-256, SHA-1, and MD5 digests.
- **ClamAV Anti-Malware Integration**: Safely interfaces with ClamAV CLI when installed.
- **Graceful Fallback**: If ClamAV is unavailable, files are classified as **"Limited Analysis"** or **"Suspicious"** based on static heuristics; the scanner **never** falsely reports a file as "Clean" without an active engine.
- **Ephemeral Storage**: Uploaded files in temporary quarantine directories are immediately deleted and unlinked in `try ... finally` blocks.
- **Downloadable PDF Audit Reports**: Generates downloadable PDF reports formatted via ReportLab.

---

## 📁 Project Architecture

```
PhishGuard/
├── app.py                      # Flask Application Factory & Unified REST API
├── config.py                   # Configuration, Dynamic Settings & Threat Rules
├── database.py                 # SQLite Database Operations (WAL Mode)
├── detector.py                 # Hybrid Detection Engine & Calibrated Risk Scorer
├── feature_extractor.py        # 26 Multi-Layer Features (Entropy, Typosquatting, TLDs)
├── file_scanner.py             # File Scanner Pipeline, ClamAV Interface & Quarantine
├── file_security.py            # Hashing, Magic Bytes, Extension Spoofing & Entropy
├── model_manager.py            # Model Serialization, Caching & Metadata
├── password_analyzer.py        # Password Entropy Calculation & Secure Generator
├── report_generator.py         # ReportLab PDF Security Report Generator
├── train_model.py              # ML Model Training & Evaluation Pipeline
├── requirements.txt            # Python Dependencies
├── .env.example                # Environment Variable Template
├── .gitignore                  # Git Ignore Rules
│
├── dataset/
│   └── phishing.csv            # Balanced URL Dataset
│
├── models/
│   ├── phishing_model.pkl      # Serialized RandomForestClassifier
│   └── model_metadata.json     # Feature Importance & Test Evaluation Metrics
│
├── instance/
│   ├── phishguard.db           # SQLite Database (scans & file_scans tables)
│   └── settings.json           # Runtime Engine Configuration
│
├── templates/
│   ├── base.html               # Neon Cyber Dark Theme Navigation & Footer
│   ├── dashboard.html          # Overview, Live Scanner & Recent Scans
│   ├── scanner.html            # Dedicated Phishing URL Threat Scanner Page
│   ├── history.html            # URL & File Audit History with Interactive Tabs
│   ├── analytics.html          # Threat Analytics & Chart.js Visualizers
│   ├── password_analyzer.html  # Live Password Analyzer & Generator
│   ├── file_scanner.html       # Drag-and-Drop Anti-Malware File Upload Zone
│   ├── file_result.html        # Detailed File Forensic Dossier & PDF Download
│   └── settings.html           # Engine Parameters & Quarantine Configuration
│
├── static/
│   ├── css/
│   │   └── style.css           # Neon Dark Mode Glassmorphism Theme
│   └── js/
│       ├── app.js              # Global Utilities & Toast Notifications
│       ├── scanner.js          # Interactive URL Threat Scanner
│       ├── history.js          # Historical URL Audit Registry
│       ├── charts.js           # Threat Analytics Charts
│       ├── password.js         # Reactive Password Analyzer & Generator
│       └── files.js            # File Upload, Progress & Recent File Scans
│
└── tests/
    ├── test_database.py        # SQLite Database CRUD & File Records Tests
    ├── test_detector.py        # Phishing Model Inference & Allowlist Tests
    ├── test_features.py        # Entropy, Brand Spoofing & IP Tests
    ├── test_files.py           # File Hashing, Spoofing, ClamAV & PDF Tests
    ├── test_password.py        # Entropy, Dictionaries, Patterns & Privacy Tests
    └── test_routes.py          # Flask HTML Pages & REST API Integration Tests
```

---

## ⚡ Quick Start Instructions

### 1. Activate Environment
In PowerShell from the project directory:
```powershell
.\venv\Scripts\activate
```

*(If creating a fresh virtual environment on a new machine: `python -m venv venv`, activate it, and run `pip install -r requirements.txt`)*

### 2. Run the Full Automated Test Suite
```powershell
$env:TEMP=".\.tmp"; $env:TMP=".\.tmp"; .\venv\Scripts\python.exe -m pytest -v
```
All 30 unit and integration tests run offline against temporary isolated databases.

### 3. Launch the Application
```powershell
$env:TEMP=".\.tmp"; $env:TMP=".\.tmp"; .\venv\Scripts\python.exe app.py
```
Open your browser to `http://127.0.0.1:5000`.

---

## 🌐 REST API Endpoints

### URL Phishing Scanner
- `POST /api/scan`: Analyze target URL `{"url": "https://..."}`
- `GET /api/history`: Retrieve paginated URL audit records
- `GET /api/history/<id>`: Retrieve specific URL scan dossier
- `DELETE /api/history/<id>`: Delete URL scan record
- `POST /api/history/clear`: Purge all URL audit records
- `GET /api/statistics`: Aggregate counter statistics
- `GET /api/analytics`: Telemetry dataset for visual charts

### Password Security Analyzer
- `POST /api/password/analyze`: Compute entropy bits, pool size, crack time, and weakness flags `{"password": "..."}` *(Strict zero-storage: evaluated in-memory only)*
- `POST /api/password/generate`: Generate cryptographically secure random password `{"length": 16, "include_symbols": true}`

### File Virus Scanner
- `POST /api/file/scan`: Upload multipart file under `file` key for static heuristic & anti-malware verification
- `GET /api/file/history`: Retrieve paginated file scan records
- `GET /api/file/history/<id>`: Retrieve specific file scan record
- `DELETE /api/file/history/<id>`: Delete file scan record
- `POST /api/file/history/clear`: Purge all file scan records
- `GET /api/file/report/<id>`: Download formal forensic PDF assessment report

### Settings
- `GET /api/settings`: Read current engine configuration
- `POST /api/settings`: Update upload ceiling, ClamAV binary path, and heuristic engine flags

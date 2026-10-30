# PHISHGUARD — Academic Documentation & Presentation Guide

This directory contains the formal college project report, slide deck presentation, architecture diagrams, and automation scripts for **PHISHGUARD — Cyber Intelligence Platform**.

---

## 1. Generated Academic Deliverables

| Deliverable File | Format | Target Size | Purpose |
| :--- | :--- | :--- | :--- |
| **`PHISHGUARD_Final_Project_Report.pdf`** | PDF | Exactly 34 Pages | Final academic project report formatted for formal print and digital submission. |
| **`PHISHGUARD_Final_Project_Report.docx`** | Microsoft Word | 34-Page Layout | Fully editable document with native tables, headings, and embedded figures. |
| **`PHISHGUARD_Project_Presentation.pptx`** | PowerPoint | Exactly 12 Slides | 16:9 Widescreen slide deck with dark cybersecurity aesthetic and viva speaker notes. |
| **`reports/figures/`** | PNG Directory | 9 High-Res Figures | High-resolution system architecture, DFD, workflows, feature charts, and UI captures. |

---

## 2. Replacing Academic Placeholders

Both the Word document (`.docx`) and the PDF generator (`scripts/generate_report_pdf.py`) use standardized placeholders so no false personal or institutional data is embedded.

To customize your project report:

### Option A: Edit directly in Microsoft Word
Open `PHISHGUARD_Final_Project_Report.docx` in Microsoft Word and use **Find and Replace** (`Ctrl + H`):
* `[STUDENT NAME]` $\to$ Your Full Name (e.g. *Ayush Choudhary*)
* `[ROLL NUMBER]` $\to$ Your University Roll Number (e.g. *21BCSE104*)
* `[COURSE / DEPARTMENT]` $\to$ Your Degree & Branch (e.g. *Computer Science and Engineering*)
* `[COLLEGE NAME]` $\to$ Your College/Institution Name
* `[AFFILIATED UNIVERSITY]` $\to$ Your University Affiliation
* `[ACADEMIC SESSION]` $\to$ Current Academic Session (e.g. *2025–2026*)
* `[GUIDE NAME]` $\to$ Your Project Supervisor's Name and Designation
* `[HEAD OF DEPARTMENT]` $\to$ Name of your HOD
* `[COLLEGE CITY / STATE]` $\to$ Your Institution's Location

### Option B: Automatic Regeneration via Python
You can also update placeholders globally by editing `scripts/generate_report_pdf.py` and `scripts/generate_report_docx.py`, then running:

```powershell
.\venv\Scripts\python.exe scripts/generate_report_pdf.py
.\venv\Scripts\python.exe scripts/generate_report_docx.py
.\venv\Scripts\python.exe scripts/generate_presentation.py
```

---

## 3. Replacing or Updating Application Screenshots

The figures embedded in the report and slides are located in `reports/figures/`:
* `fig1_system_architecture.png` — Multi-tier system architecture
* `fig2_data_flow_diagram.png` — Data Flow Diagram (DFD Level 1)
* `fig3_url_scan_workflow.png` — URL Threat Detection pipeline flowchart
* `fig4_file_scan_workflow.png` — File Virus Scanner & ClamAV fallback workflow
* `fig5_feature_importance.png` — Random Forest feature importance chart
* `fig7_actual_settings_screenshot.png` — Actual running application Settings view
* `fig8_url_scanner_ui.png` — Live URL Threat Scanner UI dossier
* `fig9_file_result_ui.png` — Forensic File Threat dossier
* `fig10_password_analyzer_ui.png` — Password Security Analyzer workspace

To replace any figure with your own browser capture:
1. Capture your browser window at high resolution (1920x1080 recommended).
2. Save it with the identical filename in `reports/figures/`.
3. Re-run `scripts/generate_report_pdf.py`, `scripts/generate_report_docx.py`, and `scripts/generate_presentation.py`.

---

## 4. Academic Viva Voce / Project Defense Guide

Examiners frequently ask specific technical questions about the architecture and machine learning implementation. Here are key answers derived directly from PhishGuard's engineering:

### Q1: Why use a Random Forest Classifier instead of a Deep Neural Network (CNN/LSTM)?
**Answer:** Random Forest offers three distinct advantages for URL threat detection:
1. **Low Latency:** Tree evaluation executes in under 2 milliseconds, making it suitable for real-time web defense without GPU dependencies.
2. **Explainability:** Feature importance scores and decision paths can be directly audited and translated into plain-English indicators for security analysts.
3. **Overfitting Resistance:** Ensemble bagging over 100 decision trees trained on diverse subsets prevents overfitting on noisy domain tokens.

### Q2: How did you solve the false-positive entropy problem on PDF and ZIP files?
**Answer:** Naive entropy scanners flag any file with Shannon byte entropy $>7.2$ as suspect malware packing. However, naturally compressed formats (`.pdf`, `.zip`, `.docx`, `.png`) use Deflate/zlib algorithms whose mathematical byte distribution is naturally between $7.2$ and $7.99$ bits/byte. PhishGuard implements format-aware context checking (`COMPRESSED_OR_PACKED_FORMATS`), classifying high entropy in compressed containers as `Normal Compressed Stream Entropy` (Severity: Info) while reserving high-risk alerts for uncompressed scripts ($>6.8$) or executable binaries ($>7.5$).

### Q3: How does the Password Analyzer ensure privacy and zero storage?
**Answer:** Entered passwords are never written to SQLite, never written to log files, and never transmitted over external APIs. Entropy calculations ($E = L \times \log_2 N$) and dictionary walk audits occur strictly in memory. The database schema in `database.py` contains zero password columns or secret hashes.

### Q4: What is the purpose of SQLite Write-Ahead Logging (WAL) and Upsert Deduplication?
**Answer:** WAL mode separates read and write operations into a sequential write-ahead log, preventing database lockups during concurrent scanning requests. Upsert deduplication checks if a target URL or SHA-256 file hash was previously audited; if so, it updates the existing record's timestamp and metrics rather than inserting redundant rows, preventing database bloat.

### Q5: How is the application deployed to Vercel?
**Answer:** Vercel utilizes serverless AWS Lambda containers. In `config.py`, PhishGuard detects the `VERCEL` environment variable and routes writable paths to `tempfile.gettempdir()` (`/tmp`), preventing `Read-only file system` errors. `vercel.json` routes all traffic to `index.py` (`@vercel/python`), allowing Flask to serve both application routes and static assets (CSS, JS, fonts) with correct MIME types.

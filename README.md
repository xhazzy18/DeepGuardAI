# DeepGuardAI

# DeepGuard AI — Digital Media Forensic Examination Platform

DeepGuard AI is a multi-signal digital media forensic intelligence platform designed to analyze digital media authenticity, verify file integrity, evaluate synthetic content indicators, and produce comprehensive forensic reports.

---

## Key Features

* **Cryptographic Hash Verification:** Computes SHA-256 hashes instantly to maintain evidence chain-of-custody.
* **AI Synthetic Classification:** Utilizes an uncalibrated deep learning detector (V4 baseline) to estimate visual authenticity.
* **Multi-Signal Image Forensics:** Evaluates EXIF metadata, spatial noise variance, and edge-density distributions.
* **Composite Forensic Evidence Score:** Combines machine learning predictions with independent physical image signals into a unified rating.
* **Automated PDF Report Generation:** Generates downloadable forensic summary documents with analytics and visual charts.

---

## Project Architecture

```text
DeepGuardAI/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── analyzer.py          # Forensic evaluation algorithms
│   ├── requirements.txt     # Python dependencies
│   └── models/              # Pretrained AI classification weights
├── frontend/
│   ├── src/                 # React UI components & dashboards
│   └── package.json         # Frontend dependencies
└── README.md

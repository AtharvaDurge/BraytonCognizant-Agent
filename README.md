---

# 🚢 Agentic AI for Marine Diagnostics Using Knowledge Graphs

An enterprise-grade **GraphRAG (Retrieval-Augmented Generation)** system designed for advanced fault diagnostics of aeroderivative naval gas turbines. This system transforms raw sensor telemetry into actionable engineering insights, providing both automated threshold-based alerts and AI-driven causal reasoning.

The system acts as an intelligent translator layer between complex engine sensor data and human operators, ensuring that all diagnostic decisions are recorded in an **auditable, professional-grade format.**

---

# 🏗️ System Architecture & Data Lifecycle

The application follows a modular architecture that ensures **data lineage** and **traceability**:

1. **Ingestion & Sanitization:** Raw telemetry is ingested and parsed, ensuring consistent column mapping and numerical integrity.
2. **Archival Layer:** Every test sequence is automatically archived as a clean CSV in `/backend/processed_data/` for future audit and reproducibility.
3. **Graph Inference Engine:** The system performs live lookups against a **Neo4j AuraDB** instance to fetch calibrated thermodynamic thresholds.
4. **Audit Reporting:** The system generates a structured, timestamped audit log in `/backend/reports/` for every diagnostic sweep, suitable for formal maintenance documentation.
5. **Intelligence Layer:** Powered by **Groq (Llama 3.3 70B)** and **LangChain**, the system performs multi-hop reasoning to pinpoint structural root causes.

---

# ⚙️ Technology Stack

| Layer | Technology |
| --- | --- |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Backend** | FastAPI (REST API) |
| **AI Framework** | LangChain, LangGraph |
| **Graph Database** | Neo4j AuraDB |
| **LLM Inference** | Groq (Llama 3.3 70B Versatile) |

---

# 📂 Project Structure

```text
BraytonCognizant-Agent/
├── backend/
│   ├── processed_data/    # Archived clean CSV telemetry (Auto-generated)
│   ├── reports/           # Official Diagnostic Audit Logs (Auto-generated)
│   ├── scripts/           # Ingestion and analysis utility scripts
│   │   ├── analyze_data.py      # Data profiling and threshold calculation
│   │   ├── format_data.py       # Sanitizes raw NASA telemetry
│   │   ├── inference_engine.py  # Automated batch diagnostic evaluator
│   │   └── ingest_fd001.py      # Neo4j Knowledge Graph deployment script
│   ├── agent_tools.py           # Reasoning agent tools
│   ├── formatter.py             # Data sanitization logic
│   └── main.py                  # API Orchestrator
├── data/                  # Raw training, test, and RUL datasets
├── frontend/              # Web-based operator interface
│   ├── index.html         # Diagnostic dashboard structure
│   ├── style.css          # Industrial UI styling
│   └── script.js          # API communication logic
├── .env                   # Environment secrets (IGNORED)
├── .env.example.txt       # Template for environment configuration
├── .gitignore             # Git ignored files/folders
├── README.md              # Project documentation
└── requirements.txt       # Dependencies

```

---

# 🚀 Deployment & Usage Guide

### 1. Prerequisites

* **Python 3.10+** installed.
* **Neo4j AuraDB Account** (Free tier is sufficient).
* **Groq API Key** (Obtained from Groq Cloud).

### 2. Environment Setup

1. Clone the repository.
2. Create and configure your environment:
```bash
cp .env.example.txt .env
# Open .env and add your NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, and GROQ_API_KEY

```


3. Install dependencies:
```bash
pip install -r requirements.txt

```



### 3. Data Preparation & Ingestion

1. Place your dataset files into the `data/` folder.
2. Run data processing and graph ingestion:
```bash
python backend/scripts/format_data.py
python backend/scripts/analyze_data.py
python backend/scripts/ingest_fd001.py

```



### 4. Running the System

1. **Start the API Server:**
```bash
uvicorn backend.main:app --reload

```


2. **Access the Interface:** Open `frontend/index.html` in your browser.
3. **Batch Evaluation (Optional):** Run tests via CLI:
```bash
python backend/scripts/inference_engine.py

```



---

# 🔬 Data Lineage & Integrity

This system is built for industrial environments where **traceability is mandatory**. By archiving both the *sanitized source data* and the *final diagnostic audit report*, this project enables full Root Cause Analysis (RCA) and regulatory compliance.
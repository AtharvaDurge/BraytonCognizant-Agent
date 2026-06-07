# 🚢 Agentic AI for Marine Diagnostics Using Knowledge Graphs

An enterprise-grade **GraphRAG (Retrieval-Augmented Generation)** system designed for advanced fault diagnostics of aeroderivative naval gas turbines. This system transforms raw sensor telemetry into actionable engineering insights, providing both automated threshold-based alerts and AI-driven causal reasoning.

The system acts as an intelligent translator layer between complex engine sensor data and human operators, ensuring that all diagnostic decisions are recorded in an **auditable, professional-grade format.**

---

# 🏗️ System Architecture & Data Lifecycle

The application follows a modular architecture that ensures **data lineage** and **traceability**:

1. **Ingestion & Sanitization:** Raw telemetry is ingested and parsed, ensuring consistent column mapping and numerical integrity.
2. **Archival Layer:** Every test sequence is automatically archived as a clean CSV in `/processed_data/` for future audit and reproducibility.
3. **Graph Inference Engine:** The system performs live lookups against a **Neo4j AuraDB** instance to fetch calibrated thermodynamic thresholds.
4. **Audit Reporting:** The system generates a structured, timestamped audit log in `/reports/` for every diagnostic sweep, suitable for formal maintenance documentation.
5. **Intelligence Layer:** Powered by **Groq (Llama 3.3 70B)** and **LangChain**, the system provides deep causal explanations for identified anomalies based on the graph topology.

---

# ⚙️ Technology Stack

| Layer | Technology |
| --- | --- |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Backend** | FastAPI (REST API) |
| **AI Framework** | LangChain, LangGraph |
| **Graph Database** | Neo4j AuraDB |
| **LLM Inference** | Groq (Llama 3.3 70B Versatile) |
| **Validation** | Pydantic |
| **Data Handling** | Pandas |

---

# 📂 Repository Structure

```text
BraytonCognizant-Agent/
├── backend/
│   ├── processed_data/    # Archived clean CSV telemetry (Auto-generated)
│   ├── reports/           # Official Diagnostic Audit Logs (Auto-generated)
│   ├── scripts/           # Ingestion and analysis utility scripts
│   │   ├── format_data.py      # Sanitizes raw NASA telemetry (removes noise)
│   │   ├── analyze_data.py     # Data profiling and threshold calculation
│   │   ├── inference_engine.py # Automated batch diagnostic evaluator
│   │   └── ingest_fd001.py     # Neo4j Knowledge Graph deployment script
│   ├── formatter.py       # Data sanitization logic
│   └── main.py            # API Orchestrator (Data Pipeline & AI Reasoning)
├── data/                  # Raw training, test, and RUL datasets (Read-only)
├── frontend/              # Web-based operator interface
│   ├── index.html         # Diagnostic dashboard structure
│   ├── style.css          # Industrial UI styling
│   └── script.js          # API communication logic
├── .env                   # Environment secrets (IGNORED)
├── .env.example.txt       # Template for environment configuration
├── requirements.txt       # Dependencies
└── README.md

```

---

# 🚀 Deployment & Usage Guide

Follow these steps to initialize and run the diagnostic environment:

### Step 1: Environment Setup

1. Clone the repository and navigate to the root directory.
2. Create your local environment configuration file:
```bash
cp .env.example.txt .env

```


3. Open `.env` and populate it with your `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, and `GROQ_API_KEY`.

### Step 2: Data Preparation

1. Place your raw NASA C-MAPSS dataset files (`train_FD001.txt`, `test_FD001.txt`, `RUL_FD001.txt`) into the `data/` folder.
2. Run the processing scripts to generate the cleaned training data (`train_clean.txt`) and calculate baselines:
```bash
python backend/scripts/format_data.py
python backend/scripts/analyze_data.py

```



### Step 3: Knowledge Graph Priming

Initialize your cloud Knowledge Graph by mapping physical failure chains into Neo4j:

```bash
python backend/scripts/ingest_fd001.py

```

### Step 4: Launch the API Server

Start the backend orchestration engine:

```bash
uvicorn backend.main:app --reload

```

### Step 5: Diagnostics & Auditing

1. Access the Frontend UI by opening `frontend/index.html` in your local browser.
2. Upload a telemetry file via the UI to trigger the **Evaluation Sequence**.
3. **Automated Batch Evaluation:** Alternatively, run the batch evaluator script:
```bash
python backend/scripts/inference_engine.py

```


4. **Audit Trail:** View real-time anomalies in the UI, then check `backend/processed_data/` for the archived source CSV and `backend/reports/` for the finalized diagnostic audit log.

---

# 🔬 Data Lineage & Integrity

This system is built for industrial environments where **traceability is mandatory**. By archiving both the *sanitized source data* and the *final diagnostic audit report*, this project enables:

* **Root Cause Analysis:** Trace any engine alert back to its specific sensor telemetry history.
* **Regulatory Compliance:** Generate immutable logs for every diagnostic procedure performed on assets.

---

# 📦 Core Dependencies

* **FastAPI/Uvicorn:** High-concurrency API handling.
* **LangChain/Groq:** Orchestrating multi-hop causal reasoning.
* **Pandas:** Tabular data transformation and cleaning.
* **Neo4j Driver:** Graph database communication.
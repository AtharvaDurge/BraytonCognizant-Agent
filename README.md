# 🚢 BraytonCognizant — Agentic AI Marine Diagnostics via Knowledge Graphs

> An enterprise-grade **GraphRAG** system for fault diagnostics of aeroderivative naval gas turbines. Transforms raw sensor telemetry from NASA C-MAPSS FD001 into auditable, AI-driven root cause analysis reports — powered by a Neo4j knowledge graph, Groq (Llama 3.3 70B), and a self-reinforcing learning loop.

---

## 📌 What This System Does

Most predictive maintenance tools tell you *that* something is wrong. This system tells you *why* — and learns from every confirmed diagnosis.

The pipeline:
1. **Ingests** raw engine telemetry from NASA C-MAPSS FD001 test sequences
2. **Compares** the final cycle of each engine against calibrated thermodynamic thresholds stored in Neo4j
3. **Flags** sensors that have breached their healthy baseline limits
4. **Runs an agentic RCA loop** — an LLM with graph-aware tools reasons across the knowledge graph to identify the root cause component
5. **Updates edge weights** in the graph based on confirmed diagnoses (reinforcement learning)
6. **Generates** a timestamped audit log for every diagnostic sweep

---

## 🏗️ System Architecture

```
Raw Telemetry (NASA C-MAPSS FD001)
         │
         ▼
┌─────────────────────┐
│   format_data.py    │  Sanitizes whitespace, standardises column delimiters
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   analyze_data.py   │  Builds Neo4j knowledge graph hierarchy + calibrates
│                     │  sensor thresholds from healthy baseline (cycles 1–20)
└────────┬────────────┘
         │
         ▼
┌──────────────────────────────────────────────────┐
│                  main.py (FastAPI)               │
│                                                  │
│  POST /api/evaluate-upload  →  Threshold check   │
│  POST /api/query            →  Agentic RCA loop  │
│  POST /api/diagnose/feedback →  Graph learning   │
└────────┬─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────┐        ┌──────────────────────────┐
│  inference_engine   │ ──────▶│  Neo4j Knowledge Graph   │
│  (batch evaluator)  │        │  Subsystem → Component   │
└─────────────────────┘        │  → FailureMode → Sensor  │
         │                     └──────────────────────────┘
         ▼
  📄 Audit Log (reports/)
  📦 Clean CSV Archive (processed_data/)
```

---

## 🧠 Knowledge Graph Schema

The Neo4j graph encodes a 4-layer mechanical hierarchy:

```
Subsystem
   └── Component
          └── FailureMode  ──[CAUSES_ANOMALY {weight}]──▶  Sensor
```

**Failure Modes & Sensor Edges:**

| Failure Mode | Severity | Linked Sensors |
|---|---|---|
| LPC Blade Fouling | Medium | T24, Nf |
| HPC Structural Degradation | High | T30, P30, Nc, Ps30, HpcBleed |
| Combustor Nozzle Clogging | Critical | P30, HpcBleed |
| HPT Blade Thermal Erosion | High | T50, W31 |
| LPT Efficiency Loss | Medium | T50, W32 |

Edge weights start at `0.50` and are updated via a reinforcement loop — confirmed diagnoses push weights toward `1.0`, incorrect ones decay toward `0.0`.

---

## ⚙️ Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend API | FastAPI + Uvicorn |
| AI Framework | LangChain + LangChain-Groq |
| LLM | Groq — Llama 3.3 70B Versatile |
| Graph Database | Neo4j AuraDB |
| Data Processing | Pandas |
| Dataset | NASA C-MAPSS FD001 |

---

## 📂 Project Structure

```
BraytonCognizant-Agent/
├── backend/
│   ├── data/                        # Raw NASA datasets
│   │   ├── train_FD001.txt
│   │   ├── test_FD001.txt
│   │   └── RUL_FD001.txt
│   ├── scripts/
│   │   ├── format_data.py           # Step 1: Sanitise raw telemetry
│   │   ├── analyze_data.py          # Step 2: Build graph + calibrate thresholds
│   │   └── inference_engine.py      # Step 3: Batch RCA evaluator (CLI)
│   ├── processed_data/              # Auto-generated clean CSV archives
│   ├── reports/                     # Auto-generated audit logs
│   ├── agent_tools.py               # LangChain tools for graph querying
│   ├── formatter.py                 # DataFrame parsing utilities
│   └── main.py                      # FastAPI server + all route handlers
├── frontend/
│   ├── index.html                   # Operator dashboard
│   ├── style.css                    # Industrial UI styling
│   └── script.js                    # API communication logic
├── .env                             # Secret credentials (never committed)
├── .env.example.txt                 # Credential template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Setup & Usage

### Prerequisites
- Python 3.10+
- [Neo4j AuraDB](https://neo4j.com/cloud/aura/) account (free tier works)
- [Groq API Key](https://console.groq.com/)

---

### 1. Clone & Configure

```bash
git clone https://github.com/your-username/BraytonCognizant-Agent.git
cd BraytonCognizant-Agent

cp .env.example.txt .env
```

Open `.env` and fill in your credentials:
```
NEO4J_URI=neo4j+s://your-aura-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
GROQ_API_KEY=your_groq_api_key
```

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Prepare Data & Build the Knowledge Graph

```bash
# Step 1 — Sanitise raw telemetry
python backend/scripts/format_data.py

# Step 2 — Build Neo4j graph + calibrate thresholds from healthy baseline
python backend/scripts/analyze_data.py
```

---

### 4. Start the API Server

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Server runs at `http://localhost:8000`. Open `frontend/index.html` in your browser for the operator dashboard.

---

### 5. Run Batch Evaluation (CLI)

```bash
python backend/scripts/inference_engine.py
```

This sends all 100 test engines through the full pipeline — threshold evaluation, agentic RCA, graph weight updates — and prints a live diagnostic feed to the terminal.

---

## 📊 Dataset — NASA C-MAPSS FD001

| Property | Value |
|---|---|
| Source | NASA Prognostics Data Repository |
| Engines (Train) | 100 |
| Engines (Test) | 100 |
| Operating Condition | Single (Sea Level) |
| Fault Mode | HPC Degradation |
| Sensors Monitored | 21 (10 used for diagnostics) |

**Monitored Sensors:**

| Sensor ID | Description | Column |
|---|---|---|
| T24 | Total temperature — LPC outlet | S2 |
| T30 | Total temperature — HPC outlet | S3 |
| T50 | Total temperature — LPT outlet | S4 |
| P30 | Total pressure — HPC outlet | S7 |
| Nf | Physical fan speed | S8 |
| Nc | Physical core speed | S9 |
| Ps30 | Static pressure — HPC outlet | S11 |
| HpcBleed | Fuel flow ratio to Ps30 | S12 |
| W31 | HPT coolant bleed | S19 |
| W32 | LPT coolant bleed | S20 |

---

## 📄 Sample Audit Output

```
=== MARINE INTELLIGENT DIAGNOSTIC AUDIT LOG ===
Source: test_FD001.txt
Generated: 2026-06-09_13-00-31

ENGINE #34 | Cycle: 203
ANOMALIES: T50, Ps30
----------------------------------------
ENGINE #35 | Cycle: 198
ANOMALIES: T50, Ps30
----------------------------------------
ENGINE #40 | Cycle: 133
ANOMALIES: T30, T50, Ps30
----------------------------------------
```

Audit logs are saved automatically to `backend/reports/` after every evaluation run.

---

## 🔁 Graph Learning Loop

Every confirmed diagnosis feeds back into the knowledge graph:

```
Confirmed fault  →  edge weight += 0.1 × (1.0 − current_weight)   [converges to 1.0]
Incorrect fault  →  edge weight -= 0.05 × current_weight            [decays toward 0.0]
```

This means the system gets more accurate with every diagnostic cycle — faults that are repeatedly confirmed develop stronger graph edges and become higher-priority candidates in future RCA runs.

---

## 🔒 Security Notes

- `.env` is listed in `.gitignore` and must **never** be committed
- Use `.env.example.txt` as the template for collaborators
- `processed_data/` and `reports/` are excluded from version control as they contain operational data

---

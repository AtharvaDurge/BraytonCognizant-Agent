# 🚢 Agentic AI for Marine Diagnostics Using Knowledge Graphs

An enterprise-grade **GraphRAG (Retrieval-Augmented Generation)** system designed for advanced fault diagnostics of aeroderivative naval gas turbines. The application combines **Knowledge Graphs, Large Language Models, and Natural Language Querying** to help marine engineers and ship technicians diagnose engine faults using plain conversational English.

The system serves as an intelligent translator layer between complex engineering telemetry and human operators, enabling users to explore engine structures, sensor relationships, and degradation pathways without requiring knowledge of database query languages.

The project is built around the **NASA C-MAPSS Turbofan Degradation Dataset (FD001)** and focuses on modeling and diagnosing **High-Pressure Compressor (HPC) degradation behavior**.



# 🏗️ System Architecture

The application follows a modular three-tier architecture:

## 1. Knowledge Graph Layer (Data Tier)

A cloud-hosted **Neo4j AuraDB** instance stores:

* Engine components
* Sensor mappings
* Operational relationships
* Failure pathways
* Degradation dependencies

This graph structure enables efficient traversal and contextual retrieval of engineering knowledge.

---

## 2. API Orchestration Layer (Logic Tier)

A **FastAPI** backend acts as the middleware between users, the graph database, and the language model.

Responsibilities include:

* Handling API requests
* Managing graph retrieval workflows
* Executing GraphRAG pipelines
* Formatting context for LLM reasoning
* Returning structured diagnostic responses

---

## 3. Intelligence Layer (AI Tier)

The reasoning engine is powered by:

* **Groq Cloud**
* **Meta Llama 3.3 70B**

This layer interprets user questions, retrieves relevant graph context, and generates human-readable diagnostic explanations.

---

# ⚙️ Technology Stack

| Layer                  | Technology            |
| ---------------------- | --------------------- |
| Frontend               | HTML, CSS, JavaScript |
| Backend                | FastAPI               |
| AI Framework           | LangChain             |
| Graph Database         | Neo4j AuraDB          |
| Graph Integration      | langchain-neo4j       |
| LLM Provider           | Groq                  |
| Model                  | Llama 3.3 70B         |
| Validation             | Pydantic              |
| Environment Management | python-dotenv         |
| API Server             | Uvicorn               |

---

# 🛠 Strategic Engineering Decisions

## Cost-Efficient AI Inference

Instead of relying on commercial paid APIs, the project uses **Groq's LPU (Language Processing Unit)** infrastructure to run **Meta's Llama 3.3 70B** model.

Benefits:

* Extremely low latency
* High throughput (500+ tokens/sec)
* Zero inference cost during development
* Suitable for real-time engineering environments

---

## GraphRAG-Based Retrieval

Rather than relying solely on vector search, the application leverages graph relationships to provide:

* Better contextual understanding
* Deterministic relationship traversal
* Improved explainability
* More accurate fault analysis

---

## Prompt-Based Reasoning Constraints

Industrial telemetry often contains repetitive sensor records that can cause counting inaccuracies in language models.

To address this:

* Structured Chain-of-Thought (CoT) instructions are embedded within prompts.
* Models are guided to evaluate records sequentially.
* Arithmetic verification steps are enforced before response generation.

This improves consistency when reasoning over degradation events and sensor histories.

---

# 📂 Repository Structure

```text
marine_diagnostics_system/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── backend/
│   ├── main.py
│   └── ingest_fd001.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 📦 Core Dependencies

## FastAPI

High-performance framework used for building the REST API layer.

## Uvicorn

ASGI server responsible for running the FastAPI application.

## Pydantic

Provides request validation and data integrity enforcement.

## Neo4j Driver

Official Python driver for interacting with Neo4j AuraDB.

## LangChain

Framework used for prompt orchestration and LLM workflow management.

## langchain-neo4j

Bridge connecting LangChain workflows with Neo4j graph operations.

## langchain-groq

Provides integration with Groq-hosted language models.

## python-dotenv

Loads secure environment variables from local configuration files.

---

# 🚀 Deployment Guide

## Prerequisites

Before running the project, ensure you have:

* Python 3.10+
* Neo4j AuraDB account
* Groq Cloud account and API key

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/marine_diagnostics_system.git

cd marine_diagnostics_system
```

---

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 3: Configure Environment Variables

Create a local environment file:

```bash
cp .env.example .env
```

Populate the `.env` file:

```env
NEO4J_URI=bolt+routing://your-instance.databases.neo4j.io:7687

NEO4J_USERNAME=neo4j

NEO4J_PASSWORD=your_auradb_password

GROQ_API_KEY=gsk_your_groq_api_key
```

> The `.gitignore` file is configured to prevent accidental exposure of secrets.

---

## Step 4: Load Dataset into Neo4j

Execute the ingestion script:

```bash
cd backend

python ingest_fd001.py
```

This script:

* Parses NASA FD001 data
* Creates graph entities
* Builds sensor relationships
* Establishes degradation pathways

---

## Step 5: Launch the API Server

```bash
uvicorn main:app --reload
```
---

## Step 6: Open Interactive API Documentation

Once the application starts successfully, access the automatically generated Swagger UI documentation using the local server URL displayed in your terminal.

Swagger UI provides:

- Endpoint testing
- Request inspection
- Response visualization
- API experimentation

---

# 🔬 Dataset

This project uses the publicly available:

**NASA C-MAPSS Turbofan Engine Degradation Simulation Dataset (FD001)**

The dataset provides:

* Engine operational settings
* Sensor measurements
* Simulated degradation trajectories
* Remaining Useful Life (RUL) behavior

The graph schema has been adapted specifically for marine gas turbine diagnostic workflows.

---




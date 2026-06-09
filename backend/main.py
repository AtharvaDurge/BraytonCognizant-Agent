import os
import datetime
import pandas as pd
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from dotenv import load_dotenv
from neo4j import GraphDatabase
from fastapi.middleware.cors import CORSMiddleware
from formatter import get_clean_dataframe_from_bytes

# Core LangChain and Groq Model Imports
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

# Custom structural graph tools built in Phase 2
from agent_tools import get_anomaly_implications, trace_root_component_hierarchy

# Load Environment Configuration
load_dotenv()

app = FastAPI(title="Agentic Marine Diagnostics Engine Core", version="3.1.0")

# Enable Cross-Origin Resource Sharing (CORS) for Frontend Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Neo4j Connection Driver Instance
GLOBAL_DRIVER = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

# --- PYDANTIC SCHEMAS ---
class DiagnosticQuery(BaseModel):
    question: str

class FeedbackPayload(BaseModel):
    failure_mode: str
    sensor_id: str
    is_correct: bool


# --- HELPER LOGGING LAYER ---
def save_professional_report(filename, ui_records):
    """Generates a structured, timestamped audit log text file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    report_dir = os.path.join(script_dir, "reports")
    os.makedirs(report_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_path = os.path.join(report_dir, f"Audit_{timestamp}_{filename}.txt")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=== MARINE INTELLIGENT DIAGNOSTIC AUDIT LOG ===\n")
        f.write(f"Source: {filename}\nGenerated: {timestamp}\n\n")
        for item in ui_records:
            f.write(f"ENGINE #{item['engine_id']} | Cycle: {item['total_cycles']}\n")
            f.write(f"ANOMALIES: {', '.join(item['anomalies']) if item['anomalies'] else 'NONE'}\n")
            f.write("-" * 40 + "\n")
    return report_path


# --- ROUTE 1: TELEMETRY INGESTION & ALERT VALIDATOR ---
@app.post("/api/evaluate-upload")
async def process_user_uploaded_file(file: UploadFile = File(...)):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # 1. Read byte stream and clean layout
        raw_bytes = await file.read()
        test_df = get_clean_dataframe_from_bytes(raw_bytes)

        # 2. Archive copy of clean dataset
        archive_dir = os.path.join(script_dir, "processed_data")
        os.makedirs(archive_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_file_path = os.path.join(archive_dir, f"Clean_{timestamp}_{file.filename}.csv")
        test_df.to_csv(clean_file_path, index=False)

        # 3. Load actual Remaining Useful Life reference sheet
        rul_file_path = os.path.abspath(os.path.join(script_dir, "..", "data", "RUL_FD001.txt"))
        rul_list = []
        if os.path.exists(rul_file_path):
            with open(rul_file_path, "r") as f:
                rul_list = [int(line.strip()) for line in f.readlines() if line.strip()]

        # 4. Pull calibrated database thresholds live from Neo4j
        sensor_thresholds = {}
        with GLOBAL_DRIVER.session() as session:
            result = session.run("MATCH (s:Sensor) RETURN s.id as id, s.critical_threshold as threshold")
            for record in result:
                if record["id"] and record["threshold"] is not None:
                    sensor_thresholds[record["id"]] = float(record["threshold"])

        # Correct NASA C-MAPSS column labels matching formatter.py headers
        sensor_graph_mapping = {
    "T24":      "S2",   # col 6  — Total temp at LPC outlet
    "T30":      "S3",   # col 7  — Total temp at HPC outlet
    "T50":      "S4",   # col 8  — Total temp at LPT outlet
    "P30":      "S7",   # col 11 — Total pressure at HPC outlet
    "Nf":       "S8",   # col 12 — Physical fan speed
    "Nc":       "S9",   # col 13 — Physical core speed
    "Ps30":     "S11",  # col 15 — Static pressure at HPC outlet
    "HpcBleed": "S12",  # col 16 — Ratio of fuel flow to Ps30  (was incorrectly S17)
    "W31":      "S19",  # col 23 — HPT coolant bleed           (was incorrectly S20)
    "W32":      "S20",  # col 24 — LPT coolant bleed           (was incorrectly S21)
}
        ui_records = []
        for engine_id in test_df['unit'].unique():
            engine_data = test_df[test_df['unit'] == engine_id]
            final_row = engine_data.iloc[-1]
            last_logged_cycle = int(final_row['cycle'])
            idx = int(engine_id) - 1
            assigned_rul = rul_list[idx] if idx < len(rul_list) else "Unknown"

            breached_sensors, healthy_sensors = [], []
            for graph_id, nasa_label in sensor_graph_mapping.items():
                if nasa_label in final_row:
                    val = float(final_row[nasa_label])
                    limit = sensor_thresholds.get(graph_id)
                    if limit and val > limit:
                        breached_sensors.append(graph_id)
                    else:
                        healthy_sensors.append(f"{graph_id} ({val:.2f} <= {limit or 'N/A'})")

            ui_records.append({
                "engine_id": int(engine_id),
                "total_cycles": last_logged_cycle,
                "remaining_life": assigned_rul,
                "anomalies": breached_sensors,
                "nominal": healthy_sensors
            })

        save_professional_report(file.filename, ui_records)
        return {"status": "Success", "data": ui_records}
    except Exception as e:
        return {"status": "Error", "message": str(e)}


# --- ROUTE 2: AGENTIC ROOT CAUSE REASONING ENGINE ---
@app.post("/api/query")
def process_marine_diagnostic(payload: DiagnosticQuery):
    try:
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)
        tools = [get_anomaly_implications, trace_root_component_hierarchy]
        llm_with_tools = llm.bind_tools(tools)

        system_instruction = """
        You are an Expert Marine Engine Reasoning Diagnostician executing a Root Cause Analysis (RCA).
        Your primary directive is to resolve the structural component failure causing active telemetry anomalies.
        
        Operational Execution Plan:
        1. Extract the active breached sensor labels mentioned within the context or question.
        2. Execute `get_anomaly_implications` with those exact sensor labels.
        3. Identify the highest-weight failure mode path. 
        4. Pass that failure mode into `trace_root_component_hierarchy` to locate the engineering root component.
        5. Respond with a clear synthesis: Triggered sensors, diagnosed failure mode with weight, and the hosting Component/Subsystem lineage.
        
        CRITICAL DATA PARSING RULE:
        At the absolute bottom of your final response, output exactly:
        CONFIRMED_FAULT: <Name of the highest-weight failure mode detected>
        """

        messages = [SystemMessage(content=system_instruction), HumanMessage(content=payload.question)]

        for _ in range(5):
            response = llm_with_tools.invoke(messages)
            messages.append(response)

            if not response.tool_calls:
                break

            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                if tool_name == "get_anomaly_implications":
                    sensors = tool_args.get("breached_sensors", [])
                    observation = get_anomaly_implications.invoke({"breached_sensors": sensors})
                elif tool_name == "trace_root_component_hierarchy":
                    # Robust cleaning of input to prevent database mapping failures
                    fm_name = tool_args.get("failure_mode_name", "").strip()
                    print(f"DEBUG: Tracing hierarchy for: '{fm_name}'")
                    observation = trace_root_component_hierarchy.invoke({"failure_mode_name": fm_name})

                    # Help the agent recover if the mapping fails
                    if "Could not map" in observation:
                        observation += " DEBUG: Verify the FailureMode name matches the node in the KG exactly."
                else:
                    observation = f"Unknown tool execution request: {tool_name}"

                messages.append(ToolMessage(content=str(observation), name=tool_name, tool_call_id=tool_call["id"]))

        return {"status": "Success", "diagnostic_answer": messages[-1].content.strip()}

    except Exception as e:
        return {"status": "Error", "diagnostic_answer": f"Agent Loop Exception Trace: {str(e)}"}


# --- ROUTE 3: GRAPH LEARNING & CONNECTION REINFORCEMENT ---
@app.post("/api/diagnose/feedback")
def submit_diagnostic_feedback(payload: FeedbackPayload):
    try:
        with GLOBAL_DRIVER.session() as session:
            if payload.is_correct:
                query = """
                MATCH (f:FailureMode {name: $fail_name})-[r:CAUSES_ANOMALY]->(s:Sensor {id: $sensor_id})
                SET r.weight = r.weight + (0.1 * (1.0 - r.weight))
                RETURN r.weight as new_weight
                """
            else:
                query = """
                MATCH (f:FailureMode {name: $fail_name})-[r:CAUSES_ANOMALY]->(s:Sensor {id: $sensor_id})
                SET r.weight = r.weight - (0.05 * r.weight)
                RETURN r.weight as new_weight
                """
            result = session.run(query, fail_name=payload.failure_mode, sensor_id=payload.sensor_id)
            record = result.single()
            if not record:
                return {"status": "Error", "message": "Causal edge connection not found."}
            return {"status": "Success", "new_weight": round(record["new_weight"], 4)}
    except Exception as e:
        return {"status": "Error", "message": str(e)}


@app.get("/health")
def health_check():
    return {"status": "online", "server": "Uvicorn Engine Core Ready"}
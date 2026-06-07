import os
import datetime
import pandas as pd
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from fastapi.middleware.cors import CORSMiddleware
from formatter import get_clean_dataframe_from_bytes

load_dotenv()
app = FastAPI(title="AeroDiagnostic Engine Core", version="2.5.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

GLOBAL_DRIVER = GraphDatabase.driver(
    os.getenv("NEO4J_URI"), 
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

class DiagnosticQuery(BaseModel):
    question: str

def save_professional_report(filename, ui_records):
    """Generates a structured, timestamped audit log."""
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

@app.post("/api/evaluate-upload")
async def process_user_uploaded_file(file: UploadFile = File(...)):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 1. READ & CLEAN
        raw_bytes = await file.read()
        test_df = get_clean_dataframe_from_bytes(raw_bytes)
        
        # 2. ARCHIVE CLEAN DATA
        archive_dir = os.path.join(script_dir, "processed_data")
        os.makedirs(archive_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_file_path = os.path.join(archive_dir, f"Clean_{timestamp}_{file.filename}.csv")
        test_df.to_csv(clean_file_path, index=False)

        # 3. RUN DIAGNOSTICS
        rul_file_path = os.path.abspath(os.path.join(script_dir, "..", "data", "RUL_FD001.txt"))
        rul_list = []
        if os.path.exists(rul_file_path):
            with open(rul_file_path, "r") as f:
                rul_list = [int(line.strip()) for line in f.readlines() if line.strip()]

        sensor_thresholds = {}
        with GLOBAL_DRIVER.session() as session:
            result = session.run("MATCH (s:Sensor) RETURN s.id as id, s.critical_threshold as threshold")
            for record in result:
                if record["id"] and record["threshold"] is not None:
                    sensor_thresholds[record["id"]] = float(record["threshold"])

        sensor_graph_mapping = {
            "T24": "S2", "T30": "S3", "T50": "S4", "P30": "S7", "Nf": "S8",
            "Nc": "S9", "Ps30": "S11", "HpcBleed": "S12", "W31": "S19", "W32": "S20"
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
                        breached_sensors.append(f"{graph_id} ({val:.2f} > {limit:.2f})")
                    else:
                        healthy_sensors.append(f"{graph_id} ({val:.2f} <= {limit or 'N/A'})")
            
            ui_records.append({
                "engine_id": int(engine_id),
                "total_cycles": last_logged_cycle,
                "remaining_life": assigned_rul,
                "anomalies": breached_sensors,
                "nominal": healthy_sensors
            })

        # 4. SAVE AUDIT REPORT
        save_professional_report(file.filename, ui_records)

        return {"status": "Success", "data": ui_records}
    except Exception as e:
        return {"status": "Error", "message": str(e)}

@app.post("/api/query")
def process_marine_diagnostic(payload: DiagnosticQuery):
    try:
        with GLOBAL_DRIVER.session() as session:
            universal_cypher = "MATCH (f:FailureMode)-[r:CAUSES_ANOMALY_IN]->(s:Sensor) RETURN f.name as failure_mode, s.id as sensor_id, s.critical_threshold as threshold"
            result = session.run(universal_cypher)
            raw_context = [record.data() for record in result]
        
        template = """
        You are an Expert Marine Engine Diagnostician. Use the following causal graph context to answer the user's question.
        Causal Context: {context}
        Instructions:
        - Analyze the relationship between components and sensors.
        - If the user asks for a diagnosis, identify the root cause based on the provided causal chains.
        - Be concise, professional, and reference specific sensors where applicable.
        Question: {question}
        """
        prompt = PromptTemplate(template=template, input_variables=["context", "question"])
        
        llm_brain = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)
        formatted_prompt = prompt.format(context=str(raw_context), question=payload.question)
        ai_response = llm_brain.invoke(formatted_prompt)
        
        return {"status": "Success", "diagnostic_answer": ai_response.content.strip()}
    except Exception as e:
        return {"status": "Error", "diagnostic_answer": str(e)}
@app.get("/health")
def health_check():
    return {"status": "online", "message": "API is operational"}
@app.get("/api/db-status")
def check_db_connection():
    try:
        with GLOBAL_DRIVER.session() as session:
            # Perform a simple, fast query
            session.run("RETURN 1")
        return {"status": "connected", "database": "Neo4j AuraDB is operational"}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}    
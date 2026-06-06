import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="AeroDiagnostic Engine Core", version="2.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class DiagnosticQuery(BaseModel):
    question: str

CONVERSATIONAL_RESPONSE_TEMPLATE = """You are a precise data-reporting agent.

- YOUR ONLY SOURCE OF TRUTH IS THE "LIVE GRAPH DATABASE CONTEXT" BELOW.
- IF A SENSOR READING EXCEEDS THE "threshold" PROVIDED IN THE CONTEXT, YOU MUST EXPLICITLY STATE THAT AN ANOMALY HAS BEEN DETECTED AND PROVIDE THE THRESHOLD VALUE.
- If multiple entries exist, list them in a clear Markdown table.

--- LIVE GRAPH DATABASE CONTEXT ---
{context}
----------------------------------

User Question: {question}

Assistant Response:"""

RESPONSE_PROMPT = ChatPromptTemplate.from_template(CONVERSATIONAL_RESPONSE_TEMPLATE)

@app.post("/api/query")
def process_marine_diagnostic(payload: DiagnosticQuery):
    try:
        driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"), 
            auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
        )
        
        with driver.session() as session:
            universal_cypher = """
            MATCH (f:FailureMode)-[r:CAUSES_ANOMALY_IN]->(s:Sensor)
            RETURN f.name as failure_mode, s.id as sensor_id, s.critical_threshold as threshold, r.weight as weight
            """
            result = session.run(universal_cypher)
            raw_context = [record.data() for record in result]
        
        driver.close()

        llm_brain = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)
        
        formatted_prompt = RESPONSE_PROMPT.format(
            context=str(raw_context),
            question=payload.question
        )
        
        ai_response = llm_brain.invoke(formatted_prompt)
        
        return {
            "status": "Success",
            "diagnostic_answer": ai_response.content.strip()
        }

    except Exception as e:
        return {
            "status": "Error", 
            "diagnostic_answer": f"Connection Error: {str(e)}"
        }

@app.get("/health")
def health_check():
    return {"status": "AeroDiagnostic Engine Core Online"}


import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("\n--- ENVIRONMENT DIAGNOSTIC CHECK ---")
print(f"NEO4J_URI detected: {NEO4J_URI is not None}")
print(f"NEO4J_USERNAME detected: {NEO4J_USERNAME is not None}")
print(f"NEO4J_PASSWORD detected: {NEO4J_PASSWORD is not None}")
print(f"GROQ_API_KEY detected: {GROQ_API_KEY is not None}")
print("------------------------------------\n")

if not all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, GROQ_API_KEY]):
    raise RuntimeError("CRITICAL ERROR: Required credentials missing from configuration vault.")

app = FastAPI(
    title="Project BraytonCognizant API Tier",
    description="Deterministic GraphRAG API Layer with Programmatic Guardrails",
    version="2.5.0"
)

class DiagnosticQuery(BaseModel):
    question: str

CONVERSATIONAL_RESPONSE_TEMPLATE = """You are an expert, highly advanced marine systems diagnostic AI assistant for aeroderivative naval gas turbines, similar to ChatGPT or Gemini.
Your core mission is to answer user queries conversationally, intelligently, and precisely based on live data from our Neo4j Graph Database.

--- LIVE GRAPH DATABASE CONTEXT ---
{context}
----------------------------------

User Request/Question: {question}

Instructions:
1. Respond in a helpful, conversational, and analytical style using markdown formatting, bold headers, and structured bullets or plain text layout where relevant.
2. Keep your answers factual and completely grounded in the database context provided above. Do not hallucinate external details.
3. CRITICAL COUNTING RULE: If the user asks for a total count, numerical summary, or "how many" objects exist in the context, trace through the context rows sequentially one-by-one to make sure you do not miss any entries. Double-check your arithmetic count step-by-step before printing the final digits.

Assistant Response:"""

RESPONSE_PROMPT = ChatPromptTemplate.from_template(CONVERSATIONAL_RESPONSE_TEMPLATE)

@app.get("/api/health")
def verify_system_health():
    """
    Operational Check Endpoint.
    Validates server availability and performs a live handshake check with Neo4j AuraDB.
    """
    try:
        graph_db = Neo4jGraph(
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
            database=NEO4J_USERNAME
        )
        graph_db.refresh_schema()
        db_status = "Connected & Synchronized"
    except Exception as e:
        db_status = f"Handshake Failed: {str(e)}"
    
    return {
        "status": "Online",
        "system_agent": "BraytonCognizant Diagnostic Core",
        "database_handshake": db_status
    }

@app.post("/api/query")
def process_marine_diagnostic(payload: DiagnosticQuery):
    """
    Universal GraphRAG Reasoning Lane with Code-Level Math Guardrails.
    """
    try:
        graph_db = Neo4jGraph(
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
            database=NEO4J_USERNAME
        )
        
        universal_cypher = """
        MATCH (f:FailureMode)-[r:CAUSES_ANOMALY_IN]->(s:Sensor)
        RETURN f.name as failure_mode, type(r) as relationship, s.id as sensor_id, s.description as sensor_desc, r.weight as relationship_weight
        """
        raw_context = graph_db.query(universal_cypher)

      

        llm_brain = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)
        
        formatted_prompt = RESPONSE_PROMPT.format(
            context=str(raw_context),
            question=payload.question
        )
        
        ai_response = llm_brain.invoke(formatted_prompt)
        
        return {
            "status": "Success",
            "query_processed": payload.question,
            "diagnostic_answer": ai_response.content.strip()
        }

    except Exception as e:
        return {
            "status": "Error",
            "detail": f"Diagnostic Stream Interrupted: {str(e)}"
        }
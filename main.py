import os
from fastapi import FastAPI
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph

# 1. Boot up environment mapping from your local folder secrets
load_dotenv()

# 2. Extract values using the exact VARIABLE KEY names from your .env file
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# 3. Environment Diagnostic Check Loop (Prints on startup in your terminal)
print("\n--- ENVIRONMENT DIAGNOSTIC CHECK ---")
print(f"NEO4J_URI detected: {NEO4J_URI is not None}")
print(f"NEO4J_USERNAME detected: {NEO4J_USERNAME is not None}")
print(f"NEO4J_PASSWORD detected: {NEO4J_PASSWORD is not None}")
print("------------------------------------\n")

# 4. Critical safety gateway block
if not all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD]):
    raise RuntimeError("CRITICAL ERROR: Neo4j environment credentials missing from local configuration vault.")

# 5. Initialize FastAPI Core App
app = FastAPI(
    title="Project BraytonCognizant API Tier",
    description="GraphRAG Translation API Layer for Aeroderivative Marine Turbine Diagnostics",
    version="2.0.0"
)

# 6. Primary Gateway Health Check Endpoint
@app.get("/api/health")
def verify_system_health():
    """
    Operational Check Endpoint.
    Validates server availability and attempts a live handshake check with the Neo4j Graph Database.
    """
    try:
        # Establish a temporary network connection to verify AuraDB is responsive
        graph_db = Neo4jGraph(
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
            database=NEO4J_USERNAME  # FORCE the driver to target database name '1bba8b49' instead of default 'neo4j'
        )
        # Force a minimal database schema extraction to validate active permissions
        graph_db.refresh_schema()
        db_status = "Connected & Synchronized"
    except Exception as e:
        db_status = f"Handshake Failed: {str(e)}"
    
    return {
        "status": "Online",
        "system_agent": "BraytonCognizant Diagnostic Core",
        "database_handshake": db_status
    }
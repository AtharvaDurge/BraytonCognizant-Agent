import os
from langchain_core.tools import tool
from neo4j import GraphDatabase, TrustAll, TrustSystemCAs
from dotenv import load_dotenv

load_dotenv()
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PWD = os.getenv("NEO4J_PASSWORD")

def _get_driver():
    """
    Returns a Neo4j driver with universal SSL handling.
    Set NEO4J_TRUST_ALL=true in .env to bypass SSL cert verification
    (required on some machines with self-signed cert chain issues).
    """
    if os.getenv("NEO4J_TRUST_ALL", "false").lower() == "true":
        return GraphDatabase.driver(
            URI.replace("neo4j+s://", "neo4j://"),
            auth=(USER, PWD),
            encrypted=True,
            trusted_certificates=TrustAll()
        )
    return GraphDatabase.driver(URI, auth=(USER, PWD))

@tool
def get_anomaly_implications(breached_sensors: list[str]) -> str:
    """
    Queries the knowledge graph to discover which Failure Modes are directly 
    linked to a list of breached sensors, alongside their historical probabilistic weights.
    Use this tool when you need to narrow down likely structural failures from anomalous sensor inputs.
    """
    if not breached_sensors:
        return "No telemetry anomalies provided."
    
    driver = _get_driver()
    query = """
    MATCH (f:FailureMode)-[r:CAUSES_ANOMALY]->(s:Sensor)
    WHERE s.id IN $sensor_ids
    RETURN f.name as failure_mode, s.id as sensor_id, r.weight as weight, f.severity as severity
    ORDER BY r.weight DESC
    """
    try:
        with driver.session() as session:
            result = session.run(query, sensor_ids=breached_sensors)
            records = [record.data() for record in result]
            if not records:
                return f"No mechanical failure modes matched the following sensors in the KG: {breached_sensors}"
            
            output = "Graph Discovery - Associated Failure Modes:\n"
            for r in records:
                output += f"- [Fault]: {r['failure_mode']} | Affected Sensor: {r['sensor_id']} | Edge Weight: {r['weight']} | Severity: {r['severity']}\n"
            return output
    except Exception as e:
        return f"Database error encountered: {str(e)}"
    finally:
        driver.close()

@tool
def trace_root_component_hierarchy(failure_mode_name: str) -> str:
    """
    Traces a failure mode upstream to identify its host component and parenting Subsystem.
    Use this tool to pinpoint the exact structural root cause engineering layer responsible for a fault.
    """
    clean_name = failure_mode_name.strip()
    
    driver = _get_driver()
    query = """
    MATCH (sub:Subsystem)-[:HAS_COMPONENT]->(comp:Component)-[:DEVELOPES_FAULT]->(f:FailureMode {name: $name})
    RETURN sub.name as subsystem, comp.name as component, comp.abbreviation as abbr
    """
    try:
        with driver.session() as session:
            result = session.run(query, name=clean_name)
            record = result.single()
            if not record:
                return f"Could not map failure mode '{clean_name}' to any mechanical component layer."
            return f"Component Lineage: Subsystem '{record['subsystem']}' -> Component '{record['component']}' ({record['abbr']})"
    except Exception as e:
        return f"Database error encountered: {str(e)}"
    finally:
        driver.close()
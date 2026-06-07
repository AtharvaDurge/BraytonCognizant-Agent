import os
import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

# Complete structural dictionary translating NASA tags to your Neo4j Database ID labels
SENSOR_MAP = {
    'S2': 'T24',
    'S3': 'T30',
    'S4': 'T50',
    'S6': 'P30',
    'S7': 'Nf',
    'S8': 'Nc',
    'S11': 'Ps30',
    'S17': 'HpcBleed',
    'S20': 'W31',
    'S21': 'W32'
}

def ingest_thresholds():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir.endswith("scripts"):
        base_dir = os.path.dirname(os.path.dirname(script_dir))
    else:
        base_dir = os.path.dirname(script_dir)
        
    data_path = os.path.join(base_dir, 'data', 'baseline_thresholds.csv')
    
    if not os.path.exists(data_path):
        print(f"❌ Error: Baseline reference file not found at: {data_path}")
        return

    df = pd.read_csv(data_path)
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    
    try:
        with driver.session() as session:
            print("🔄 Synchronizing calibrated baselines into Neo4j graph nodes...")
            for _, row in df.iterrows():
                tag = str(row['sensor']).upper().strip()
                val = float(row['threshold'])
                sensor_id = row['sensor']
                
                if tag in SENSOR_MAP:
                    node_id = SENSOR_MAP[tag]
                    query = """
                    MATCH (s:Sensor {id: $id})
                    SET s.critical_threshold = $val
                    RETURN s
                    """
                    result = session.run(query, id=node_id, val=val)
                    if result.peek():
                        print(f"✅ Mapped {tag} -> Node ({node_id}) to threshold: {val:.4f}")
    finally:
        driver.close()
        print("🏁 Ingestion Pipeline Finished.")

if __name__ == "__main__":
    ingest_thresholds()
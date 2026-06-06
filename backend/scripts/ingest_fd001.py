import pandas as pd
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

SENSOR_MAP = {
    'S2': 'T24',
    'S3': 'T30',
}

def ingest_thresholds():
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'baseline_thresholds.csv')
    
    if not os.path.exists(data_path):
        print(f"Error: File not found at {data_path}")
        return

    df = pd.read_csv(data_path)
    
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    
    try:
        with driver.session() as session:
            for _, row in df.iterrows():
                raw_id = str(row['sensor']).upper()
                sensor_id = SENSOR_MAP.get(raw_id, raw_id)
                
                query = """
                MATCH (s:Sensor {id: $id})
                SET s.critical_threshold = $val
                """
                session.run(query, id=sensor_id, val=float(row['val']))
                print(f"✅ Successfully updated {sensor_id} with threshold {row['val']}")
                
    except Exception as e:
        print(f"Ingestion failed: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    ingest_thresholds()


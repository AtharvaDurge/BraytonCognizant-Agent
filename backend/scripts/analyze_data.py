import os
import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv

# 1. SETUP ENVIRONMENT & CREDENTIALS
load_dotenv()
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PWD = os.getenv("NEO4J_PASSWORD")

# 2. DEFINITIVE NASA C-MAPSS FD001 COLUMN MAP (0-indexed)
column_map = {
    'T24': 6, 'T30': 7, 'T50': 8, 'P30': 11, 'Nf': 12,
    'Nc': 13, 'Ps30': 15, 'HpcBleed': 16, 'W31': 23, 'W32': 24
}

def push_to_neo4j(sensor_id, threshold):
    driver = GraphDatabase.driver(URI, auth=(USER, PWD))
    try:
        with driver.session() as session:
            query = """
            MATCH (s:Sensor {id: $id})
            SET s.critical_threshold = $threshold
            RETURN s.id, s.critical_threshold
            """
            session.run(query, id=sensor_id, threshold=float(threshold))
    finally:
        driver.close()

# 3. ABSOLUTE PATH RESOLUTION
# Finds the project root regardless of script sub-folder location
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))
data_path = os.path.join(root_dir, 'data', 'train_clean.txt')
output_path = os.path.join(root_dir, 'data', 'baseline_thresholds.csv')

print(f"DEBUG: Looking for data at: {data_path}")

try:
    if not os.path.exists(data_path):
        print(f"CRITICAL ERROR: File not found at {data_path}")
    else:
        df = pd.read_csv(data_path, sep=r'\s+', header=None, engine='python')
        print("\n===== COLUMN DEBUG =====")
        print(df.iloc[0])
        print("========================\n")
        print(f"DEBUG: Data loaded successfully. Shape: {df.shape}")

        # Healthy baseline: Cycles 1-20
        healthy_df = df[df[1] <= 20]

        print("\n--- CALCULATING & PUSHING THRESHOLDS ---")
        results = []
        for s, idx in column_map.items():
            print(f"{s} -> Column {idx}")
            print(healthy_df[idx].head())
            print("----------------")
        for s, idx in column_map.items():
          
            val = healthy_df[idx].mean() * 1.01
            print(f"Pushing {s}: {val:.4f} to Neo4j...")
            push_to_neo4j(s, val)
            results.append({'sensor': s, 'threshold': val})

        # Save to CSV in the project root/data folder
        pd.DataFrame(results).to_csv(output_path, index=False)
        print(f"\nDEBUG: Thresholds saved to {output_path}")
        print("DEBUG: Successfully synced all thresholds to Neo4j!")

except Exception as e:
    print(f"DEBUG: Error occurred: {e}")
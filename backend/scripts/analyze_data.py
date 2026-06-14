import os
import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PWD = os.getenv("NEO4J_PASSWORD")

column_map = {
    'T24': 6, 'T30': 7, 'T50': 8, 'P30': 11, 'Nf': 12,
    'Nc': 13, 'Ps30': 15, 'HpcBleed': 16, 'W31': 23, 'W32': 24
}

def initialize_deep_knowledge_graph():
    """Wipes old flat data and builds the multi-layered structural engine schema."""
    driver = GraphDatabase.driver(URI, auth=(USER, PWD))
    
    cleanup_query = "MATCH (n) DETACH DELETE n;"
    
    schema_constraints = [
        "CREATE CONSTRAINT unique_subsystem IF NOT EXISTS FOR (s:Subsystem) REQUIRE s.name IS UNIQUE;",
        "CREATE CONSTRAINT unique_component IF NOT EXISTS FOR (c:Component) REQUIRE c.name IS UNIQUE;",
        "CREATE CONSTRAINT unique_failure IF NOT EXISTS FOR (f:FailureMode) REQUIRE f.name IS UNIQUE;",
        "CREATE CONSTRAINT unique_sensor IF NOT EXISTS FOR (s:Sensor) REQUIRE s.id IS UNIQUE;"
    ]

    build_hierarchy_query = """
    // 1. Create Subsystems
    MERGE (turbo:Subsystem {name: "Turbomachinery Subsystem", description: "Core gas turbine components processing airflow"})
    MERGE (combustor_sub:Subsystem {name: "Combustor Subsystem", description: "Fuel delivery and high-temperature combustion chamber"})
    
    // 2. Create Components
    MERGE (lpc:Component {name: "Low Pressure Compressor", abbreviation: "LPC"})
    MERGE (hpc:Component {name: "High Pressure Compressor", abbreviation: "HPC"})
    MERGE (cc:Component {name: "Combustor Chamber", abbreviation: "CC"})
    MERGE (hpt:Component {name: "High Pressure Turbine", abbreviation: "HPT"})
    MERGE (lpt:Component {name: "Low Pressure Turbine", abbreviation: "LPT"})
    
    // 3. Connect Subsystems to Components
    MERGE (turbo)-[:HAS_COMPONENT]->(lpc)
    MERGE (turbo)-[:HAS_COMPONENT]->(hpc)
    MERGE (combustor_sub)-[:HAS_COMPONENT]->(cc)
    MERGE (turbo)-[:HAS_COMPONENT]->(hpt)
    MERGE (turbo)-[:HAS_COMPONENT]->(lpt)
    
    // 4. Create Failure Modes
    MERGE (f_lpc_fouling:FailureMode {name: "LPC Blade Fouling", severity: "Medium"})
    MERGE (f_hpc_wear:FailureMode {name: "HPC Structural Degradation", severity: "High"})
    MERGE (f_cc_nozzle:FailureMode {name: "Combustor Nozzle Clogging", severity: "Critical"})
    MERGE (f_hpt_erosion:FailureMode {name: "HPT Blade Thermal Erosion", severity: "High"})
    MERGE (f_lpt_efficiency:FailureMode {name: "LPT Efficiency Loss", severity: "Medium"})
    
    // 5. Connect Components to Failure Modes
    MERGE (lpc)-[:DEVELOPES_FAULT]->(f_lpc_fouling)
    MERGE (hpc)-[:DEVELOPES_FAULT]->(f_hpc_wear)
    MERGE (cc)-[:DEVELOPES_FAULT]->(f_cc_nozzle)
    MERGE (hpt)-[:DEVELOPES_FAULT]->(f_hpt_erosion)
    MERGE (lpt)-[:DEVELOPES_FAULT]->(f_lpt_efficiency)
    
    // 6. Create Sensors (Matching NASA C-MAPSS Mapping layout)
    MERGE (s2:Sensor {id: "T24", description: "Total temperature at LPC outlet", critical_threshold: 0.0})
    MERGE (s3:Sensor {id: "T30", description: "Total temperature at HPC outlet", critical_threshold: 0.0})
    MERGE (s4:Sensor {id: "T50", description: "Total temperature at LPT outlet", critical_threshold: 0.0})
    MERGE (s7:Sensor {id: "P30", description: "Total pressure at HPC outlet", critical_threshold: 0.0})
    MERGE (s8:Sensor {id: "Nf", description: "Physical fan speed", critical_threshold: 0.0})
    MERGE (s9:Sensor {id: "Nc", description: "Physical core speed", critical_threshold: 0.0})
    MERGE (s11:Sensor {id: "Ps30", description: "Static pressure at HPC outlet", critical_threshold: 0.0})
    MERGE (s12:Sensor {id: "HpcBleed", description: "Ratio of fuel flow to Ps30", critical_threshold: 0.0})
    MERGE (s19:Sensor {id: "W31", description: "HPT coolant bleed", critical_threshold: 0.0})
    MERGE (s20:Sensor {id: "W32", description: "LPT coolant bleed", critical_threshold: 0.0})
    
    // 7. Connect Failure Nodes to Sensors with Baseline Probabilistic Edge Weights
    MERGE (f_lpc_fouling)-[:CAUSES_ANOMALY {weight: 0.50, description: "Fouling restricts air, modifying fan flow"}]->(s2)
    MERGE (f_lpc_fouling)-[:CAUSES_ANOMALY {weight: 0.50}]->(s8)
    
    MERGE (f_hpc_wear)-[:CAUSES_ANOMALY {weight: 0.50, description: "HPC wear causes abnormal thermal loads"}]->(s3)
    MERGE (f_hpc_wear)-[:CAUSES_ANOMALY {weight: 0.50}]->(s7)
    MERGE (f_hpc_wear)-[:CAUSES_ANOMALY {weight: 0.50}]->(s9)
    MERGE (f_hpc_wear)-[:CAUSES_ANOMALY {weight: 0.50}]->(s11)
    MERGE (f_hpc_wear)-[:CAUSES_ANOMALY {weight: 0.50}]->(s12)
    
    MERGE (f_cc_nozzle)-[:CAUSES_ANOMALY {weight: 0.50, description: "Clogged nozzles skew structural fuel/air burn ratios"}]->(s7)
    MERGE (f_cc_nozzle)-[:CAUSES_ANOMALY {weight: 0.50}]->(s12)
    
    MERGE (f_hpt_erosion)-[:CAUSES_ANOMALY {weight: 0.50, description: "HPT erosion shifts downstream exhaust profiles"}]->(s4)
    MERGE (f_hpt_erosion)-[:CAUSES_ANOMALY {weight: 0.50}]->(s19)
    
    MERGE (f_lpt_efficiency)-[:CAUSES_ANOMALY {weight: 0.50, description: "LPT performance loss alters downstream exit parameters"}]->(s4)
    MERGE (f_lpt_efficiency)-[:CAUSES_ANOMALY {weight: 0.50}]->(s20)
    """

    try:
        with driver.session() as session:
            print("🧹 Step 1: Cleaning up existing flat graph connections...")
            session.run(cleanup_query)
            
            print("🔒 Step 2: Applying database schema uniqueness constraints...")
            for statement in schema_constraints:
                session.run(statement)
                
            print("🏗️ Step 3: Generating multi-layered mechanical component structural hierarchy...")
            session.run(build_hierarchy_query)
            print("✅ Graph structural base successfully established.")
    finally:
        driver.close()

def update_sensor_threshold(sensor_id, threshold):
    """Updates the calculated data threshold parameter on pre-existing schema structural nodes."""
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

script_dir = os.path.dirname(os.path.abspath(__file__))

def find_project_root(start_dir):
    current = start_dir
    for _ in range(5):
        if os.path.isdir(os.path.join(current, 'data')):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.path.dirname(start_dir)

root_dir = find_project_root(script_dir)
data_path = os.path.join(root_dir, 'data', 'train_clean.txt')
output_path = os.path.join(root_dir, 'data', 'baseline_thresholds.csv')

print(f"DEBUG: Looking for data at: {data_path}")

try:
    if not os.path.exists(data_path):
        print(f"CRITICAL ERROR: File not found at {data_path}")
    else:
        initialize_deep_knowledge_graph()

        df = pd.read_csv(data_path, sep='\t', header=None, engine='python')
        print(f"DEBUG: Data loaded successfully. Shape: {df.shape}")

        healthy_df = df[df[1] <= 20]

        print("\n--- CALCULATING & SYNCING TELEMETRY THRESHOLDS ---")
        results = []
        for s, idx in column_map.items():
            # Calculate threshold: mean * 1.01
            val = healthy_df[idx].mean() * 1.01
            print(f"Pushing calculated threshold for {s}: {val:.4f} to Neo4j...")
            update_sensor_threshold(s, val)
            results.append({'sensor': s, 'threshold': val})

        pd.DataFrame(results).to_csv(output_path, index=False)
        print(f"\nDEBUG: Threshold reference backup saved locally to {output_path}")
        print("🎉 Phase 1 Complete: Structural Graph populated and calibrated successfully!")

except Exception as e:
    print(f"DEBUG: Error occurred: {e}")
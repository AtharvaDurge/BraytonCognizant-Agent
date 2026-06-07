import os
import requests
import pandas as pd

API_URL = "http://localhost:8000/api/query"

def run_automated_evaluation():
    # 1. ABSOLUTE PATH RESOLVER
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_script_dir, "..", ".."))
    
    test_path = os.path.join(root_dir, 'data', 'test_FD001.txt')
    rul_path = os.path.join(root_dir, 'data', 'RUL_FD001.txt')
    log_output_path = os.path.join(root_dir, 'backend', 'reports', 'diagnostic_evaluation_log.txt')
    
    if not os.path.exists(test_path) or not os.path.exists(rul_path):
        print(f"❌ Evaluation cancelled: Required source data assets missing.")
        return

    # NASA FD001 standard whitespace layout
    test_df = pd.read_csv(test_path, sep=r"\s+", header=None)
    rul_df = pd.read_csv(rul_path, sep=r"\s+", header=None)
    
    # Core engineering sensor layout map matching your Neo4j configuration
    # Key: Graph Node Identifier -> Value: Zero-based Pandas index position in row
    sensor_column_mapping = {
        "T24": 6, "T30": 7, "T50": 8, "P30": 11, "Nf": 12,
        "Nc": 13, "Ps30": 16, "HpcBleed": 19, "W31": 21, "W32": 22
    }

    unique_engines = test_df[0].unique()
    evaluation_records = []

    print(f"🚀 Starting dynamic multi-sensor validation over {len(unique_engines[:5])} engine test samples...")

    for engine_id in unique_engines[:5]:
        engine_data = test_df[test_df[0] == engine_id]
        final_cycle_row = engine_data.iloc[-1]
        last_logged_cycle = int(final_cycle_row[1])
        
        # Build a neat string summary of ALL 10 sensor streams for this engine row
        telemetry_summary_lines = []
        sensor_records_text = ""
        
        for name, col_idx in sensor_column_mapping.items():
            val = float(final_cycle_row[col_idx])
            telemetry_summary_lines.append(f"{name}: {val:.2f}")
            sensor_records_text += f"• Terminal {name} value: {val:.2f}\n"

        # Build a rich prompt so Llama has the complete picture
        prompt_query = (
            f"Automated System Inspection Log: Engine Unit #{engine_id} reached its maximum test cycle of {last_logged_cycle}.\n"
            f"Current full telemetry profile data:\n"
            f"{sensor_records_text}\n"
            f"Cross-reference all 10 parameters against your structural graph limits. What failure modes are developing?"
        )
        
        try:
            response = requests.post(API_URL, json={"question": prompt_query}, timeout=15)
            if response.status_code == 200:
                ai_diagnosis = response.json().get("diagnostic_answer", "Error reading response payload.")
            else:
                ai_diagnosis = f"HTTP Error Status Code: {response.status_code}"
        except Exception as err:
            ai_diagnosis = (
                f"❌ Network Connection Failure!\n"
                f"Reason: Your main.py backend server is NOT running or port 8000 is blocked.\n"
                f"Details: {err}"
            )
            
        ground_truth_rul = int(rul_df.iloc[int(engine_id) - 1][0])
        
        record = (
            f"================================================\n"
            f"🔍 DIAGNOSTIC RECORD: ENGINE UNIT {engine_id}\n"
            f"================================================\n"
            f"• Last Recorded Operation Cycle : {last_logged_cycle}\n"
            f"• Ground Truth Remaining Life   : {ground_truth_rul} cycles\n"
            f"• Active Telemetry Profile      : {', '.join(telemetry_summary_lines)}\n\n"
            f"🤖 AI System Analytical Output:\n{ai_diagnosis}\n"
            f"================================================\n\n"
        )
        evaluation_records.append(record)
        print(f"Processed Unit #{engine_id} with all 10 sensors successfully.")

    # Write logs safely to backend/reports/
    with open(log_output_path, "w", encoding="utf-8") as log_file:
        log_file.writelines(evaluation_records)
        
    print(f"\nValidation sequence complete!")
    print(f"📝 Full multi-sensor evaluation log saved to: {log_output_path}")

if __name__ == "__main__":
    run_automated_evaluation()
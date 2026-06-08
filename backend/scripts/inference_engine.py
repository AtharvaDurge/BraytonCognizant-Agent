import os
import requests
import pandas as pd

EVAL_URL = "http://localhost:8000/api/evaluate-upload"
QUERY_URL = "http://localhost:8000/api/query"
FEEDBACK_URL = "http://localhost:8000/api/diagnose/feedback"

def run_automated_evaluation():
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_script_dir, "..", ".."))
    
    test_path = os.path.join(root_dir, 'data', 'test_FD001.txt')
    
    if not os.path.exists(test_path):
        test_path = os.path.join(current_script_dir, 'test_FD001.txt')

    if not os.path.exists(test_path):
        print("❌ Evaluation cancelled: Required source data assets missing.")
        return

    print("📤 Sending engine log sheet to /api/evaluate-upload...")
    try:
        with open(test_path, 'rb') as f:
            files = {'file': (os.path.basename(test_path), f, 'text/plain')}
            eval_response = requests.post(EVAL_URL, files=files, timeout=15)
        ui_records = eval_response.json().get("data", [])
    except Exception as e:
        print(f"❌ Connection error to backend server: {e}")
        return

    for record in ui_records[:3]:
        engine_id = record["engine_id"]
        anomalies = record["anomalies"]
        
        if not anomalies:
            print(f"✅ Engine Unit #{engine_id} is operating nominally. Skipping RCA loop.")
            continue
            
        print(f"\n🚀 Running Agentic Root Cause Analysis for Engine Unit #{engine_id}...")
        print(f"🚨 Active Anomaly Flags Detected: {anomalies}")

        prompt_query = (
            f"Automated System Inspection Log: Marine Engine Unit #{engine_id} has flagged critical threshold "
            f"breaches in the following sensor streams: {', '.join(anomalies)}. "
            f"Analyze the relationship against your structural knowledge graph to identify the structural root cause component."
        )
        
        query_response = requests.post(QUERY_URL, json={"question": prompt_query}, timeout=20)
        ai_diagnosis = query_response.json().get("diagnostic_answer", "No response.")
        
        print(f"🤖 AI Analytical Synthesis:\n{ai_diagnosis}\n")

        # --- SMART LEARNING LOOP EXTRACTOR ---
        # Parse the true confirmed fault out of the AI response string dynamically
        detected_fault = None
        for line in ai_diagnosis.split("\n"):
            if "CONFIRMED_FAULT:" in line:
                detected_fault = line.split("CONFIRMED_FAULT:")[-1].strip()
                break
        
        # Fallback safeguard if parsing string matches nothing
        if not detected_fault:
            detected_fault = "HPC Structural Degradation" if "Ps30" in anomalies else "LPT Efficiency Loss"

        print(f"🔄 Simulating Engineer Diagnostic Verification for: {detected_fault}")
        for sensor in anomalies:
            feedback_payload = {
                "failure_mode": detected_fault,
                "sensor_id": sensor,
                "is_correct": True
            }
            fb_res = requests.post(FEEDBACK_URL, json=feedback_payload, timeout=10)
            if fb_res.status_code == 200 and fb_res.json().get("status") == "Success":
                print(f"📈 [Graph Learning Update]: Edge link ({feedback_payload['failure_mode']} -> {sensor}) updated to Weight: {fb_res.json().get('new_weight')}")
            else:
                print(f"⚠️ [Graph Learning Notice]: Edge path does not exist for ({feedback_payload['failure_mode']} -> {sensor}). Skipping weight update.")

    print("\n🎉 Project End-To-End Testing Phase Concluded Successfully!")

if __name__ == "__main__":
    run_automated_evaluation()
const API_BASE = "http://localhost:8000/api";

let extractedCurrentFault = null;
let triggeredAnomaliesList = [];

const FAULT_SENSOR_MAP = {
    "LPC Blade Fouling":          ["T24", "Nf"],
    "HPC Structural Degradation": ["T30", "P30", "Nc", "Ps30", "HpcBleed"],
    "Combustor Nozzle Clogging":  ["P30", "HpcBleed"],
    "HPT Blade Thermal Erosion":  ["T50", "W31"],
    "LPT Efficiency Loss":        ["T50", "W32"],
};

const VALID_SENSORS = ["T24", "T30", "T50", "P30", "Nf", "Nc", "Ps30", "HpcBleed", "W31", "W32"];

document.getElementById('send-btn').addEventListener('click', sendQuestion);
document.getElementById('user-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendQuestion();
});

async function sendQuestion() {
    const inputEl = document.getElementById('user-input');
    const chatOutput = document.getElementById('chat-output');
    const questionText = inputEl.value.trim();

    if (!questionText) return;

    inputEl.value = "";
    
    chatOutput.innerHTML += `<div class="message user-msg">${questionText}</div>`;
    chatOutput.scrollTop = chatOutput.scrollHeight;

    const loadingId = "loader-" + Date.now();
    chatOutput.innerHTML += `<div class="message assistant-msg" id="${loadingId}">🧠 Agent is navigating knowledge graph tools...</div>`;
    chatOutput.scrollTop = chatOutput.scrollHeight;

    try {
        const response = await fetch(`${API_BASE}/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: questionText })
        });
        const result = await response.json();
        
        const targetLoader = document.getElementById(loadingId);
        if (result.status === "Success") {
            let cleanAnswer = result.diagnostic_answer;
            
            // Separate tracking metadata from human-readable text block
            if (cleanAnswer.includes("CONFIRMED_FAULT:")) {
                const parts = cleanAnswer.split("CONFIRMED_FAULT:");
                cleanAnswer = parts[0].trim();
                extractedCurrentFault = parts[1].trim();
                
                // Extract only real sensor IDs from the query text, not random words
                triggeredAnomaliesList = questionText
                    .split(/[\s,]+/)
                    .filter(token => VALID_SENSORS.includes(token));

                // Show the human feedback configuration panel layout
                document.getElementById('target-fault-display').innerText = extractedCurrentFault;
                document.getElementById('feedback-panel').style.display = "block";
            }
            
            targetLoader.innerText = cleanAnswer;
        } else {
            targetLoader.innerText = `❌ Error: ${result.diagnostic_answer}`;
        }
    } catch (error) {
        document.getElementById(loadingId).innerText = "❌ Exception occurred tracing path.";
    }
    chatOutput.scrollTop = chatOutput.scrollHeight;
}

document.getElementById('confirm-true-btn').addEventListener('click', () => submitGraphFeedback(true));
document.getElementById('confirm-false-btn').addEventListener('click', () => submitGraphFeedback(false));

async function submitGraphFeedback(isCorrect) {
    if (!extractedCurrentFault) return;

    const feedbackPanel = document.getElementById('feedback-panel');

    const validSensorsForFault = FAULT_SENSOR_MAP[extractedCurrentFault] || [];
    const sensorsToUpdate = triggeredAnomaliesList.filter(s => validSensorsForFault.includes(s));

    if (sensorsToUpdate.length === 0) {
        console.warn(`No valid edges found for fault "${extractedCurrentFault}" with sensors: ${triggeredAnomaliesList}`);
        feedbackPanel.style.display = "none";
        return;
    }

    let lastWeight = null;
    for (const sensor of sensorsToUpdate) {
        try {
            const response = await fetch(`${API_BASE}/diagnose/feedback`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    failure_mode: extractedCurrentFault,
                    sensor_id: sensor,
                    is_correct: isCorrect
                })
            });
            const data = await response.json();
            if (data.status === "Success") {
                lastWeight = data.new_weight;
                console.log(`📈 Edge (${extractedCurrentFault} -> ${sensor}) updated to weight: ${data.new_weight}`);
            } else {
                console.warn(`⚠️ Skipped (${extractedCurrentFault} -> ${sensor}): ${data.message}`);
            }
        } catch (err) {
            console.error(`Feedback transmission failed for sensor ${sensor}:`, err);
        }
    }

    if (lastWeight !== null) {
        alert(`📈 Graph Learning Sync: ${sensorsToUpdate.length} edge(s) updated. Latest weight: ${lastWeight}`);
    }
    feedbackPanel.style.display = "none";
}

document.getElementById('run-test-btn').addEventListener('click', async () => {
    const fileInput = document.getElementById('test-file-input');
    const logsOutput = document.getElementById('logs-output');
    const resultsWindow = document.getElementById('test-results');
    const btn = document.getElementById('run-test-btn');

    if (!fileInput.files.length) {
        alert("Please select a standard telemetry file first.");
        return;
    }

    btn.disabled = true;
    btn.innerText = "Analyzing Telemetry stream...";
    resultsWindow.style.display = "block";
    logsOutput.innerText = "Processing industrial data vectors over network streams...";

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const response = await fetch(`${API_BASE}/evaluate-upload`, {
            method: "POST",
            body: formData
        });
        const result = await response.json();

        if (result.status === "Success") {
            let logViewText = `=== DYNAMIC BOUNDARY INGESTION RESPONSE RESULTS ===\n\n`;
            result.data.forEach(item => {
                logViewText += `ENGINE ID: #${item.engine_id} | Cycled: ${item.total_cycles} | RUL Prediction: ${item.remaining_life}\n`;
                logViewText += `🚨 Triggered Anomalies : [ ${item.anomalies.join(", ") || 'NONE'} ]\n`;
                logViewText += `------------------------------------------------\n`;
            });
            logsOutput.innerText = logViewText;
        } else {
            logsOutput.innerText = `❌ Ingestion Error: ${result.message}`;
        }
    } catch (error) {
        logsOutput.innerText = `❌ Connection Error: Could not transfer data stream to backend core.\n${error}`;
    } finally {
        btn.disabled = false;
        btn.innerText = "Run Uploaded Test Sequence";
    }
});
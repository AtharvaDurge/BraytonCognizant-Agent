const API_BASE = "http://localhost:8000/api";

// Core Variables to track session feedback state
let extractedCurrentFault = null;
let triggeredAnomaliesList = [];

document.getElementById('send-btn').addEventListener('click', sendQuestion);
document.getElementById('user-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendQuestion();
});

// --- DYNAMIC DISCOVERY & QUERY LAYER ---
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
                
                // Track current active sensors mentioned in the query input to connect feedback targets
                triggeredAnomaliesList = questionText.match(/[A-Z][0-9a-zA-Z]+/g) || ["Ps30", "T30"]; 

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

// --- ACTIVE REINFORCEMENT LEARNING PANEL CLICK LIFECYCLES ---
document.getElementById('confirm-true-btn').addEventListener('click', () => submitGraphFeedback(true));
document.getElementById('confirm-false-btn').addEventListener('click', () => submitGraphFeedback(false));

async function submitGraphFeedback(isCorrect) {
    if (!extractedCurrentFault) return;
    
    const feedbackPanel = document.getElementById('feedback-panel');
    const sensorToUpdate = triggeredAnomaliesList[0] || "Ps30"; // Fallback target protect

    try {
        const response = await fetch(`${API_BASE}/diagnose/feedback`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                failure_mode: extractedCurrentFault,
                sensor_id: sensorToUpdate,
                is_correct: isCorrect
            })
        });
        const data = await response.json();
        if (data.status === "Success") {
            alert(`📈 Graph Learning Sync: Connection weight adjusted to: ${data.new_weight}`);
            feedbackPanel.style.display = "none";
        } else {
            alert(`⚠️ Update Alert: ${data.message}`);
        }
    } catch (err) {
        console.error("Feedback transmission failed:", err);
    }
}

// --- TIME-SERIES FILE INGESTION LOGIC ---
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
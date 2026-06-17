const API_BASE = "http://localhost:8000/api";

let triggeredAnomaliesList = [];

const FAULT_SENSOR_MAP = {
    "LPC Blade Fouling":          ["T24", "Nf"],
    "HPC Structural Degradation": ["T30", "P30", "Nc", "Ps30", "HpcBleed"],
    "Combustor Nozzle Clogging":  ["P30", "HpcBleed"],
    "HPT Blade Thermal Erosion":  ["T50", "W31"],
    "LPT Efficiency Loss":        ["T50", "W32"],
};

const VALID_SENSORS = ["T24", "T30", "T50", "P30", "Nf", "Nc", "Ps30", "HpcBleed", "W31", "W32"];

/**
 * Builds a reverse map: sensor -> [fault1, fault2, ...]
 * so each triggered sensor can be updated under every fault that owns it.
 */
const SENSOR_FAULT_MAP = {};
for (const [fault, sensors] of Object.entries(FAULT_SENSOR_MAP)) {
    for (const sensor of sensors) {
        if (!SENSOR_FAULT_MAP[sensor]) SENSOR_FAULT_MAP[sensor] = [];
        SENSOR_FAULT_MAP[sensor].push(fault);
    }
}

/**
 * Extracts all valid sensor IDs mentioned anywhere in a block of text.
 */
function extractSensorsFromText(text) {
    return VALID_SENSORS.filter(sensor => {
        const pattern = new RegExp(`(?<![A-Za-z0-9])${sensor}(?![A-Za-z0-9])`, 'i');
        return pattern.test(text);
    });
}

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

            if (cleanAnswer.includes("CONFIRMED_FAULT:")) {
                const parts = cleanAnswer.split("CONFIRMED_FAULT:");
                cleanAnswer = parts[0].trim();

                // Extract sensors from BOTH user query and full AI response text
                const combinedText = questionText + " " + cleanAnswer;
                triggeredAnomaliesList = extractSensorsFromText(combinedText);

                console.log(`🔍 Sensors detected for feedback: [${triggeredAnomaliesList.join(", ")}]`);

                // Show confirmed fault name from AI (display only)
                const confirmedFaultLabel = parts[1].trim();
                document.getElementById('target-fault-display').innerText = confirmedFaultLabel;
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
    const feedbackPanel = document.getElementById('feedback-panel');

    if (!triggeredAnomaliesList.length) {
        console.warn("No triggered sensors found — nothing to update.");
        feedbackPanel.style.display = "none";
        return;
    }

    // Grab the actual text displayed in the latest assistant response block
    const assistantMessages = document.querySelectorAll('.assistant-msg');
    const diagnosticText = assistantMessages.length > 0 ? assistantMessages[assistantMessages.length - 1].innerText : "";

    // For each triggered sensor, find ALL faults that own that sensor
    // Filter out faults that weren't actively mentioned in the AI's diagnosis response.
    const edgesToUpdate = [];
    for (const sensor of triggeredAnomaliesList) {
        const owningFaults = SENSOR_FAULT_MAP[sensor] || [];
        for (const fault of owningFaults) {
            // Only sync the edge if the fault was part of the final diagnosis printout
            if (diagnosticText.includes(fault)) {
                edgesToUpdate.push({ fault, sensor });
            }
        }
    }

    if (edgesToUpdate.length === 0) {
        console.warn(`No active diagnosed graph edges found for sensors: [${triggeredAnomaliesList.join(", ")}]`);
        feedbackPanel.style.display = "none";
        return;
    }

    console.log(`📡 Updating ${edgesToUpdate.length} edge(s):`, edgesToUpdate);

    let updatedCount = 0;
    let lastWeight = null;
    const updatedSensors = new Set();

    for (const { fault, sensor } of edgesToUpdate) {
        try {
            const response = await fetch(`${API_BASE}/diagnose/feedback`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    failure_mode: fault,
                    sensor_id: sensor,
                    is_correct: isCorrect
                })
            });
            const data = await response.json();
            if (data.status === "Success") {
                updatedCount++;
                lastWeight = data.new_weight;
                updatedSensors.add(sensor);
                console.log(`📈 Edge (${fault} -> ${sensor}) updated to weight: ${data.new_weight}`);
            } else {
                console.warn(`⚠️ Skipped (${fault} -> ${sensor}): ${data.message}`);
            }
        } catch (err) {
            console.error(`Feedback transmission failed for (${fault} -> ${sensor}):`, err);
        }
    }

    if (updatedCount > 0) {
        alert(`📈 Graph Learning Sync: ${updatedCount} edge(s) updated.\nSensors: [${[...updatedSensors].join(", ")}]\nLatest weight: ${lastWeight}`);
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
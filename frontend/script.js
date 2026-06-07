const API_BASE = "http://localhost:8000/api";

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
    chatOutput.innerHTML += `<div class="message assistant-msg" id="${loadingId}">Querying knowledge base...</div>`;
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
            targetLoader.innerText = result.diagnostic_answer;
        } else {
            targetLoader.innerText = `❌ Error: ${result.diagnostic_answer}`;
        }
    } catch (err) {
        document.getElementById(loadingId).innerText = "Connection Error: Could not reach the Diagnostic Core.";
    }
    chatOutput.scrollTop = chatOutput.scrollHeight;
}

document.getElementById('run-test-btn').addEventListener('click', async () => {
    const fileInput = document.getElementById('test-file-input');
    const btn = document.getElementById('run-test-btn');
    const logsOutput = document.getElementById('logs-output');
    const resultsContainer = document.getElementById('test-results');
    
    if (!fileInput.files || fileInput.files.length === 0) {
        alert("Please select or upload a telemetry text file first!");
        return;
    }

    const selectedFile = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", selectedFile);

    btn.disabled = true;
    btn.innerText = "Uploading & Processing...";
    logsOutput.innerText = `Ingesting user file: ${selectedFile.name}...\nReading uploaded operational matrices...\nConnecting to Cloud Neo4j instance thresholds...\nSynchronizing NASA remaining operational countdown timers...\n\n`;
    resultsContainer.style.display = "block";
    
    try {
        const response = await fetch(`${API_BASE}/evaluate-upload`, {
            method: "POST",
            body: formData
        });
        const result = await response.json();
        
        if (result.status === "Success") {
            let logViewText = `📊 EVALUATION LOG FOR UPLOADED TELEMETRY FILE: ${selectedFile.name}\n`;
            logViewText += `================================================\n\n`;
            
            result.data.forEach(item => {
                logViewText += `================================================\n`;
                logViewText += `🔍 DIAGNOSTIC RECORD: ENGINE ASSET PROFILE #${item.engine_id}\n`;
                logViewText += `------------------------------------------------\n`;
                logViewText += `• Final Logged Cycle      : ${item.total_cycles}\n`;
                logViewText += `• Remaining Useful Life   : ${item.remaining_life} cycles\n\n`;
                
                // 1. Compile Anomalies Block
                logViewText += `⚠️ ANOMALIES DETECTED:\n`;
                if (item.anomalies.length > 0) {
                    item.anomalies.forEach(anomaly => {
                        logViewText += `  - ${anomaly}\n`;
                    });
                } else {
                    logViewText += `  - None. All monitored nodes are within constraints.\n`;
                }
                
                logViewText += `\n`; 
                
                // 2. Compile Healthy/Nominal Systems Block
                logViewText += `✅ NOMINAL SYSTEMS OPERATING INTENDEDLY:\n`;
                if (item.nominal.length > 0) {
                    item.nominal.forEach(healthy => {
                        logViewText += `  - ${healthy}\n`;
                    });
                } else {
                    logViewText += `  - Warning: No nominal channels tracked.\n`;
                }
                
                // 3. Dynamic Rule-Based Assessment Text Logic
                logViewText += `\n📋 HIGH-LEVEL SYSTEM STATUS ASSESSMENT:\n`;
                if (item.anomalies.length >= 4) {
                    logViewText += `🔴 CRITICAL DEGRADATION: Multi-system anomalous breaches detected. Urgent compressor overhaul required.\n`;
                } else if (item.anomalies.length > 0) {
                    logViewText += `🟡 WARNING: Incipient performance decay tracked. Monitor thermal parameters closely.\n`;
                } else {
                    logViewText += `🟢 NOMINAL: Core parameter metrics within standardized thermochemical design limits.\n`;
                }
                
                logViewText += `================================================\n\n`;
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
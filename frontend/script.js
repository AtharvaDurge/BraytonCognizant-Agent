const API_BASE_URL = "http://localhost:8000";

async function sendMessage() {
    const userInputField = document.getElementById("user-input");
    const userInput = userInputField.value.trim();
    const chatBox = document.getElementById("chat-box");

    if (!userInput) return;

    chatBox.innerHTML += `
        <p class="user-msg">
            <b>Technician:</b> ${userInput}
        </p>
    `;

    userInputField.value = "";

    chatBox.innerHTML += `
        <p id="thinking" class="ai-msg">
            <b>Diagnostic AI:</b> Analyzing telemetry and graph pathways...
        </p>
    `;

    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch(`${API_BASE_URL}/api/query`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: userInput
            })
        });

        const data = await response.json();

        const thinkingElement = document.getElementById("thinking");
        if (thinkingElement) {
            thinkingElement.remove();
        }

        if (data.status === "Success") {
            const parsedResponse = marked.parse(data.diagnostic_answer);

            chatBox.innerHTML += `
                <div class="ai-msg">
                    <b>Diagnostic AI:</b><br>
                    ${parsedResponse}
                </div>
            `;
        } else {
            chatBox.innerHTML += `
                <p class="error-msg">
                    <b>System Error:</b> ${data.diagnostic_answer}
                </p>
            `;
        }
    } catch (error) {
        const thinkingElement = document.getElementById("thinking");
        if (thinkingElement) {
            thinkingElement.remove();
        }

        chatBox.innerHTML += `
            <p class="error-msg">
                <b>Connection Error:</b> Could not reach the Diagnostic Core.
            </p>
        `;

        console.error("API Connection Error:", error);
    }

    chatBox.scrollTop = chatBox.scrollHeight;
}

document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});
const API_BASE_URL = "http://localhost:5000/";

// Helper function to set status messages
function setStatus(elementId, message, statusType = null) {
    const statusDiv = document.getElementById(elementId);
    statusDiv.textContent = message;
    statusDiv.className = `status ${statusType || ''}`;
}

// Function to fetch and display the chat history
async function fetchChatHistory() {
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat_history`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        if (data.chat_history) {
            const chatBox = document.getElementById("chat-box");
            chatBox.innerHTML = ""; // Clear previous chat
            data.chat_history.forEach(entry => {
                chatBox.innerHTML += `<p>${entry}</p>`;
            });
            
        } else {
            setStatus('chat-status', `Error fetching chat history: ${data.error}`, 'error');
            console.error("Error fetching chat history:", data.error);
        }
    } catch (error) {
         setStatus('chat-status', `Error fetching chat history: ${error}`, 'error');
        console.error("Error fetching chat history:", error);
    }
}

// Function to handle the initial query
async function fetchInitialQuery() {
    const query = document.getElementById("query-input").value;
    if (!query) {
        alert("Please enter a topic.");
        return;
    }

    setStatus('initial-query-status', 'Processing initial query...', 'loading');
    document.getElementById('submit-topic-btn').disabled = true;
    try {
        const response = await fetch(`${API_BASE_URL}/initial_query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        });
         if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (data.message) {
             setStatus('initial-query-status', data.message);
            // Fetch and display the chat history after successful processing
            await fetchChatHistory();
        } else {
           setStatus('initial-query-status', data.error, 'error');
           alert(data.error);
        }
    } catch (error) {
        setStatus('initial-query-status', `Error processing initial query: ${error}`, 'error');
        console.error("Error processing initial query:", error);
    } finally {
        document.getElementById('submit-topic-btn').disabled = false;
    }
}

// Function to handle conversational queries
async function fetchChatResponse() {
    const query = document.getElementById("chat-input").value;
    if (!query) {
        alert("Please enter a question.");
        return;
    }

     setStatus('chat-status', 'Sending question...', 'loading');
     document.getElementById('send-btn').disabled = true;
    try {
        const response = await fetch(`${API_BASE_URL}/conversational_query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        });
         if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        if (data.response) {
            // Fetch and display the updated chat history
            await fetchChatHistory(); // Call fetchChatHistory here
            document.getElementById("chat-input").value = "";
            setStatus('chat-status', 'Question sent.');
        } else {
            setStatus('chat-status', data.error, 'error');
            alert(data.error);
        }
    } catch (error) {
         setStatus('chat-status', `Error sending question: ${error}`, 'error');
        console.error("Error sending question:", error);
    } finally {
         document.getElementById('send-btn').disabled = false;
    }
}

// Function to fetch and display the graph visualization
async function fetchGraph() {
    setStatus('graph-status', 'Loading graph...', 'loading');
    document.getElementById('show-graph-btn').disabled = true;
    try {
        const response = await fetch(`${API_BASE_URL}/show_graph`);
         if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        if (data.sentiment_html && data.relationship_html) {
            const sentimentIframe = document.getElementById("graph-frame-sentiment");
            const relationshipIframe = document.getElementById("graph-frame-relationship");
            
            sentimentIframe.srcdoc = data.sentiment_html; // Use srcdoc to embed HTML
            relationshipIframe.srcdoc = data.relationship_html;
            
            sentimentIframe.style.display = "block";
            relationshipIframe.style.display = "block";
            
             setStatus('graph-status', 'Graph loaded.');
        } else {
            setStatus('graph-status', data.error, 'error');
            alert(data.error);
        }
    } catch(error) {
        setStatus('graph-status', `Error loading graph: ${error}`, 'error');
        console.error("Error loading graph:", error);
    } finally {
         document.getElementById('show-graph-btn').disabled = false;
    }
}

// Function to show chat history
async function showChatHistory() {
    await fetchChatHistory();
}

// Initial fetch of chat history
document.addEventListener('DOMContentLoaded', () => {
    fetchChatHistory();
});
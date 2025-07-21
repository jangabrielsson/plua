// plua2 Main Page JavaScript

let currentTab = 'repl';

function showTab(tabName) {
    // Hide all tab contents
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(content => content.classList.remove('active'));

    // Remove active class from all tabs
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => tab.classList.remove('active'));

    // Show selected tab content
    document.getElementById(tabName).classList.add('active');

    // Add active class to clicked tab
    event.target.classList.add('active');

    currentTab = tabName;

    // Load data when switching to status tab
    if (tabName === 'status') {
        loadStatusData();
    }
}

function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    document.getElementById('current-time').textContent = timeString;
}

async function executeLua(event) {
    event.preventDefault();
    
    const codeInput = document.getElementById('lua-code');
    const executeBtn = document.getElementById('execute-btn');
    const output = document.getElementById('output');
    
    const code = codeInput.value.trim();
    if (!code) return;

    // Disable button and show executing state
    executeBtn.disabled = true;
    executeBtn.textContent = 'Executing...';

    // Add input to output
    const inputLine = document.createElement('div');
    inputLine.className = 'output-line input';
    inputLine.textContent = code;
    output.appendChild(inputLine);

    try {
        const response = await fetch('/plua/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code: code, timeout: 30.0 })
        });

        const result = await response.json();

        if (result.success) {
            if (result.output) {
                const outputLine = document.createElement('div');
                outputLine.className = 'output-line result';
                outputLine.textContent = result.output.trim();
                output.appendChild(outputLine);
            }
            
            if (result.result !== null && result.result !== undefined) {
                const resultLine = document.createElement('div');
                resultLine.className = 'output-line result';
                resultLine.textContent = `=> ${JSON.stringify(result.result)}`;
                output.appendChild(resultLine);
            }
        } else {
            const errorLine = document.createElement('div');
            errorLine.className = 'output-line error';
            errorLine.textContent = `Error: ${result.error || 'Unknown error'}`;
            output.appendChild(errorLine);
        }

    } catch (error) {
        const errorLine = document.createElement('div');
        errorLine.className = 'output-line error';
        errorLine.textContent = `Network Error: ${error.message}`;
        output.appendChild(errorLine);
    }

    // Scroll to bottom
    output.scrollTop = output.scrollHeight;

    // Re-enable button
    executeBtn.disabled = false;
    executeBtn.textContent = 'Execute';

    // Clear input
    codeInput.value = '';
}

function clearOutput() {
    const output = document.getElementById('output');
    output.innerHTML = `
        <div class="output-line info">Output cleared. Ready for new commands.</div>
    `;
}

async function loadStatusData() {
    try {
        // Load info endpoint
        const infoResponse = await fetch('/plua/info');
        const info = await infoResponse.json();

        document.getElementById('api-version').textContent = info.api_version || 'Unknown';
        document.getElementById('lua-version').textContent = info.lua_version || 'Unknown';

        // Load status endpoint
        const statusResponse = await fetch('/plua/status');
        const status = await statusResponse.json();

        document.getElementById('runtime-status').textContent = status.status || 'Unknown';
        document.getElementById('active-timers').textContent = status.active_timers || '0';
        document.getElementById('uptime').textContent = status.uptime || 'Unknown';
        
        // Check if Fibaro API is active
        document.getElementById('fibaro-status').textContent = info.fibaro_api_active ? '✓ Active' : '✗ Inactive';

    } catch (error) {
        console.error('Failed to load status data:', error);
        // Set error states
        document.getElementById('api-version').textContent = 'Error';
        document.getElementById('lua-version').textContent = 'Error';
        document.getElementById('runtime-status').textContent = 'Error';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize clock
    updateClock();
    setInterval(updateClock, 1000);

    // Auto-refresh status when tab is active
    setInterval(() => {
        if (currentTab === 'status') {
            loadStatusData();
        }
    }, 5000);

    // Handle Enter key in textarea (Ctrl+Enter to execute)
    const luaCodeTextarea = document.getElementById('lua-code');
    if (luaCodeTextarea) {
        luaCodeTextarea.addEventListener('keydown', function(event) {
            if (event.ctrlKey && event.key === 'Enter') {
                event.preventDefault();
                executeLua(event);
            }
        });
    }

    // Load initial status data
    setTimeout(loadStatusData, 1000);
});

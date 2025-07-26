// plua Main Page JavaScript

let currentTab = 'repl';
let ws = null;
let currentQuickAppsData = {}; // Store current QuickApps data for comparison

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
    
    // Load QuickApps when switching to quickapps tab
    if (tabName === 'quickapps') {
        loadQuickApps();
        // Connect WebSocket for real-time updates
        connectWebSocket();
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
                outputLine.innerHTML = result.output.trim();
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

    // Auto-refresh status when tab is active (but not QuickApps - they use WebSocket)
    setInterval(() => {
        if (currentTab === 'status') {
            loadStatusData();
        }
        // QuickApps use WebSocket real-time updates, no auto-refresh needed
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

// QuickApps functionality
async function loadQuickApps() {
    const qaGrid = document.getElementById('qa-grid');
    
    try {
        // Show loading state
        qaGrid.innerHTML = '<div class="qa-loading">Loading QuickApps...</div>';
        
        // Get QuickApps list from Lua and convert to JSON string within Lua
        const luaCode = `
            local quickapps = _PY.get_quickapps()
            local result = {}
            
            for i, qa in ipairs(quickapps) do
                local device = {
                    id = qa.device.id,
                    name = qa.device.name,
                    type = qa.device.type
                }
                
                -- Convert UI structure to plain table, filtering out functions
                local ui = {}
                for j, row in ipairs(qa.UI) do
                    if type(row) == "table" then
                        if row.type then
                            -- Single element - filter out function references
                            local element = {}
                            for k, v in pairs(row) do
                                if type(v) ~= "function" then
                                    element[k] = v
                                end
                            end
                            table.insert(ui, element)
                        else
                            -- Array of elements
                            local uiRow = {}
                            for k, element in ipairs(row) do
                                local cleanElement = {}
                                for key, value in pairs(element) do
                                    if type(value) ~= "function" then
                                        cleanElement[key] = value
                                    end
                                end
                                table.insert(uiRow, cleanElement)
                            end
                            table.insert(ui, uiRow)
                        end
                    end
                end
                
                table.insert(result, {
                    device = device,
                    UI = ui
                })
            end
            
            -- Return as JSON string to avoid Lua table serialization issues
            return json.encode(result)
        `;
        
        const response = await fetch('/plua/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: luaCode })
        });
        
        const result = await response.json();
        
        if (result.success && result.result) {
            // Parse the JSON string returned from Lua
            const quickApps = JSON.parse(result.result);
            
            // Store current QuickApps data for comparison
            currentQuickAppsData = {};
            quickApps.forEach(qa => {
                currentQuickAppsData[qa.device.id] = qa;
            });
            
            renderQuickApps(quickApps);
        } else {
            // No QuickApps found or feature not available - show empty tab
            qaGrid.innerHTML = '';
        }
    } catch (error) {
        // Suppress error messages and show empty tab
        console.log('QuickApps not available:', error.message || error);
        qaGrid.innerHTML = '';
    }
}

function renderQuickApps(quickApps) {
    const qaGrid = document.getElementById('qa-grid');
    
    if (!quickApps || quickApps.length === 0) {
        // Show empty tab instead of "No QuickApps running" message
        qaGrid.innerHTML = '';
        return;
    }
    
    qaGrid.innerHTML = '';
    
    quickApps.forEach(qa => {
        const qaCard = createQuickAppCard(qa);
        qaGrid.appendChild(qaCard);
    });
}

function createQuickAppCard(qa) {
    const card = document.createElement('div');
    card.className = 'qa-card';
    card.setAttribute('data-qa-id', qa.device.id); // Changed to data-qa-id for consistency
    
    // Header with name and ID
    const header = document.createElement('div');
    header.className = 'qa-header';
    
    const name = document.createElement('div');
    name.className = 'qa-name';
    name.textContent = qa.device.name || 'Unnamed QuickApp';
    
    const id = document.createElement('div');
    id.className = 'qa-id';
    id.textContent = `ID: ${qa.device.id}`;
    
    header.appendChild(name);
    header.appendChild(id);
    card.appendChild(header);
    
    // Device type
    const type = document.createElement('div');
    type.className = 'qa-type';
    type.textContent = qa.device.type || 'Unknown Type';
    card.appendChild(type);
    
    // UI Elements
    if (qa.UI && qa.UI.length > 0) {
        const uiContainer = document.createElement('div');
        uiContainer.className = 'qa-ui';
        
        qa.UI.forEach((row, index) => {
            const uiRow = createUIRow(row, qa.device.id, index);
            if (uiRow) {
                uiContainer.appendChild(uiRow);
            }
        });
        
        card.appendChild(uiContainer);
    }
    
    return card;
}

function createUIRow(row, deviceId, rowIndex) {
    const elements = Array.isArray(row) ? row : [row];
    
    // Skip empty or invalid rows
    if (!elements.length || elements.every(el => !el || !el.visible)) return null;
    
    const rowDiv = document.createElement('div');
    rowDiv.className = 'qa-ui-row';
    rowDiv.setAttribute('data-element-index', rowIndex); // Add tracking attribute
    
    // Count buttons for layout
    const buttonCount = elements.filter(el => el.type === 'button').length;
    if (buttonCount > 0) {
        rowDiv.classList.add(`buttons-${buttonCount}`);
    }
    
    elements.forEach((element, elementIndex) => {
        if (!element || !element.visible) return;
        
        const uiElement = createUIElement(element, deviceId);
        if (uiElement) {
            // Add element ID attribute for tracking changes via WebSocket
            if (element.id) {
                uiElement.setAttribute('data-element-id', element.id);
            }
            // Add element type attribute for granular updates
            if (element.type) {
                uiElement.setAttribute('data-element-type', element.type);
            }
            // Add element index attribute for tracking individual elements within a row
            uiElement.setAttribute('data-element-sub-index', elementIndex);
            rowDiv.appendChild(uiElement);
        }
    });
    
    return rowDiv.children.length > 0 ? rowDiv : null;
}

function createUIElement(element, deviceId) {
    switch (element.type) {
        case 'label':
            return createLabel(element);
        case 'button':
            return createButton(element, deviceId);
        case 'switch':
            return createSwitch(element, deviceId);
        case 'slider':
            return createSlider(element, deviceId);
        case 'select':
            return createSelect(element, deviceId);
        case 'multi':
            return createMultiSelect(element, deviceId);
        default:
            console.warn('Unknown UI element type:', element.type);
            return null;
    }
}

function createLabel(element) {
    const label = document.createElement('div');
    label.className = 'qa-ui-label qa-label'; // Add qa-label for easy targeting
    label.innerHTML = element.text || '';
    return label;
}

function createButton(element, deviceId) {
    const button = document.createElement('button');
    button.className = 'qa-ui-button qa-button'; // Add qa-button for easy targeting
    button.textContent = element.text || 'Button';
    button.onclick = () => {
        triggerUIAction(deviceId, element.onReleased, element.id, [], 'onReleased'); // Empty values for buttons
    };
    return button;
}

function createSwitch(element, deviceId) {
    const button = document.createElement('button');
    button.className = 'qa-ui-button qa-ui-switch-btn qa-switch'; // Add qa-switch for easy targeting
    button.textContent = element.text || 'Switch';
    
    const isOn = element.value === 'true' || element.value === true;
    button.classList.add(isOn ? 'qa-ui-switch-btn-on' : 'qa-ui-switch-btn-off');
    
    button.onclick = () => {
        // Toggle state visually
        button.classList.toggle('qa-ui-switch-btn-on');
        button.classList.toggle('qa-ui-switch-btn-off');
        
        // Trigger action with true/false value
        const newValue = button.classList.contains('qa-ui-switch-btn-on');
        triggerUIAction(deviceId, element.onReleased, element.id, [newValue], 'onReleased');
    };
    
    return button;
}

function createSlider(element, deviceId) {
    const container = document.createElement('div');
    container.className = 'qa-ui-slider-container';
    
    // Only add label if text exists and is not empty
    if (element.text && element.text.trim() !== '') {
        const label = document.createElement('span');
        label.textContent = element.text;
        label.style.marginRight = '8px';
        container.appendChild(label);
    }
    
    const slider = document.createElement('input');
    slider.type = 'range';
    slider.className = 'qa-ui-slider qa-slider'; // Add qa-slider for easy targeting
    slider.min = element.min || 0;
    slider.max = element.max || 100;
    slider.step = element.step || 1;
    slider.value = element.value || 0;
    
    // Add value display
    const valueDisplay = document.createElement('span');
    valueDisplay.className = 'qa-slider-value';
    valueDisplay.textContent = slider.value;
    container.appendChild(valueDisplay);
    
    // Add tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'slider-tooltip';
    tooltip.textContent = slider.value;
    container.appendChild(tooltip);
    
    slider.oninput = () => {
        valueDisplay.textContent = slider.value;
        tooltip.textContent = slider.value;
        tooltip.classList.add('active');
    };
    
    slider.onchange = () => {
        triggerUIAction(deviceId, element.onChanged, element.id, [slider.value], 'onChanged');
        setTimeout(() => tooltip.classList.remove('active'), 1000);
    };
    
    container.appendChild(slider);
    return container;
}

function createSelect(element, deviceId) {
    const select = document.createElement('select');
    select.className = 'qa-ui-select qa-select'; // Add qa-select for easy targeting
    
    if (element.options) {
        element.options.forEach(option => {
            const opt = document.createElement('option');
            opt.value = option.value || option;
            opt.textContent = option.text || option;
            opt.selected = (option.value || option) === element.value;
            select.appendChild(opt);
        });
    }
    
    select.onchange = () => {
        triggerUIAction(deviceId, element.onToggled, element.id, [select.value], 'onToggled');
    };
    
    return select;
}

function createMultiSelect(element, deviceId) {
    const container = document.createElement('div');
    container.className = 'qa-ui-multidrop';
    
    // Create a hidden select element for easier targeting
    const hiddenSelect = document.createElement('select');
    hiddenSelect.className = 'qa-multi-select';
    hiddenSelect.style.display = 'none';
    hiddenSelect.multiple = true;
    
    const button = document.createElement('div');
    button.className = 'qa-ui-multidrop-btn';
    
    const selectedCount = element.values ? element.values.length : 0;
    if (selectedCount === 0) {
        button.textContent = element.text || 'Choose...';
    } else if (selectedCount === 1) {
        button.textContent = '1 selected';
    } else {
        button.textContent = `${selectedCount} selected`;
    }
    
    const list = document.createElement('div');
    list.className = 'qa-ui-multidrop-list';
    
    if (element.options) {
        element.options.forEach(option => {
            const optionValue = option.value || option;
            const optionText = option.text || option;
            
            // Add to hidden select for easier targeting
            const opt = document.createElement('option');
            opt.value = optionValue;
            opt.textContent = optionText;
            opt.selected = element.values && element.values.includes(optionValue);
            hiddenSelect.appendChild(opt);
            
            const label = document.createElement('label');
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = optionValue;
            checkbox.checked = element.values && element.values.includes(optionValue);
            
            checkbox.onchange = () => {
                const checkboxes = list.querySelectorAll('input[type="checkbox"]');
                const selectedValues = Array.from(checkboxes)
                    .filter(cb => cb.checked)
                    .map(cb => cb.value);
                
                // Update hidden select
                Array.from(hiddenSelect.options).forEach(opt => {
                    opt.selected = selectedValues.includes(opt.value);
                });
                
                // Update button text
                const count = selectedValues.length;
                if (count === 0) {
                    button.textContent = element.text || 'Choose...';
                } else if (count === 1) {
                    button.textContent = '1 selected';
                }
                
                triggerUIAction(deviceId, element.onToggled, element.id, [selectedValues], 'onToggled');
            };
            
            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(optionText));
            list.appendChild(label);
        });
    }
    
    button.onclick = () => {
        container.classList.toggle('open');
    };
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!container.contains(e.target)) {
            container.classList.remove('open');
        }
    });
    
    container.appendChild(hiddenSelect); // Add hidden select for targeting
    container.appendChild(button);
    container.appendChild(list);
    return container;
}

async function triggerUIAction(deviceId, actionName, elementId, values = [], eventType) {
    if (!actionName && !elementId) return;
    
    try {
        const response = await fetch('/api/plugins/callUIEvent', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                deviceID: deviceId,
                elementName: elementId,
                eventType: eventType,
                values: values
            })
        });
        
        if (!response.ok) {
            console.error('Failed to trigger UI action:', response.status, response.statusText);
        }
    } catch (error) {
        console.error('Error triggering UI action:', error);
    }
}

function refreshQuickApps() {
    loadQuickApps();
}

// WebSocket connection for real-time UI updates
function connectWebSocket() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        return; // Already connected
    }
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = function(event) {
        console.log('WebSocket connected');
    };
    
    ws.onmessage = function(event) {
        try {
            const message = JSON.parse(event.data);
            console.log('WebSocket message received:', message); // Debug log
            if (message.type === 'ui_update') {
                handleUIUpdate(message.qa_id, message.data);
            } else if (message.type === 'view_update') {
                handleViewUpdate(message.qa_id, message.element_id, message.property, message.value);
            }
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    };
    
    ws.onclose = function(event) {
        console.log('WebSocket disconnected', event.code, event.reason);
        
        // If the server is shutting down (code 1000 with specific reason), don't try to reconnect immediately
        if (event.code === 1000 && event.reason === "Server shutting down") {
            console.log('Server is shutting down, will retry connection after longer delay');
            // Try to reconnect after 10 seconds in case server restarts
            setTimeout(connectWebSocket, 10000);
        } else {
            // Normal disconnection, try to reconnect after 3 seconds
            setTimeout(connectWebSocket, 3000);
        }
    };
    
    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
    };
}

function handleUIUpdate(qaId, newData) {
    try {
        // Parse the JSON data if it's a string
        const newQAData = typeof newData === 'string' ? JSON.parse(newData) : newData;
        const currentQAData = currentQuickAppsData[qaId];
        
        if (!currentQAData) {
            // New QuickApp, refresh the entire list
            loadQuickApps();
            return;
        }
        
        // Compare UI elements by their id and update only changed ones
        const newUIElements = newQAData.UI || [];
        const currentUIElements = currentQAData.UI || [];
        
        // Create maps for easier lookup by element id
        const newUIMap = {};
        const currentUIMap = {};
        
        newUIElements.forEach(element => {
            if (element.id) {
                newUIMap[element.id] = element;
            }
        });
        
        currentUIElements.forEach(element => {
            if (element.id) {
                currentUIMap[element.id] = element;
            }
        });
        
        // Find elements that have changed
        const changedElements = [];
        
        Object.keys(newUIMap).forEach(elementId => {
            const newElement = newUIMap[elementId];
            const currentElement = currentUIMap[elementId];
            
            // Compare the entire element - if different, it needs updating
            if (!currentElement || JSON.stringify(newElement) !== JSON.stringify(currentElement)) {
                changedElements.push(newElement);
            }
        });
        
        // Update the stored data
        currentQuickAppsData[qaId] = newQAData;
        
        // Re-render only the changed elements
        if (changedElements.length > 0) {
            updateChangedUIElements(qaId, changedElements);
        }
        
    } catch (error) {
        console.error('Error handling UI update:', error);
        // Fallback to full refresh
        loadQuickApps();
    }
}

function updateChangedUIElements(qaId, changedElements) {
    // Find the QuickApp container
    const qaContainer = document.querySelector(`[data-qa-id="${qaId}"]`);
    if (!qaContainer) {
        console.log(`QuickApp container not found for ID ${qaId}, doing full refresh`);
        loadQuickApps();
        return;
    }
    
    changedElements.forEach(element => {
        // Find the existing UI element by its id
        const existingElement = qaContainer.querySelector(`[data-element-id="${element.id}"]`);
        if (existingElement) {
            // Create new element
            const newElement = createUIElement(element);
            newElement.setAttribute('data-element-id', element.id);
            if (element.type) {
                newElement.setAttribute('data-element-type', element.type);
            }
            
            // Replace the existing element
            existingElement.parentNode.replaceChild(newElement, existingElement);
            console.log(`Updated UI element ${element.id} for QA ${qaId}`);
        } else {
            console.log(`UI element ${element.id} not found, doing full refresh`);
            loadQuickApps();
        }
    });
}

// Handle real-time UI updates from WebSocket
function handleUIUpdate(qaId, newData) {
    try {
        // Parse the new data if it's a JSON string
        let parsedData;
        if (typeof newData === 'string') {
            parsedData = JSON.parse(newData);
        } else {
            parsedData = newData;
        }
        
        // Only update if we're on the QuickApps tab
        if (currentTab !== 'quickapps') {
            return;
        }
        
        // Get the existing QA data
        const existingData = currentQuickAppsData[qaId];
        if (!existingData) {
            // New QuickApp, refresh the entire view
            loadQuickApps();
            return;
        }
        
        // Store the new data
        currentQuickAppsData[qaId] = parsedData;
        
        // Update only the changed elements
        updateQuickAppElements(qaId, existingData, parsedData);
        
    } catch (e) {
        console.error('Error handling UI update:', e);
        // Fallback to full refresh
        if (currentTab === 'quickapps') {
            loadQuickApps();
        }
    }
}

// Update only the changed UI elements for a specific QuickApp
function updateQuickAppElements(qaId, oldData, newData) {
    if (!newData.UI || !oldData.UI) return;
    
    const qaContainer = document.querySelector(`[data-qa-id="${qaId}"]`);
    if (!qaContainer) return;
    
    // Compare UI elements and update only changed ones
    for (let i = 0; i < newData.UI.length; i++) {
        const newElement = newData.UI[i];
        const oldElement = oldData.UI[i];
        
        if (!oldElement || !elementsEqual(oldElement, newElement)) {
            // Element changed, update it
            updateSingleUIElement(qaContainer, newElement, i);
        }
    }
}

// Check if two UI elements are equal
function elementsEqual(elem1, elem2) {
    if (!elem1 || !elem2) return false;
    if (elem1.name !== elem2.name) return false;
    if (elem1.type !== elem2.type) return false;
    
    // Check key properties that might change
    const keys = ['text', 'value', 'values', 'options'];
    for (const key of keys) {
        if (elem1[key] !== elem2[key]) {
            if (Array.isArray(elem1[key]) && Array.isArray(elem2[key])) {
                if (JSON.stringify(elem1[key]) !== JSON.stringify(elem2[key])) {
                    return false;
                }
            } else {
                return false;
            }
        }
    }
    
    return true;
}

// Update a single UI element in place
function updateSingleUIElement(qaContainer, element, index) {
    const elementContainer = qaContainer.querySelector(`[data-element-index="${index}"]`);
    if (!elementContainer) return;
    
    // Update based on element type
    switch (element.type) {
        case 'label':
            const label = elementContainer.querySelector('.qa-label');
            // if (label) label.textContent = element.text || '';
            if (label) label.innerHTML = element.text || '';
            break;
            
        case 'button':
            const button = elementContainer.querySelector('.qa-button');
            if (button) button.textContent = element.text || element.caption || 'Button';
            break;
            
        case 'switch':
            const switchInput = elementContainer.querySelector('.qa-switch');
            if (switchInput) switchInput.checked = element.value === true;
            break;
            
        case 'slider':
            const slider = elementContainer.querySelector('.qa-slider');
            const sliderValue = elementContainer.querySelector('.qa-slider-value');
            if (slider) {
                slider.value = element.value || 0;
                slider.min = element.min || 0;
                slider.max = element.max || 100;
            }
            if (sliderValue) {
                sliderValue.textContent = element.value || 0;
            }
            break;
            
        case 'select':
            const select = elementContainer.querySelector('.qa-select');
            if (select) {
                // Update options if they changed
                const newOptions = element.options || [];
                select.innerHTML = '';
                newOptions.forEach(option => {
                    const optionElement = document.createElement('option');
                    optionElement.value = option;
                    optionElement.textContent = option;
                    if (option === element.value) {
                        optionElement.selected = true;
                    }
                    select.appendChild(optionElement);
                });
            }
            break;
            
        case 'multi':
            const multiSelect = elementContainer.querySelector('.qa-multi-select');
            if (multiSelect) {
                // Update options and selection
                const newOptions = element.options || [];
                const selectedValues = element.values || [];
                multiSelect.innerHTML = '';
                newOptions.forEach(option => {
                    const optionElement = document.createElement('option');
                    optionElement.value = option;
                    optionElement.textContent = option;
                    if (selectedValues.includes(option)) {
                        optionElement.selected = true;
                    }
                    multiSelect.appendChild(optionElement);
                });
            }
            break;
    }
}

// Handle granular view updates from WebSocket
function handleViewUpdate(qaId, elementId, property, value) {
    try {
        console.log(`Handling view update for QA ${qaId}, element ${elementId}, property ${property}, value:`, value);
        
        // Only update if we're on the QuickApps tab
        console.log('Current tab:', currentTab);
        // Temporarily bypass tab check for debugging
        // if (currentTab !== 'quickapps') {
        //     console.log('Not on quickapps tab, skipping update');
        //     return;
        // }
        
        // Find the QuickApp container
        const qaContainer = document.querySelector(`[data-qa-id="${qaId}"]`);
        if (!qaContainer) {
            console.log(`QuickApp container not found for ID ${qaId}`);
            return;
        }
        console.log('Found QA container:', qaContainer);
        
        // Find the UI element by its data-element-id
        const elementContainer = qaContainer.querySelector(`[data-element-id="${elementId}"]`);
        if (!elementContainer) {
            console.log(`UI element ${elementId} not found in QA ${qaId}`);
            // Debug: let's see what elements are available
            const allElements = qaContainer.querySelectorAll('[data-element-id]');
            console.log('Available elements with data-element-id:', Array.from(allElements).map(el => el.getAttribute('data-element-id')));
            return;
        }
        console.log('Found element container:', elementContainer);
        
        // Update the specific property based on element type
        const elementType = elementContainer.getAttribute('data-element-type');
        console.log('Element type:', elementType);
        updateElementProperty(elementContainer, elementType, property, value);
        
        // Update the stored data as well
        if (currentQuickAppsData[qaId] && currentQuickAppsData[qaId].UI) {
            const uiElements = currentQuickAppsData[qaId].UI;
            const elementIndex = uiElements.findIndex(el => el.id == elementId);
            if (elementIndex !== -1) {
                uiElements[elementIndex][property] = value;
                console.log('Updated stored data for element', elementId);
            }
        }
        
    } catch (error) {
        console.error('Error handling view update:', error);
    }
}

// Update a specific property of a UI element
function updateElementProperty(elementContainer, elementType, property, value) {
    console.log(`Updating element property: type=${elementType}, property=${property}, value=${value}`);
    switch (elementType) {
        case 'label':
            if (property === 'text') {
                // For labels, the elementContainer IS the label element
                if (elementContainer.classList.contains('qa-label')) {
                    // elementContainer.textContent = value;
                    elementContainer.innerHTML = value;
                    console.log('Updated label text directly');
                } else {
                    // Fallback: look for a child with qa-label class
                    const label = elementContainer.querySelector('.qa-label');
                    if (label) {
                        // label.textContent = value;
                        label.innerHTML = value;
                        console.log('Updated label text via child element');
                    } else {
                        console.log('No qa-label element found');
                    }
                }
            }
            break;
            
        case 'button':
            if (property === 'text' || property === 'caption') {
                const button = elementContainer.querySelector('.qa-button');
                if (button) button.textContent = value;
            }
            break;
            
        case 'switch':
            if (property === 'value') {
                const switchInput = elementContainer.querySelector('.qa-switch');
                if (switchInput) switchInput.checked = value === true || value === 'true';
            }
            break;
            
        case 'slider':
            const slider = elementContainer.querySelector('.qa-slider');
            const sliderValue = elementContainer.querySelector('.qa-slider-value');
            
            if (property === 'value') {
                if (slider) slider.value = value;
                if (sliderValue) sliderValue.textContent = value;
            } else if (property === 'min') {
                if (slider) slider.min = value;
            } else if (property === 'max') {
                if (slider) slider.max = value;
            }
            break;
            
        case 'select':
            const select = elementContainer.querySelector('.qa-select');
            if (property === 'value' && select) {
                select.value = value;
            } else if (property === 'options' && select) {
                // Rebuild options
                select.innerHTML = '';
                (value || []).forEach(option => {
                    const optionElement = document.createElement('option');
                    optionElement.value = option;
                    optionElement.textContent = option;
                    select.appendChild(optionElement);
                });
            }
            break;
            
        case 'multi':
            const multiSelect = elementContainer.querySelector('.qa-multi-select');
            if (property === 'values' && multiSelect) {
                // Update selection
                Array.from(multiSelect.options).forEach(option => {
                    option.selected = (value || []).includes(option.value);
                });
            } else if (property === 'options' && multiSelect) {
                // Rebuild options
                multiSelect.innerHTML = '';
                (value || []).forEach(option => {
                    const optionElement = document.createElement('option');
                    optionElement.value = option;
                    optionElement.textContent = option;
                    multiSelect.appendChild(optionElement);
                });
            }
            break;
            
        default:
            console.log(`Unsupported element type for granular update: ${elementType}`);
    }
}

// Initialize WebSocket connection when page loads
document.addEventListener('DOMContentLoaded', function() {
    connectWebSocket();
});

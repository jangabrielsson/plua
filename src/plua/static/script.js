// --- WebSocket for live QuickApps UI updates ---
(function() {
    let ws;
    function connectWebSocket() {
        ws = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws/quickapps');
        ws.onopen = function() {
            console.log('WebSocket connected to /ws/quickapps');
        };
        ws.onmessage = function(event) {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === 'ui_update') {
                    // Check if QuickApps tab is active or if QuickApps content is visible
                    const quickappsTab = document.getElementById('quickapps');
                    const quickappsContent = document.querySelector('#quickapps.tab-content');
                    const isTabActive = quickappsTab && quickappsTab.classList.contains('active');
                    const isContentVisible = quickappsContent && quickappsContent.classList.contains('active');
                    
                    if (isTabActive || isContentVisible) {
                        loadQuickApps();
                    }
                }
            } catch (e) {
                console.error('WebSocket message error', e);
            }
        };
        ws.onclose = function() {
            console.log('WebSocket disconnected, reconnecting in 2s...');
            // Try to reconnect after a delay
            setTimeout(connectWebSocket, 2000);
        };
        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
    }
    connectWebSocket();
})();

function showTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');

    // Load status if needed
    if (tabName === 'status') {
        loadStatus();
    }
    
    // Load QuickApps if needed
    if (tabName === 'quickapps') {
        loadQuickApps();
    }
}

async function executeCode() {
    const code = document.getElementById('code').value;
    const output = document.getElementById('output');
    const executeBtn = document.getElementById('executeBtn');

    output.textContent = 'Executing...';
    executeBtn.disabled = true;

    try {
        const response = await fetch('/api/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: code })
        });

        const result = await response.json();

        if (result.success) {
            const timeStr = result.execution_time?.toFixed(3) || '0.000';
            const outputText = result.result || 'No output';
            output.innerHTML = `<span class="status success">Success (${timeStr}s)</span><br><br>Output:<br>${outputText}`;
        } else {
            const timeStr = result.execution_time?.toFixed(3) || '0.000';
            output.innerHTML = `<span class="status error">Error (${timeStr}s)</span><br><br>${result.error}`;
        }
    } catch (error) {
        output.innerHTML = `<span class="status error">Request Failed</span><br><br>${error.message}`;
    } finally {
        executeBtn.disabled = false;
    }
}

function clearOutput() {
    document.getElementById('output').textContent = 'Ready to execute Lua code...';
}

async function loadStatus() {
    const statusContent = document.getElementById('statusContent');

    try {
        const response = await fetch('/api/status');
        const status = await response.json();

        const interpreterStatus = status.interpreter_initialized ? 'success' : 'error';
        const interpreterText = status.interpreter_initialized ? 'Initialized' : 'Not Initialized';

        statusContent.innerHTML = `
            <p><strong>Server Time:</strong> ${status.server_time || 'Unknown'}</p>
            <p><strong>Interpreter:</strong> <span class="status ${interpreterStatus}">${interpreterText}</span></p>
            <p><strong>Active Sessions:</strong> ${status.active_sessions || 0}</p>
            <p><strong>Active Timers:</strong> ${status.active_timers || 0}</p>
            <p><strong>Network Operations:</strong> ${status.active_network_operations || 0}</p>
            <p><strong>Python Version:</strong> ${status.python_version || 'Unknown'}</p>
            <p><strong>Lua Version:</strong> ${status.lua_version || 'Unknown'}</p>
            <p><strong>PLua Version:</strong> ${status.plua_version || 'Unknown'}</p>
        `;
    } catch (error) {
        statusContent.innerHTML = `<span class="status error">Failed to load status: ${error.message}</span>`;
    }
}

// Helper to call the /api/plugins/callUIEvent endpoint
async function callUIEvent(deviceID, elementName, eventType, value) {
    const payload = {
        deviceID: deviceID,
        elementName: elementName,
        eventType: eventType
    };
    if (value !== undefined) payload.value = value;
    try {
        await fetch('/api/plugins/callUIEvent', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    } catch (e) {
        console.error('callUIEvent failed', e);
    }
}

async function loadQuickApps() {
    const quickappsList = document.getElementById('quickappsList');
    const loadQABtn = document.getElementById('loadQABtn');

    quickappsList.textContent = 'Loading QuickApps...';
    loadQABtn.disabled = true;

    try {
        const response = await fetch('/api/quickapps');
        const quickapps = await response.json();

        if (quickapps.length === 0) {
            quickappsList.innerHTML = '<span class="status info">No QuickApps currently running</span>';
        } else {
            let html = '<div class="qa-grid">';
            let multiPlaceholders = [];
            quickapps.forEach((qa, qaIdx) => {
                const device = qa.device;
                html += `
                    <div class="qa-card">
                        <div class="qa-header">
                            <span class="qa-name">${device.name}</span>
                            <span class="qa-id">ID: ${device.id}</span>
                        </div>
                        <div class="qa-type">${device.type}</div>
                        <div class="qa-ui">
                            ${renderQuickAppUI(qa.UI, multiPlaceholders, qaIdx, device.id)}
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            quickappsList.innerHTML = html;
            // After HTML is set, replace placeholders with DOM elements
            multiPlaceholders.forEach(ph => {
                const span = document.getElementById(ph.placeholderId);
                if (span) {
                    const el = renderMultiSelect(ph.id, ph.values, ph.selected, ph.onChange, ph.deviceID, ph.eventType);
                    span.replaceWith(el);
                }
            });
        }
    } catch (error) {
        quickappsList.innerHTML = `<span class="status error">Failed to load QuickApps: ${error.message}</span>`;
    } finally {
        loadQABtn.disabled = false;
    }
}

// Render the UI structure for a QuickApp
function renderQuickAppUI(UI, multiPlaceholders, qaIdx, deviceID) {
    if (!UI || !Array.isArray(UI) || UI.length === 0) {
        return '<div class="qa-ui-empty">No UI elements</div>';
    }
    let html = '';
    UI.forEach((row, rowIdx) => {
        let isCompact = false;
        let elements = Array.isArray(row) ? row : [row];
        if (elements.length === 1 && (elements[0].type === 'select' || elements[0].type === 'multi')) {
            isCompact = true;
        }
        html += `<div class="qa-ui-row${isCompact ? ' compact' : ''}">`;
        elements.forEach((el, elIdx) => {
            html += renderUIElement(el, multiPlaceholders, qaIdx, rowIdx, elIdx, deviceID);
        });
        html += '</div>';
    });
    return html;
}

function renderUIElement(el, multiPlaceholders, qaIdx, rowIdx, elIdx, deviceID) {
    if (!el || !el.type) return '';
    switch (el.type) {
        case 'label':
            return `<div class="qa-ui-label">${el.text || ''}</div>`;
        case 'button': {
            // Support onReleased, onLongPressDown, onLongPressReleased
            const events = ['onReleased', 'onLongPressDown', 'onLongPressReleased'];
            const btnId = `btn-${qaIdx}-${rowIdx}-${elIdx}-${Math.random().toString(36).substr(2,6)}`;
            setTimeout(() => {
                const btn = document.getElementById(btnId);
                if (btn) {
                    events.forEach(evt => {
                        if (el[evt] && el[evt] !== "") {
                            btn.addEventListener('click', () => {
                                callUIEvent(deviceID, el.id, evt, undefined);
                            });
                        }
                    });
                }
            }, 0);
            return `<button id="${btnId}" class="qa-ui-button qa-ui-button-grey">${el.text || el.name || 'Button'}</button>`;
        }
        case 'slider': {
            const sliderId = `slider-${qaIdx}-${rowIdx}-${elIdx}-${Math.random().toString(36).substr(2,6)}`;
            const tooltipId = `slider-tooltip-${qaIdx}-${rowIdx}-${elIdx}-${Math.random().toString(36).substr(2,6)}`;
            setTimeout(() => {
                const slider = document.getElementById(sliderId);
                const tooltip = document.getElementById(tooltipId);
                if (slider && tooltip) {
                    function updateTooltip() {
                        tooltip.textContent = slider.value;
                        const min = Number(slider.min || 0);
                        const max = Number(slider.max || 100);
                        const val = Number(slider.value);
                        const percent = (val - min) / (max - min);
                        const thumbWidth = 16;
                        const sliderWidth = slider.offsetWidth;
                        const thumbX = percent * (sliderWidth - thumbWidth) + thumbWidth / 2;
                        tooltip.style.left = `${thumbX}px`;
                    }
                    function showTooltip() {
                        tooltip.classList.add('active');
                        updateTooltip();
                    }
                    function hideTooltip() {
                        tooltip.classList.remove('active');
                    }
                    slider.addEventListener('input', () => {
                        updateTooltip();
                        requestAnimationFrame(updateTooltip);
                        if (el.onChanged && el.onChanged !== "") {
                            callUIEvent(deviceID, el.id, 'onChanged', slider.value);
                        }
                    });
                    slider.addEventListener('mousedown', showTooltip);
                    slider.addEventListener('touchstart', showTooltip);
                    slider.addEventListener('mouseup', hideTooltip);
                    slider.addEventListener('touchend', hideTooltip);
                    slider.addEventListener('mouseleave', hideTooltip);
                    slider.addEventListener('mouseenter', showTooltip);
                }
            }, 0);
            return `<div style="position:relative;display:flex;align-items:center;width:100%;"><input type="range" class="qa-ui-slider" id="${sliderId}" min="${el.min||0}" max="${el.max||100}" step="${el.step||1}" value="${el.value||0}"><span class="slider-tooltip" id="${tooltipId}">${el.value||0}</span></div>`;
        }
        case 'switch': {
            const isOn = el.value === "true" || el.value === true;
            const btnClass = isOn ? 'qa-ui-switch-btn-on' : 'qa-ui-switch-btn-off';
            const btnId = `switch-btn-${qaIdx}-${rowIdx}-${elIdx}-${Math.random().toString(36).substr(2,6)}`;
            setTimeout(() => {
                const btn = document.getElementById(btnId);
                if (btn) {
                    btn.addEventListener('click', () => {
                        btn.classList.toggle('qa-ui-switch-btn-on');
                        btn.classList.toggle('qa-ui-switch-btn-off');
                        const newState = btn.classList.contains('qa-ui-switch-btn-on');
                        if (el.onToggled && el.onToggled !== "") {
                            callUIEvent(deviceID, el.id, 'onToggled', newState ? 'true' : 'false');
                        }
                    });
                }
            }, 0);
            return `<button id="${btnId}" class="qa-ui-button qa-ui-switch-btn ${btnClass}">${el.text || ''}</button>`;
        }
        case 'select': {
            const selectId = `select-${qaIdx}-${rowIdx}-${elIdx}-${Math.random().toString(36).substr(2,6)}`;
            setTimeout(() => {
                const select = document.getElementById(selectId);
                if (select) {
                    select.addEventListener('change', () => {
                        if (el.onToggled && el.onToggled !== "") {
                            callUIEvent(deviceID, el.id, 'onToggled', select.value);
                        }
                    });
                }
            }, 0);
            return `
                <select class="qa-ui-select" id="${selectId}">
                    ${(el.options||[]).map(opt => 
                        `<option value="${opt.value || opt.text}"`
                        + ((el.value && (el.value == opt.value || el.value == opt.text)) ? ' selected' : '') 
                        + `>${opt.text || opt.value}</option>`
                    ).join('')}
                </select>
            `;
        }
        case 'multi': {
            const placeholderId = `multi-ph-${qaIdx}-${rowIdx}-${elIdx}-${Math.random().toString(36).substr(2,6)}`;
            multiPlaceholders.push({
                placeholderId,
                id: el.id,
                values: (el.options||[]).map(o => o.value || o.text),
                selected: el.values || [],
                onChange: (values) => {
                    if (el.onToggled && el.onToggled !== "") {
                        callUIEvent(deviceID, el.id, 'onToggled', '[' + values.join(',') + ']');
                    }
                },
                deviceID,
                eventType: el.onToggled
            });
            return `<span id="${placeholderId}"></span>`;
        }
        default:
            return `<span class="qa-ui-unknown">${el.type}</span>`;
    }
}

function renderMultiSelect(id, values, selected, onChange, deviceID, eventType) {
    const container = document.createElement('div');
    container.className = 'qa-ui-multidrop';
    container.tabIndex = 0;

    const btn = document.createElement('div');
    btn.className = 'qa-ui-multidrop-btn';
    btn.textContent = selected.length === 0 ? 'Choose...' : (selected.length === 1 ? '1 selected' : `${selected.length} selected`);
    btn.tabIndex = 0;
    btn.setAttribute('role', 'button');
    btn.setAttribute('aria-haspopup', 'listbox');
    btn.setAttribute('aria-expanded', 'false');

    const list = document.createElement('div');
    list.className = 'qa-ui-multidrop-list';

    values.forEach(val => {
        const item = document.createElement('label');
        item.className = 'qa-ui-multidrop-item';
        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.value = val;
        cb.checked = selected.includes(val);
        cb.addEventListener('change', (e) => {
            const idx = selected.indexOf(val);
            if (cb.checked && idx === -1) selected.push(val);
            else if (!cb.checked && idx !== -1) selected.splice(idx, 1);
            btn.textContent = selected.length === 0 ? 'Choose...' : (selected.length === 1 ? '1 selected' : `${selected.length} selected`);
            onChange(selected.slice(), deviceID, eventType);
        });
        item.appendChild(cb);
        item.appendChild(document.createTextNode(val));
        list.appendChild(item);
    });

    btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = container.classList.toggle('open');
        btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!container.contains(e.target)) {
            container.classList.remove('open');
            btn.setAttribute('aria-expanded', 'false');
        }
    });

    container.appendChild(btn);
    container.appendChild(list);
    return container;
}

// Event delegation for custom multi-select dropdowns
// Remove quickappsList event listener, use document-level delegation
//
document.addEventListener('click', function(e) {
    // Open/close dropdown if .qa-ui-multidrop-btn is clicked
    if (e.target.classList && e.target.classList.contains('qa-ui-multidrop-btn')) {
        e.stopPropagation();
        const btn = e.target;
        const container = btn.closest('.qa-ui-multidrop');
        if (container) {
            container.classList.toggle('open');
            btn.setAttribute('aria-expanded', container.classList.contains('open') ? 'true' : 'false');
        }
        return;
    }
    // Only close dropdowns if click is outside any .qa-ui-multidrop
    if (!e.target.closest('.qa-ui-multidrop')) {
        document.querySelectorAll('.qa-ui-multidrop').forEach(container => {
            container.classList.remove('open');
            const btn = container.querySelector('.qa-ui-multidrop-btn');
            if (btn) btn.setAttribute('aria-expanded', 'false');
        });
    }
});

// Update button label on checkbox change
// Use event delegation for checkboxes inside .qa-ui-multidrop-list

document.addEventListener('change', function(e) {
    if (e.target.closest('.qa-ui-multidrop-list') && e.target.type === 'checkbox') {
        const list = e.target.closest('.qa-ui-multidrop-list');
        const btn = list.parentNode.querySelector('.qa-ui-multidrop-btn');
        const checked = list.querySelectorAll('input[type="checkbox"]:checked');
        let label = 'Choose...';
        if (checked.length === 1) {
            label = '1 selected';
        } else if (checked.length > 1) {
            label = `${checked.length} selected`;
        }
        btn.textContent = label;
    }
});

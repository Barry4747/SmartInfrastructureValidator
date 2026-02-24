document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Leaflet Map
    // Coordinates set to central Poland
    const map = L.map('map').setView([51.9194, 19.1451], 6);

    // Dark-themed tile layer (CartoDB Dark Matter)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);

    // Stores node markers by ID
    const markers = {};
    let totalLogsCount = 0;

    // Stats elements
    const totalNodesEl = document.getElementById('total-nodes');
    const activeLogsEl = document.getElementById('active-logs');

    // Stats variables for the active log rate calculation
    let logsInLastSecond = 0;
    setInterval(() => {
        activeLogsEl.innerText = logsInLastSecond;
        logsInLastSecond = 0; // reset every second
    }, 1000);

    // 2. Fetch all nodes from API
    async function fetchNodes() {
        try {
            const res = await fetch('/api/nodes/?limit=500');
            const nodes = await res.json();

            totalNodesEl.innerText = nodes.length;

            nodes.forEach(node => {
                // Prevent duplicate markers if fetchNodes is called again
                if (markers[node.node_id]) {
                    return;
                }

                const lat = node.latitude;
                const lon = node.longitude;

                if (lat && lon) {
                    // Create Custom DivIcon
                    const icon = L.divIcon({
                        className: 'custom-marker',
                        html: '', // Empty because we rely on the CSS sizing/border
                        iconSize: [14, 14],
                        iconAnchor: [7, 7],
                        popupAnchor: [0, -10]
                    });

                    const marker = L.marker([lat, lon], { icon: icon }).addTo(map);

                    const faultPort = node.vendor_config?.fault_port;

                    let actionsHTML = '';
                    if (faultPort) {
                        actionsHTML = `
                            <div class="popup-actions" style="margin-top: 15px; display: flex; gap: 8px;">
                                <button onclick="injectFault(${faultPort})" class="btn-danger">Inject Fault</button>
                                <button onclick="fixFault(${faultPort})" class="btn-success">Fix Node</button>
                            </div>
                        `;
                    }

                    const popupHTML = `
                        <div class="popup-title">${node.node_name}</div>
                        <div class="popup-data">
                            <span class="data-label">Type:</span><span class="data-val">${node.node_type}</span>
                            <span class="data-label">IP:</span><span class="data-val">${node.ip_address}</span>
                            <span class="data-label">Max Speed:</span><span class="data-val">${node.max_throughput_mbps} Mbps</span>
                        </div>
                        ${actionsHTML}
                    `;
                    marker.bindPopup(popupHTML);

                    markers[node.node_id] = marker;
                }
            });

        } catch (error) {
            console.error("Failed to load network nodes", error);
        }
    }

    // 3. Set up WebSocket Connection
    function connectWS() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/events`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log("WebSocket connection established!");
            document.querySelector('.system-status p').innerText = "System Online";
            document.querySelector('.pulse-dot').style.backgroundColor = "var(--accent-green)";
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                if (data.type === "new_log") {
                    logsInLastSecond++;
                    totalLogsCount++;
                    handleNewLog(data);
                } else if (data.type === "new_alarm") {
                    handleNewAlarm(data);
                }
            } catch (error) {
                console.error("Error parsing WS message:", error);
            }
        };

        ws.onclose = () => {
            console.warn("WebSocket disconnected. Retrying in 5s...");
            document.querySelector('.system-status p').innerText = "System Offline - Reconnecting...";
            document.querySelector('.pulse-dot').style.backgroundColor = "var(--accent-red)";
            setTimeout(connectWS, 5000);
        };
    }

    // Prevents spamming the API if many unknown node logs arrive at once
    let isFetchingNodes = false;

    // 4. Handle Visual Feedback for a New Log
    function handleNewLog(payload) {
        const nodeId = payload.node_id;
        const logData = payload.log;

        if (markers[nodeId]) {
            const marker = markers[nodeId];

            // Brief highlight effect on the marker
            const iconEl = marker.getElement();
            if (iconEl) {
                iconEl.style.boxShadow = "0 0 20px var(--accent-green)";
                iconEl.style.backgroundColor = "var(--accent-green)";
                setTimeout(() => {
                    iconEl.style.boxShadow = "0 0 10px rgba(51, 170, 255, 0.5)";
                    iconEl.style.backgroundColor = "var(--bg-secondary)";
                }, 400);
            }

            // Create notification bubble container
            const bubbleDiv = document.createElement('div');
            bubbleDiv.className = 'log-bubble-container';

            // Generate Inner Bubble content depending on what data we want to show
            // E.g. showing connected users as typical info log
            bubbleDiv.innerHTML = `
                <div class="log-bubble">
                    <i class="fa-solid fa-bolt"></i>
                    <span>Log: ${logData.connected_users} Users</span>
                </div>
            `;

            // Append the div to the marker's icon element
            if (iconEl) {
                iconEl.appendChild(bubbleDiv);

                // Remove the element after animation ends
                setTimeout(() => {
                    if (bubbleDiv.parentElement) {
                        bubbleDiv.parentElement.removeChild(bubbleDiv);
                    }
                }, 3000); // the CSS animation is 3s long
            }
        } else {
            // Node not found on map. It was likely added after we loaded.
            if (!isFetchingNodes) {
                isFetchingNodes = true;
                fetchNodes().then(() => {
                    isFetchingNodes = false;
                    // Try handling it again if the node is now loaded
                    if (markers[nodeId]) {
                        handleNewLog(payload);
                    }
                });
            }
        }
    }

    // 5. Handle Visual Feedback for an Alarm
    function handleNewAlarm(payload) {
        const nodeId = payload.node_id;

        if (markers[nodeId]) {
            const marker = markers[nodeId];
            const iconEl = marker.getElement();

            if (iconEl) {
                // Flash red for alarm
                iconEl.style.boxShadow = "0 0 25px var(--accent-red)";
                iconEl.style.backgroundColor = "var(--accent-red)";
                iconEl.style.borderColor = "var(--accent-red)";

                setTimeout(() => {
                    iconEl.style.boxShadow = "0 0 10px rgba(51, 170, 255, 0.5)";
                    iconEl.style.backgroundColor = "var(--bg-secondary)";
                    iconEl.style.borderColor = "var(--accent-blue)";
                }, 1000);
            }

            const bubbleDiv = document.createElement('div');
            bubbleDiv.className = 'log-bubble-container';
            // Override animation layer to ensure alarm shows up top
            bubbleDiv.style.zIndex = "1001";
            bubbleDiv.style.left = "0px";    // Move to the right side of the icon to prevent overlap
            bubbleDiv.style.bottom = "30px";  // slightly higher

            bubbleDiv.innerHTML = `
                <div class="log-bubble" style="background: linear-gradient(135deg, rgba(255,51,102,0.9), rgba(200,0,50,0.7)); box-shadow: 0 5px 15px var(--glow-red);">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                    <span>${payload.severity}: ${payload.description}</span>
                </div>
            `;

            if (iconEl) {
                iconEl.appendChild(bubbleDiv);
                setTimeout(() => {
                    if (bubbleDiv.parentElement) {
                        bubbleDiv.parentElement.removeChild(bubbleDiv);
                    }
                }, 4000);
            }
        } else {
            // Node not found on map, try to fetch it first so we don't lose the alarm
            if (!isFetchingNodes) {
                isFetchingNodes = true;
                fetchNodes().then(() => {
                    isFetchingNodes = false;
                    if (markers[nodeId]) {
                        handleNewAlarm(payload);
                    }
                });
            }
        }
    }

    // 6. Handle Clear Nodes Button
    const btnClearNodes = document.getElementById('btn-clear-nodes');
    if (btnClearNodes) {
        btnClearNodes.addEventListener('click', async () => {
            if (confirm("Are you sure you want to delete all nodes? This will also delete all their logs and alarms.")) {
                try {
                    const response = await fetch('/api/nodes/', { method: 'DELETE' });
                    const result = await response.json();

                    if (response.ok) {
                        alert(result.message);

                        // Clear markers from map
                        for (const nodeId in markers) {
                            map.removeLayer(markers[nodeId]);
                        }

                        // Reset state
                        for (const prop of Object.getOwnPropertyNames(markers)) {
                            delete markers[prop];
                        }
                        totalNodesEl.innerText = '0';
                    } else {
                        alert("Failed to delete nodes.");
                    }
                } catch (error) {
                    console.error("Error deleting nodes:", error);
                    alert("Error deleting nodes.");
                }
            }
        });
    }

    // Launch!
    fetchNodes();
    connectWS();
});

// Expose fault handlers to global scope for inline onclick handlers
window.injectFault = async function (port) {
    try {
        const res = await fetch(`http://localhost:${port}/api/fault/cooling`, { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
            alert(`Fault injected successfully: ${data.message}`);
        } else {
            alert(`Failed to inject fault: ${res.statusText}`);
        }
    } catch (err) {
        console.error("Error injecting fault:", err);
        alert("Network error while injecting fault. Is the port mapped correctly?");
    }
};

window.fixFault = async function (port) {
    try {
        const res = await fetch(`http://localhost:${port}/api/fault/fix`, { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
            alert(`Node fixed successfully: ${data.message}`);
        } else {
            alert(`Failed to fix node: ${res.statusText}`);
        }
    } catch (err) {
        console.error("Error fixing node:", err);
        alert("Network error while fixing node. Is the port mapped correctly?");
    }
};

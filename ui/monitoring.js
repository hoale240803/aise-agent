document.addEventListener('DOMContentLoaded', () => {
    // Initialize WebSocket connection
    const ws = new WebSocket('ws://localhost:8080/monitoring');

    // Initialize charts
    const cpuChart = initializeChart('cpuChart', 'CPU Usage', '%');
    const memoryChart = initializeChart('memoryChart', 'Memory Usage', 'MB');

    // Agent status updates
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateAgentStatus(data.agents);
        updateActivityLog(data.logs);
        updatePerformanceMetrics(data.metrics);
    };

    // Filter controls
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            filterLogs(button.textContent.toLowerCase());
        });
    });

    // Search functionality
    const searchInput = document.querySelector('.search-controls input');
    searchInput.addEventListener('input', (e) => {
        filterLogsBySearch(e.target.value);
    });

    // Clear search
    const clearButton = document.querySelector('.clear-btn');
    clearButton.addEventListener('click', () => {
        searchInput.value = '';
        filterLogsBySearch('');
    });

    // Agent control buttons
    const controlButtons = document.querySelectorAll('.control-btn');
    controlButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            const action = e.target.closest('.control-btn');
            const agent = action.closest('.control-card').querySelector('h3').textContent;
            const actionType = action.classList.contains('pause') ? 'pause' :
                action.classList.contains('resume') ? 'resume' : 'restart';

            try {
                const response = await fetch('/api/agents/control', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        agent,
                        action: actionType
                    })
                });

                if (!response.ok) {
                    throw new Error('Failed to execute action');
                }

                // Update UI based on response
                updateAgentStatusUI(agent, actionType);
            } catch (error) {
                console.error('Error:', error);
                // Show error notification
                addLogEntry('error', 'System', `Failed to ${actionType} ${agent}: ${error.message}`);
            }
        });
    });

    // Settings changes
    const settingsSelects = document.querySelectorAll('.setting-item select');
    settingsSelects.forEach(select => {
        select.addEventListener('change', async (e) => {
            const setting = e.target.closest('.setting-item').querySelector('label').textContent;
            const value = e.target.value;
            const agent = e.target.closest('.control-card').querySelector('h3').textContent;

            try {
                const response = await fetch('/api/agents/settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        agent,
                        setting,
                        value
                    })
                });

                if (!response.ok) {
                    throw new Error('Failed to update setting');
                }

                // Show success notification
                addLogEntry('info', 'System', `Updated ${setting} for ${agent} to ${value}`);
            } catch (error) {
                console.error('Error:', error);
                // Show error notification
                addLogEntry('error', 'System', `Failed to update ${setting} for ${agent}: ${error.message}`);
            }
        });
    });
});

// Helper Functions
function initializeChart(canvasId, label, unit) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: label,
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: unit
                    }
                }
            }
        }
    });
}

function updateAgentStatus(agents) {
    agents.forEach(agent => {
        const card = document.querySelector(`.status-card:has(h3:contains("${agent.name}"))`);
        if (card) {
            updateStatusIndicator(card, agent.status);
            updateAgentMetrics(card, agent.metrics);
        }
    });
}

function updateStatusIndicator(card, status) {
    const indicator = card.querySelector('.status-indicator');
    indicator.className = 'status-indicator';
    indicator.classList.add(status.toLowerCase());
}

function updateAgentMetrics(card, metrics) {
    const metricsContainer = card.querySelector('.agent-metrics');
    metricsContainer.innerHTML = '';

    Object.entries(metrics).forEach(([key, value]) => {
        const metricDiv = document.createElement('div');
        metricDiv.className = 'metric';
        metricDiv.innerHTML = `
            <span class="label">${key}</span>
            <span class="value">${value}</span>
        `;
        metricsContainer.appendChild(metricDiv);
    });
}

function updateActivityLog(logs) {
    const logContainer = document.querySelector('.activity-log');
    logs.forEach(log => {
        addLogEntry(log.type, log.agent, log.message, log.timestamp);
    });
}

function addLogEntry(type, agent, message, timestamp = new Date().toLocaleTimeString()) {
    const logContainer = document.querySelector('.activity-log');
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    logEntry.innerHTML = `
        <span class="timestamp">${timestamp}</span>
        <span class="agent">${agent}</span>
        <span class="message">${message}</span>
        <button class="action-btn">${getActionButtonText(type)}</button>
    `;
    logContainer.insertBefore(logEntry, logContainer.firstChild);
}

function getActionButtonText(type) {
    switch (type) {
        case 'error': return 'Retry';
        case 'warning': return 'Investigate';
        case 'info': return 'Review';
        default: return 'View';
    }
}

function filterLogs(type) {
    const logEntries = document.querySelectorAll('.log-entry');
    logEntries.forEach(entry => {
        if (type === 'all' || entry.classList.contains(type)) {
            entry.style.display = 'grid';
        } else {
            entry.style.display = 'none';
        }
    });
}

function filterLogsBySearch(query) {
    const logEntries = document.querySelectorAll('.log-entry');
    const searchTerm = query.toLowerCase();

    logEntries.forEach(entry => {
        const message = entry.querySelector('.message').textContent.toLowerCase();
        const agent = entry.querySelector('.agent').textContent.toLowerCase();

        if (message.includes(searchTerm) || agent.includes(searchTerm)) {
            entry.style.display = 'grid';
        } else {
            entry.style.display = 'none';
        }
    });
}

function updatePerformanceMetrics(metrics) {
    // Update CPU chart
    updateChartData(cpuChart, metrics.cpu);

    // Update Memory chart
    updateChartData(memoryChart, metrics.memory);

    // Update task queue
    updateTaskQueue(metrics.queue);
}

function updateChartData(chart, data) {
    chart.data.labels.push(new Date().toLocaleTimeString());
    chart.data.datasets[0].data.push(data);

    // Keep only last 20 data points
    if (chart.data.labels.length > 20) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }

    chart.update();
}

function updateTaskQueue(queue) {
    const queueContainer = document.querySelector('.queue-status');
    queueContainer.innerHTML = '';

    queue.forEach((task, index) => {
        const queueItem = document.createElement('div');
        queueItem.className = 'queue-item';
        queueItem.innerHTML = `
            <span class="task-name">${task.name}</span>
            <span class="queue-position">Position: ${index + 1}</span>
        `;
        queueContainer.appendChild(queueItem);
    });
}

function updateAgentStatusUI(agent, action) {
    const card = document.querySelector(`.status-card:has(h3:contains("${agent}"))`);
    if (card) {
        const statusIndicator = card.querySelector('.status-indicator');
        statusIndicator.className = 'status-indicator';

        switch (action) {
            case 'pause':
                statusIndicator.classList.add('paused');
                break;
            case 'resume':
            case 'restart':
                statusIndicator.classList.add('active');
                break;
        }
    }
} 
// DriftLock Dashboard JavaScript

// State
let baselineData = null;
let driftChart = null;
let historyData = [];

// Severity color mapping
const SEVERITY_COLORS = {
    'none': '#10b981',
    'minor': '#3b82f6',
    'moderate': '#f59e0b',
    'severe': '#ef4444',
    'critical': '#991b1b'
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadBaseline();
    loadHistory();
    setupEventListeners();
    initializeChart();
});

// Setup event listeners
function setupEventListeners() {
    document.getElementById('config-form').addEventListener('submit', handleConfigSubmit);
    document.getElementById('load-baseline').addEventListener('click', loadBaselineValues);
    document.getElementById('clear-history').addEventListener('click', clearHistory);
}

// Load baseline configuration
async function loadBaseline() {
    try {
        const response = await fetch('/api/baseline');
        const data = await response.json();
        baselineData = data;

        // Display thresholds
        document.getElementById('threshold-none').textContent = `< ${data.thresholds.none.toFixed(2)}`;
        document.getElementById('threshold-minor').textContent = `< ${data.thresholds.minor.toFixed(2)}`;
        document.getElementById('threshold-moderate').textContent = `< ${data.thresholds.moderate.toFixed(2)}`;
        document.getElementById('threshold-severe').textContent = `< ${data.thresholds.severe.toFixed(2)}`;

        // Display baseline dimensions
        displayBaselineInfo(data.baseline);
    } catch (error) {
        console.error('Failed to load baseline:', error);
        showError('Failed to load baseline configuration');
    }
}

// Display baseline information
function displayBaselineInfo(baseline) {
    const container = document.getElementById('baseline-info');
    const dimensions = baseline.dimensions || {};

    let html = '';
    html += `<div class="baseline-item">
        <strong>Version</strong>
        <span>${baseline.version || 'N/A'}</span>
    </div>`;

    html += `<div class="baseline-item">
        <strong>JSD Tolerance</strong>
        <span>${baseline.jsd_tolerance || 'N/A'}</span>
    </div>`;

    for (const [key, value] of Object.entries(dimensions)) {
        html += `<div class="baseline-item">
            <strong>${capitalize(key)}</strong>
            <span>${value.toFixed(2)}</span>
        </div>`;
    }

    container.innerHTML = html;
}

// Load baseline values into form
function loadBaselineValues() {
    if (!baselineData) {
        showError('Baseline not loaded yet');
        return;
    }

    const dimensions = baselineData.baseline.dimensions || {};
    for (const [key, value] of Object.entries(dimensions)) {
        const input = document.getElementById(key);
        if (input) {
            input.value = value.toFixed(2);
        }
    }
}

// Handle configuration form submission
async function handleConfigSubmit(event) {
    event.preventDefault();

    const config = {
        dimensions: {
            integrity: parseFloat(document.getElementById('integrity').value),
            governance: parseFloat(document.getElementById('governance').value),
            reliability: parseFloat(document.getElementById('reliability').value),
            maintainability: parseFloat(document.getElementById('maintainability').value),
            security: parseFloat(document.getElementById('security').value),
        }
    };

    try {
        const response = await fetch('/api/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(config),
        });

        if (!response.ok) {
            throw new Error('Check failed');
        }

        const result = await response.json();
        displayVerdictResult(result.verdict);
        await loadHistory(); // Refresh history
    } catch (error) {
        console.error('Failed to check configuration:', error);
        showError('Failed to check configuration');
    }
}

// Display verdict result
function displayVerdictResult(verdict) {
    // Update JSD score
    const jsdCard = document.getElementById('jsd-card');
    const jsdScore = document.getElementById('jsd-score');
    jsdScore.textContent = verdict.jsd_score.toFixed(4);

    // Remove all severity classes
    Object.keys(SEVERITY_COLORS).forEach(sev => {
        jsdCard.classList.remove(`severity-${sev}`);
    });

    // Add current severity class
    jsdCard.classList.add(`severity-${verdict.severity}`);

    // Update severity
    const severityCard = document.getElementById('severity-card');
    const severityText = document.getElementById('severity');
    severityText.textContent = verdict.severity.toUpperCase();

    // Remove all severity classes
    Object.keys(SEVERITY_COLORS).forEach(sev => {
        severityCard.classList.remove(`severity-${sev}`);
    });

    // Add current severity class
    severityCard.classList.add(`severity-${verdict.severity}`);

    // Update affected dimensions
    const dimensionsCard = document.getElementById('dimensions-card');
    const affectedCount = document.getElementById('affected-count');
    const dimensionList = document.getElementById('dimension-list');

    affectedCount.textContent = verdict.affected_dimensions.length;
    dimensionList.textContent = verdict.affected_dimensions.length > 0
        ? verdict.affected_dimensions.join(', ')
        : 'None';

    // Determine dimension card color based on drift
    dimensionsCard.classList.remove('severity-none', 'severity-critical');
    dimensionsCard.classList.add(
        verdict.affected_dimensions.length > 0 ? 'severity-critical' : 'severity-none'
    );

    // Update recommendation
    const recommendation = document.getElementById('recommendation');
    recommendation.textContent = verdict.recommendation;
    recommendation.style.borderLeftColor = SEVERITY_COLORS[verdict.severity];
}

// Load drift history
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();
        historyData = data.history;

        // Update history count
        document.getElementById('history-count').textContent =
            `${data.count} check${data.count !== 1 ? 's' : ''} recorded`;

        // Update chart
        updateChart();
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

// Clear drift history
async function clearHistory() {
    if (!confirm('Are you sure you want to clear all history?')) {
        return;
    }

    try {
        const response = await fetch('/api/clear-history', {
            method: 'POST',
        });

        if (response.ok) {
            historyData = [];
            updateChart();
            document.getElementById('history-count').textContent = '0 checks recorded';

            // Reset status display
            document.getElementById('jsd-score').textContent = '--';
            document.getElementById('severity').textContent = '--';
            document.getElementById('affected-count').textContent = '--';
            document.getElementById('dimension-list').textContent = '--';
            document.getElementById('recommendation').textContent = '⏳ Awaiting configuration check...';
        }
    } catch (error) {
        console.error('Failed to clear history:', error);
        showError('Failed to clear history');
    }
}

// Initialize chart
function initializeChart() {
    const ctx = document.getElementById('drift-chart').getContext('2d');

    driftChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'JSD Score',
                data: [],
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.3,
                fill: true,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#e6e8eb'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const index = context.dataIndex;
                            const severity = historyData[index]?.severity || 'unknown';
                            return `JSD: ${context.parsed.y.toFixed(4)} (${severity})`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 0.15,
                    ticks: {
                        color: '#8b92a0'
                    },
                    grid: {
                        color: '#2d3548'
                    }
                },
                x: {
                    ticks: {
                        color: '#8b92a0',
                        maxTicksLimit: 10
                    },
                    grid: {
                        color: '#2d3548'
                    }
                }
            }
        }
    });
}

// Update chart with history data
function updateChart() {
    if (!driftChart || historyData.length === 0) {
        return;
    }

    const labels = historyData.map((entry, index) => {
        const date = new Date(entry.timestamp);
        return date.toLocaleTimeString();
    });

    const data = historyData.map(entry => entry.jsd_score);

    // Update chart colors based on severity
    const colors = historyData.map(entry => SEVERITY_COLORS[entry.severity] || '#6366f1');

    driftChart.data.labels = labels;
    driftChart.data.datasets[0].data = data;
    driftChart.data.datasets[0].pointBackgroundColor = colors;
    driftChart.data.datasets[0].pointBorderColor = colors;

    driftChart.update();
}

// Utility functions
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function showError(message) {
    const recommendation = document.getElementById('recommendation');
    recommendation.textContent = `❌ Error: ${message}`;
    recommendation.style.borderLeftColor = SEVERITY_COLORS['critical'];
}

// Monitor Dashboard JavaScript

let chart = null;
let refreshInterval = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initChart();
    loadStatus();
    loadHistory();

    // Auto refresh every 10 seconds
    refreshInterval = setInterval(() => {
        loadStatus();
        loadHistory();
    }, 10000);

    // Event listeners
    document.getElementById('startBtn').addEventListener('click', startScheduler);
    document.getElementById('stopBtn').addEventListener('click', stopScheduler);
});

// Initialize Chart
function initChart() {
    const ctx = document.getElementById('healthChart').getContext('2d');
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Success Rate (%)',
                    data: [],
                    borderColor: '#73c990',
                    backgroundColor: 'rgba(115, 201, 144, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Failed Count',
                    data: [],
                    borderColor: '#fca0a0',
                    backgroundColor: 'rgba(252, 160, 160, 0.1)',
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#d4d4d4'
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#858585' },
                    grid: { color: '#3e3e42' }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    ticks: { color: '#858585' },
                    grid: { color: '#3e3e42' },
                    title: {
                        display: true,
                        text: 'Success Rate (%)',
                        color: '#73c990'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    ticks: { color: '#858585' },
                    grid: { display: false },
                    title: {
                        display: true,
                        text: 'Failed Count',
                        color: '#fca0a0'
                    }
                }
            }
        }
    });
}

// Load scheduler status
async function loadStatus() {
    try {
        const response = await fetch('/api/scheduler/status');
        const status = await response.json();

        const statusBadge = document.getElementById('statusBadge');
        const nextRunEl = document.getElementById('nextRun');

        if (status.is_running) {
            statusBadge.textContent = 'Running';
            statusBadge.className = 'status-badge status-running';

            if (status.next_run) {
                const nextDate = new Date(status.next_run);
                nextRunEl.textContent = `Next run: ${formatTime(nextDate)}`;
            }
        } else {
            statusBadge.textContent = 'Stopped';
            statusBadge.className = 'status-badge status-stopped';
            nextRunEl.textContent = '';
        }

        // Update interval input
        if (status.interval_minutes) {
            document.getElementById('intervalInput').value = status.interval_minutes;
        }

    } catch (error) {
        console.error('Failed to load status:', error);
    }
}

// Load history and update dashboard
async function loadHistory() {
    try {
        const response = await fetch('/api/scheduler/history?limit=50');
        const history = await response.json();

        if (!history || history.length === 0) {
            return;
        }

        // Update metrics
        const latest = history[history.length - 1];
        document.getElementById('totalChecks').textContent = latest.total || 0;
        document.getElementById('successRate').textContent = (latest.success_rate || 0) + '%';
        document.getElementById('failedCount').textContent = latest.failed || 0;

        if (latest.timestamp) {
            const lastDate = new Date(latest.timestamp);
            document.getElementById('lastCheck').textContent = formatTime(lastDate);
        }

        // Update chart
        updateChart(history);

        // Update history table
        updateHistoryTable(history);

    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

// Update chart with history data
function updateChart(history) {
    const labels = history.map(h => {
        const date = new Date(h.timestamp);
        return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
    });

    const successRates = history.map(h => h.success_rate || 0);
    const failedCounts = history.map(h => h.failed || 0);

    chart.data.labels = labels;
    chart.data.datasets[0].data = successRates;
    chart.data.datasets[1].data = failedCounts;
    chart.update();
}

// Update history table
function updateHistoryTable(history) {
    const tbody = document.getElementById('historyBody');
    tbody.innerHTML = '';

    // Show last 20 entries
    const recentHistory = history.slice(-20).reverse();

    recentHistory.forEach(entry => {
        const tr = document.createElement('tr');

        const timestamp = new Date(entry.timestamp);
        const rateClass = entry.success_rate >= 90 ? 'rate-high' :
            entry.success_rate >= 70 ? 'rate-medium' : 'rate-low';

        tr.innerHTML = `
            <td>${formatDateTime(timestamp)}</td>
            <td>${entry.total}</td>
            <td style="color: #73c990;">${entry.passed}</td>
            <td style="color: #fca0a0;">${entry.failed}</td>
            <td class="success-rate ${rateClass}">${entry.success_rate}%</td>
        `;

        tbody.appendChild(tr);
    });
}

// Start scheduler
async function startScheduler() {
    const interval = parseInt(document.getElementById('intervalInput').value);

    if (interval < 1 || interval > 1440) {
        alert('Please enter a valid interval (1-1440 minutes)');
        return;
    }

    try {
        const response = await fetch('/api/scheduler/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ interval_minutes: interval })
        });

        const result = await response.json();

        if (result.status === 'started') {
            alert(`Scheduler started with ${interval} minute interval`);
            loadStatus();
        } else if (result.status === 'already_running') {
            alert('Scheduler is already running');
        }
    } catch (error) {
        alert('Failed to start scheduler: ' + error);
    }
}

// Stop scheduler
async function stopScheduler() {
    try {
        const response = await fetch('/api/scheduler/stop', {
            method: 'POST'
        });

        const result = await response.json();

        if (result.status === 'stopped') {
            alert('Scheduler stopped');
            loadStatus();
        } else if (result.status === 'not_running') {
            alert('Scheduler is not running');
        }
    } catch (error) {
        alert('Failed to stop scheduler: ' + error);
    }
}

// Format time
function formatTime(date) {
    return date.toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// Format date time
function formatDateTime(date) {
    return date.toLocaleString('ko-KR', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});

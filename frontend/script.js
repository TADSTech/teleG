// Configuration
const API_BASE = 'http://localhost:9999';
const STORAGE_KEY = 'teleG_dashboard';

// State
let state = {
    isOnline: false,
    uptime: 0,
    messageCount: 0,
    alertCount: 0,
    alerts: [],
    lastUpdate: new Date()
};

// Load state from localStorage
function loadState() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
        state = JSON.parse(saved);
    }
}

// Save state to localStorage
function saveState() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadState();
    setupEventListeners();
    updateDashboard();
    checkAuthStatus();  // Check auth on startup
    setInterval(updateDashboard, 5000); // Update every 5 seconds
    setInterval(updateTime, 1000); // Update time every second
    setInterval(checkAuthStatus, 2000); // Check auth every 2 seconds
});

// Setup event listeners
function setupEventListeners() {
    document.getElementById('clearCacheBtn').addEventListener('click', clearCache);
    document.getElementById('restartBtn').addEventListener('click', restartService);
    document.getElementById('logsBtn').addEventListener('click', showLogs);
    document.getElementById('settingsBtn').addEventListener('click', showSettings);
    document.querySelector('.refresh-btn').addEventListener('click', updateDashboard);
}

// Update dashboard
async function updateDashboard() {
    try {
        // Check if service is online
        const response = await fetch(`${API_BASE}/health`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        }).catch(() => null);

        if (response && response.ok) {
            const data = await response.json();
            state.isOnline = true;
            state.messageCount = data.messagesProcessed || 0;
            state.alertCount = data.alertsSent || 0;
            state.uptime = data.uptime || 0;

            // Add sample alerts if none exist
            if (state.alerts.length === 0 && state.alertCount > 0) {
                state.alerts = [
                    {
                        time: new Date(Date.now() - Math.random() * 3600000),
                        message: 'Sample alert from THEABZBRAND'
                    }
                ];
            }

            updateStatusUI('online');
        } else {
            state.isOnline = false;
            updateStatusUI('offline');
        }
    } catch (error) {
        state.isOnline = false;
        updateStatusUI('offline');
    }

    state.lastUpdate = new Date();
    saveState();
    renderUI();
}

// Update status UI
function updateStatusUI(status) {
    const indicator = document.getElementById('statusIndicator');
    const dot = indicator.querySelector('.dot');

    if (status === 'online') {
        dot.className = 'dot active';
        indicator.innerHTML = '<span class="dot active"></span><span style="color: #28a745;">Online</span>';
    } else if (status === 'offline') {
        dot.className = 'dot error';
        indicator.innerHTML = '<span class="dot error"></span><span style="color: #dc3545;">Offline</span>';
    }
}

// Render UI
function renderUI() {
    // Update uptime
    const uptime = formatUptime(state.uptime);
    document.getElementById('uptime').textContent = uptime;

    // Update counts
    document.getElementById('messageCount').textContent = state.messageCount.toLocaleString();
    document.getElementById('alertCount').textContent = state.alertCount;
    document.getElementById('alertBadge').textContent = state.alertCount;

    // Update last alert
    if (state.alerts.length > 0) {
        const lastAlert = state.alerts[0];
        const time = new Date(lastAlert.time);
        const timeStr = time.toLocaleTimeString();
        document.getElementById('lastAlert').textContent = timeStr;
    }

    // Render alerts list
    const alertsList = document.getElementById('alertsList');
    if (state.alerts.length === 0) {
        alertsList.innerHTML = '<p class="empty-state">No alerts yet</p>';
    } else {
        alertsList.innerHTML = state.alerts.slice(0, 10).map((alert, idx) => `
            <div class="alert-item">
                <div class="time">${new Date(alert.time).toLocaleString()}</div>
                <div class="message">${escapeHtml(alert.message)}</div>
            </div>
        `).join('');
    }

    // Update time
    updateTime();
}

// Format uptime
function formatUptime(seconds) {
    if (seconds === 0) return 'N/A';
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const mins = Math.floor((seconds % 3600) / 60);

    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${mins}m`;
    return `${mins}m`;
}

// Update time display
function updateTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });
    document.getElementById('updateTime').textContent = timeStr;
}

// Clear cache
async function clearCache() {
    const btn = document.getElementById('clearCacheBtn');
    const msg = document.getElementById('actionMessage');
    btn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/cache/clear`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            showMessage('Cache cleared successfully ✓', 'success');
            state.messageCount = 0;
            saveState();
        } else {
            showMessage('Failed to clear cache', 'error');
        }
    } catch (error) {
        showMessage('Service unavailable. Clearing local data...', 'warning');
        state.alerts = [];
        state.messageCount = 0;
        saveState();
    }

    btn.disabled = false;
    setTimeout(() => {
        msg.textContent = '';
        msg.className = 'action-message';
    }, 3000);
}

// Restart service
async function restartService() {
    if (!confirm('Restart the telegram monitor service? (This will interrupt monitoring briefly)')) {
        return;
    }

    const btn = document.getElementById('restartBtn');
    btn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/service/restart`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            showMessage('Service restarting... (30 seconds)', 'success');
            setTimeout(() => updateDashboard(), 2000);
        } else {
            showMessage('Failed to restart service', 'error');
        }
    } catch (error) {
        showMessage('Cannot restart remotely. SSH into VPS and run: sudo systemctl restart telegram-monitor', 'warning');
    }

    btn.disabled = false;
    setTimeout(() => {
        document.getElementById('actionMessage').textContent = '';
        document.getElementById('actionMessage').className = 'action-message';
    }, 4000);
}

// Show logs
async function showLogs() {
    const modal = document.getElementById('logsModal');
    const logsText = document.getElementById('logsText');
    modal.style.display = 'flex';
    logsText.textContent = 'Loading logs...';

    try {
        const response = await fetch(`${API_BASE}/logs`);
        if (response.ok) {
            const data = await response.json();
            logsText.textContent = data.logs || 'No logs available';
        } else {
            logsText.textContent = 'Failed to fetch logs';
        }
    } catch (error) {
        logsText.textContent = `Cannot connect to service.\n\nTo view logs on VPS, run:\nsudo journalctl -u telegram-monitor -f`;
    }
}

// Close logs modal
function closeLogsModal() {
    document.getElementById('logsModal').style.display = 'none';
}

// Download logs
function downloadLogs() {
    const logsText = document.getElementById('logsText').textContent;
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(logsText));
    element.setAttribute('download', `telegram-monitor-${new Date().toISOString().slice(0,10)}.log`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

// Show settings
function showSettings() {
    document.getElementById('configSection').style.display = 'block';
    document.querySelector('.config-section').scrollIntoView({ behavior: 'smooth' });
}

// Close settings
function closeSettings() {
    document.getElementById('configSection').style.display = 'none';
}

// Save settings
async function saveSettings() {
    const threshold = document.getElementById('alertThreshold').value;
    const pauseAlerts = document.getElementById('pauseAlerts').checked;

    try {
        const response = await fetch(`${API_BASE}/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                alertThreshold: parseInt(threshold),
                pauseAlerts: pauseAlerts
            })
        });

        if (response.ok) {
            showMessage('Settings saved successfully ✓', 'success');
            setTimeout(() => closeSettings(), 1500);
        } else {
            showMessage('Failed to save settings', 'error');
        }
    } catch (error) {
        showMessage('Cannot connect to service', 'error');
    }
}

// Show message
function showMessage(text, type) {
    const msg = document.getElementById('actionMessage');
    msg.textContent = text;
    msg.className = `action-message ${type}`;
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Check authentication status
async function checkAuthStatus() {
    try {
        const response = await fetch(`${API_BASE}/auth/status`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        }).catch(() => null);

        if (response && response.ok) {
            const data = await response.json();
            
            if (data.state === 'waiting_for_code') {
                showAuthModal(data.message || 'Enter your Telegram verification code');
            } else if (data.state === 'code_received') {
                closeAuthModal();
            } else if (data.state === 'code_timeout') {
                showMessage('⚠️ Code input timed out. Service will retry.', 'warning');
                closeAuthModal();
            }
        }
    } catch (error) {
        // Silently fail - service may not be running
    }
}

// Show auth modal
function showAuthModal(message = '') {
    const modal = document.getElementById('authModal');
    modal.style.display = 'flex';
    
    // Clear previous code
    document.getElementById('authCode').value = '';
    
    // Update message
    if (message) {
        document.getElementById('authMessage').textContent = message;
    }
    
    // Focus on input
    setTimeout(() => {
        document.getElementById('authCode').focus();
    }, 100);
}

// Close auth modal
function closeAuthModal() {
    const modal = document.getElementById('authModal');
    modal.style.display = 'none';
    document.getElementById('authCode').value = '';
}

// Submit authentication code
async function submitAuthCode() {
    const code = document.getElementById('authCode').value.trim();
    
    if (!code) {
        document.getElementById('authMessage').textContent = 'Please enter a code';
        return;
    }
    
    try {
        document.getElementById('authMessage').textContent = 'Submitting...';
        
        const response = await fetch(`${API_BASE}/auth/submit-code`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: code })
        });
        
        if (response.ok) {
            document.getElementById('authMessage').textContent = '✓ Code submitted! Authenticating...';
            setTimeout(() => {
                closeAuthModal();
                showMessage('✓ Authenticated successfully!', 'success');
            }, 1500);
        } else {
            const error = await response.json();
            document.getElementById('authMessage').textContent = error.message || 'Failed to submit code';
        }
    } catch (error) {
        document.getElementById('authMessage').textContent = 'Error: ' + error.message;
    }
}

// Cancel authentication
function cancelAuth() {
    closeAuthModal();
    showMessage('⚠️ Authentication cancelled', 'warning');
}

// Allow Enter key to submit code
document.addEventListener('DOMContentLoaded', () => {
    const authCodeInput = document.getElementById('authCode');
    if (authCodeInput) {
        authCodeInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                submitAuthCode();
            }
        });
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeLogsModal();
        closeSettings();
    }
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        updateDashboard();
    }
});

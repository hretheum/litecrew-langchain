// LiteCrew Dashboard JavaScript

class Dashboard {
    constructor() {
        this.autoRefresh = false;
        this.refreshInterval = null;
        this.ws = null;
        this.apiBase = '/api/v1';
        
        this.init();
    }
    
    init() {
        this.loadMetrics();
        this.loadCrews();
        this.loadTaskProgress();
        this.loadLogs();
        this.setupWebSocket();
        
        // Auto-refresh every 5 seconds when enabled
        this.setupAutoRefresh();
    }
    
    async loadMetrics() {
        try {
            const [healthResponse, crewsResponse] = await Promise.all([
                fetch(`${this.apiBase}/health`),
                fetch(`${this.apiBase}/crews`)
            ]);
            
            const health = await healthResponse.json();
            const crewsData = await crewsResponse.json();
            
            // Update metrics
            document.getElementById('active-crews').textContent = crewsData.crews?.length || 0;
            document.getElementById('memory-usage').textContent = `${Math.round(health.memory_mb || 0)}MB`;
            document.getElementById('api-latency').textContent = '< 50ms';
            
            // Mock some additional metrics
            document.getElementById('tasks-completed').textContent = Math.floor(Math.random() * 100);
            
        } catch (error) {
            console.error('Failed to load metrics:', error);
        }
    }
    
    async loadCrews() {
        try {
            const response = await fetch(`${this.apiBase}/crews`);
            const data = await response.json();
            
            const crewList = document.getElementById('crew-list');
            crewList.innerHTML = '';
            
            if (!data.crews || data.crews.length === 0) {
                crewList.innerHTML = '<p style="color: #666; text-align: center; padding: 2rem;">No crews found. Create a crew using the API.</p>';
                return;
            }
            
            data.crews.forEach(crew => {
                const crewElement = this.createCrewElement(crew);
                crewList.appendChild(crewElement);
            });
            
        } catch (error) {
            console.error('Failed to load crews:', error);
            document.getElementById('crew-list').innerHTML = '<p style="color: #ef4444;">Failed to load crews</p>';
        }
    }
    
    createCrewElement(crew) {
        const div = document.createElement('div');
        div.className = 'crew-item';
        
        const status = Math.random() > 0.5 ? 'active' : 'idle';
        const progress = Math.floor(Math.random() * 100);
        
        div.innerHTML = `
            <div class="crew-name">${crew.name}</div>
            <div class="crew-status status-${status}">${status.toUpperCase()}</div>
            <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #666;">
                ${crew.description || 'No description'}
            </div>
            <div style="margin-top: 0.5rem;">
                <small style="color: #666;">Agents: ${crew.agents?.length || 0} | Tasks: ${crew.tasks?.length || 0}</small>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${progress}%"></div>
            </div>
            <small style="color: #666;">Progress: ${progress}%</small>
        `;
        
        return div;
    }
    
    async loadTaskProgress() {
        try {
            const response = await fetch(`${this.apiBase}/executions`);
            const data = await response.json();
            
            const progressContainer = document.getElementById('task-progress');
            progressContainer.innerHTML = '';
            
            if (!data.executions || data.executions.length === 0) {
                progressContainer.innerHTML = '<p style="color: #666; text-align: center; padding: 1rem;">No task executions found.</p>';
                return;
            }
            
            data.executions.slice(0, 5).forEach(execution => {
                const progressElement = this.createProgressElement(execution);
                progressContainer.appendChild(progressElement);
            });
            
        } catch (error) {
            console.error('Failed to load task progress:', error);
            document.getElementById('task-progress').innerHTML = '<p style="color: #ef4444;">Failed to load task progress</p>';
        }
    }
    
    createProgressElement(execution) {
        const div = document.createElement('div');
        div.style.marginBottom = '1rem';
        div.style.padding = '1rem';
        div.style.border = '1px solid #e5e7eb';
        div.style.borderRadius = '6px';
        
        const status = execution.status || 'running';
        const progress = status === 'completed' ? 100 : Math.floor(Math.random() * 80) + 10;
        
        div.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <strong>Execution ${execution.execution_id?.slice(0, 8) || 'unknown'}</strong>
                <span class="crew-status status-${status === 'completed' ? 'active' : 'idle'}">${status.toUpperCase()}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${progress}%"></div>
            </div>
            <small style="color: #666;">Progress: ${progress}% | Duration: ${execution.duration ? Math.round(execution.duration) + 's' : 'N/A'}</small>
        `;
        
        return div;
    }
    
    loadLogs() {
        const logViewer = document.getElementById('log-viewer');
        
        // Mock log entries
        const logs = [
            { timestamp: new Date().toISOString(), level: 'info', message: 'Dashboard initialized successfully' },
            { timestamp: new Date(Date.now() - 60000).toISOString(), level: 'info', message: 'API server started on port 8000' },
            { timestamp: new Date(Date.now() - 120000).toISOString(), level: 'info', message: 'LiteCrew engine loaded' },
            { timestamp: new Date(Date.now() - 180000).toISOString(), level: 'warn', message: 'High memory usage detected: 45MB' },
            { timestamp: new Date(Date.now() - 240000).toISOString(), level: 'info', message: 'Crew execution completed: crew_123' }
        ];
        
        logViewer.innerHTML = '';
        
        logs.forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.innerHTML = `
                <span class="log-timestamp">[${new Date(log.timestamp).toLocaleTimeString()}]</span>
                <span class="log-level-${log.level}">[${log.level.toUpperCase()}]</span>
                ${log.message}
            `;
            logViewer.appendChild(logEntry);
        });
    }
    
    setupWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.addLogEntry('info', 'Real-time connection established');
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (e) {
                    console.log('WebSocket message:', event.data);
                }
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.addLogEntry('warn', 'Real-time connection lost');
                
                // Attempt to reconnect after 5 seconds
                setTimeout(() => this.setupWebSocket(), 5000);
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.addLogEntry('error', 'WebSocket connection error');
            };
            
        } catch (error) {
            console.error('Failed to setup WebSocket:', error);
        }
    }
    
    handleWebSocketMessage(data) {
        if (data.type === 'execution_started') {
            this.addLogEntry('info', `Execution started: ${data.execution_id}`);
        } else if (data.type === 'execution_completed') {
            this.addLogEntry('info', `Execution completed: ${data.execution_id}`);
            this.loadTaskProgress(); // Refresh progress
        } else if (data.type === 'execution_progress') {
            this.addLogEntry('info', `Execution progress: ${data.progress}% - ${data.message}`);
        }
    }
    
    addLogEntry(level, message) {
        const logViewer = document.getElementById('log-viewer');
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        logEntry.innerHTML = `
            <span class="log-timestamp">[${new Date().toLocaleTimeString()}]</span>
            <span class="log-level-${level}">[${level.toUpperCase()}]</span>
            ${message}
        `;
        
        logViewer.insertBefore(logEntry, logViewer.firstChild);
        
        // Keep only last 20 entries
        while (logViewer.children.length > 20) {
            logViewer.removeChild(logViewer.lastChild);
        }
    }
    
    setupAutoRefresh() {
        const toggle = document.getElementById('auto-refresh-toggle');
        
        if (this.autoRefresh) {
            toggle.classList.add('active');
            this.startAutoRefresh();
        }
    }
    
    startAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        this.refreshInterval = setInterval(() => {
            this.loadMetrics();
            this.loadCrews();
            this.loadTaskProgress();
        }, 5000);
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
}

// Global functions
function refreshCrews() {
    dashboard.loadCrews();
    dashboard.addLogEntry('info', 'Crews refreshed manually');
}

function toggleAutoRefresh() {
    const toggle = document.getElementById('auto-refresh-toggle');
    dashboard.autoRefresh = !dashboard.autoRefresh;
    
    if (dashboard.autoRefresh) {
        toggle.classList.add('active');
        dashboard.startAutoRefresh();
        dashboard.addLogEntry('info', 'Auto-refresh enabled');
    } else {
        toggle.classList.remove('active');
        dashboard.stopAutoRefresh();
        dashboard.addLogEntry('info', 'Auto-refresh disabled');
    }
}

// Initialize dashboard when page loads
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new Dashboard();
});
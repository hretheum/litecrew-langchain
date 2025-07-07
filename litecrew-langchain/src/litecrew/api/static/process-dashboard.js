/**
 * Process type extensions for LiteCrew Dashboard
 */

class ProcessDashboard {
    constructor() {
        this.processTypes = [];
        this.currentCrewId = null;
        this.ws = null;
        this.initializeProcessTypes();
    }

    async initializeProcessTypes() {
        try {
            const response = await fetch('/api/v1/process-types');
            this.processTypes = await response.json();
            this.renderProcessTypeSelector();
        } catch (error) {
            console.error('Failed to load process types:', error);
        }
    }

    renderProcessTypeSelector() {
        const container = document.getElementById('process-selector-container');
        if (!container) return;

        let html = `
            <div class="process-selector">
                <h3>Process Type</h3>
                <div class="process-type-grid">
        `;

        this.processTypes.forEach(type => {
            html += `
                <div class="process-type-card" data-process="${type.name}">
                    <h4>${type.name}</h4>
                    <p>${type.description}</p>
                    ${type.supports_moderator ? '<span class="badge">Supports Moderator</span>' : ''}
                </div>
            `;
        });

        html += `</div></div>`;
        container.innerHTML = html;

        // Add click handlers
        document.querySelectorAll('.process-type-card').forEach(card => {
            card.addEventListener('click', () => this.selectProcessType(card.dataset.process));
        });
    }

    selectProcessType(processType) {
        // Update UI
        document.querySelectorAll('.process-type-card').forEach(card => {
            card.classList.toggle('selected', card.dataset.process === processType);
        });

        // Show config options
        this.showProcessConfig(processType);
    }

    showProcessConfig(processType) {
        const type = this.processTypes.find(t => t.name === processType);
        if (!type) return;

        const container = document.getElementById('process-config-container');
        if (!container) return;

        let html = `
            <div class="process-config">
                <h4>Configuration for ${processType}</h4>
                <form id="process-config-form">
        `;

        type.configurable_options.forEach(option => {
            const example = type.example_config[option];
            html += `
                <div class="form-group">
                    <label for="${option}">${option.replace(/_/g, ' ')}</label>
                    <input type="${typeof example === 'number' ? 'number' : 'text'}" 
                           id="${option}" 
                           name="${option}" 
                           value="${example || ''}"
                           placeholder="${example || ''}">
                </div>
            `;
        });

        html += `
                </form>
            </div>
        `;

        container.innerHTML = html;
    }

    connectWebSocket(crewId) {
        this.currentCrewId = crewId;
        
        // Close existing connection
        if (this.ws) {
            this.ws.close();
        }

        // Create new WebSocket connection
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.ws = new WebSocket(`${protocol}//${window.location.host}/ws/crew/${crewId}`);

        this.ws.onopen = () => {
            console.log('WebSocket connected for crew:', crewId);
            this.updateConnectionStatus(true);
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleProcessEvent(data);
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.updateConnectionStatus(false);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    handleProcessEvent(data) {
        if (data.type === 'process_event') {
            const eventContainer = document.getElementById('process-events');
            if (!eventContainer) return;

            const eventHtml = `
                <div class="process-event ${data.event}">
                    <span class="timestamp">${new Date(data.data.timestamp).toLocaleTimeString()}</span>
                    <span class="event-type">${data.event}</span>
                    <span class="event-data">${JSON.stringify(data.data.data)}</span>
                </div>
            `;

            eventContainer.insertAdjacentHTML('afterbegin', eventHtml);

            // Update visualization if needed
            if (data.event === 'task_completed' || data.event === 'debate_round_completed') {
                this.updateVisualization();
            }
        }
    }

    updateConnectionStatus(connected) {
        const indicator = document.getElementById('ws-status');
        if (indicator) {
            indicator.className = connected ? 'connected' : 'disconnected';
            indicator.textContent = connected ? 'Connected' : 'Disconnected';
        }
    }

    async updateVisualization() {
        if (!this.currentCrewId) return;

        try {
            const response = await fetch(`/api/v1/crews/${this.currentCrewId}/visualization`);
            const vizData = await response.json();
            
            this.renderTimeline(vizData.timeline);
            this.renderAgentStats(vizData.agent_stats);
            
            if (vizData.debate_data) {
                this.renderDebateVisualization(vizData.debate_data);
            } else if (vizData.panel_data) {
                this.renderPanelVisualization(vizData.panel_data);
            }
        } catch (error) {
            console.error('Failed to update visualization:', error);
        }
    }

    renderTimeline(timeline) {
        const container = document.getElementById('process-timeline');
        if (!container || !timeline) return;

        let html = '<div class="timeline">';
        timeline.forEach(event => {
            html += `
                <div class="timeline-event">
                    <div class="timeline-marker"></div>
                    <div class="timeline-content">
                        <strong>${event.agent}</strong> - ${event.phase}
                        <span class="time">+${event.duration_from_start.toFixed(2)}s</span>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        
        container.innerHTML = html;
    }

    renderAgentStats(stats) {
        const container = document.getElementById('agent-stats');
        if (!container || !stats) return;

        let html = '<div class="agent-stats-grid">';
        Object.entries(stats).forEach(([agent, data]) => {
            html += `
                <div class="agent-stat-card">
                    <h4>${agent}</h4>
                    <div class="stat">Turns: ${data.turn_count}</div>
                    <div class="stat">Phases: ${data.phases.join(', ')}</div>
                </div>
            `;
        });
        html += '</div>';
        
        container.innerHTML = html;
    }

    renderDebateVisualization(debateData) {
        const container = document.getElementById('process-specific-viz');
        if (!container) return;

        let html = '<div class="debate-viz"><h3>Debate Progress</h3>';
        
        // Render rounds
        Object.entries(debateData.rounds).forEach(([round, turns]) => {
            html += `<div class="debate-round">
                <h4>Round ${round}</h4>
                <div class="debate-turns">`;
            
            turns.forEach(turn => {
                html += `
                    <div class="debate-turn ${turn.position}">
                        <strong>${turn.agent}</strong> (${turn.position})
                        <p>${turn.summary}</p>
                    </div>
                `;
            });
            
            html += '</div></div>';
        });
        
        html += '</div>';
        container.innerHTML = html;
    }

    renderPanelVisualization(panelData) {
        const container = document.getElementById('process-specific-viz');
        if (!container) return;

        let html = '<div class="panel-viz"><h3>Panel Discussion</h3>';
        
        html += `
            <div class="panel-info">
                <div>Moderator: ${panelData.moderator || 'None'}</div>
                <div>Panelists: ${panelData.panelists.join(', ')}</div>
                <div>Consensus: ${panelData.consensus_reached ? 'Yes' : 'No'}</div>
            </div>
        `;
        
        if (Object.keys(panelData.votes).length > 0) {
            html += '<div class="panel-votes"><h4>Votes</h4>';
            Object.entries(panelData.votes).forEach(([agent, vote]) => {
                html += `<div>${agent}: ${vote}</div>`;
            });
            html += '</div>';
        }
        
        html += '</div>';
        container.innerHTML = html;
    }

    async switchCrewProcess(crewId, processType, processConfig) {
        try {
            const response = await fetch(`/api/v1/crews/${crewId}/process`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    process_type: processType,
                    process_config: processConfig
                })
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Process switched successfully:', result);
                return result;
            } else {
                throw new Error(`Failed to switch process: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error switching process:', error);
            throw error;
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.processDashboard = new ProcessDashboard();
});
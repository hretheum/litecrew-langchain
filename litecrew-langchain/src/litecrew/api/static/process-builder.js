// Process Builder Component for LiteCrew Dashboard

class ProcessBuilder {
    constructor() {
        this.apiBase = '/api/v1';
        this.templates = [];
        this.currentTemplate = null;
        this.formData = {};
        
        this.init();
    }
    
    async init() {
        await this.loadTemplates();
        this.setupEventListeners();
    }
    
    async loadTemplates() {
        try {
            const response = await fetch(`${this.apiBase}/process-templates`);
            this.templates = await response.json();
            this.renderTemplateSelector();
        } catch (error) {
            console.error('Failed to load templates:', error);
            this.showError('Failed to load process templates');
        }
    }
    
    renderTemplateSelector() {
        const container = document.getElementById('template-selector');
        if (!container) return;
        
        let html = `
            <div class="template-grid">
                ${this.templates.map(template => `
                    <div class="template-card" data-template="${template.name}">
                        <h3>${this.formatTemplateName(template.name)}</h3>
                        <p>${template.description}</p>
                        <div class="template-meta">
                            <span class="process-type">${template.process_type}</span>
                            <span class="estimated-time">${this.formatTime(template.estimated_time)}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        container.innerHTML = html;
        
        // Add click handlers
        container.querySelectorAll('.template-card').forEach(card => {
            card.addEventListener('click', () => {
                const templateName = card.dataset.template;
                this.selectTemplate(templateName);
            });
        });
    }
    
    async selectTemplate(templateName) {
        try {
            const response = await fetch(`${this.apiBase}/process-templates/${templateName}`);
            this.currentTemplate = await response.json();
            this.renderConfigForm();
        } catch (error) {
            console.error('Failed to load template details:', error);
            this.showError('Failed to load template details');
        }
    }
    
    renderConfigForm() {
        const container = document.getElementById('config-form');
        if (!container || !this.currentTemplate) return;
        
        // Show config form section
        document.getElementById('template-config-section').style.display = 'block';
        
        let formHtml = `
            <h3>Configure ${this.formatTemplateName(this.currentTemplate.name)}</h3>
            <form id="process-config-form">
        `;
        
        // Add fields based on template type
        const fields = this.getTemplateFields(this.currentTemplate.name);
        fields.forEach(field => {
            formHtml += this.renderFormField(field);
        });
        
        // Add common fields
        formHtml += `
            <div class="form-group">
                <label>
                    <input type="checkbox" id="auto-execute" name="auto_execute" />
                    Start execution immediately after creation
                </label>
            </div>
            
            <div class="form-actions">
                <button type="submit" class="btn btn-primary">Create Crew</button>
                <button type="button" class="btn btn-secondary" onclick="processBuilder.reset()">Cancel</button>
            </div>
        </form>
        `;
        
        container.innerHTML = formHtml;
        
        // Add form submit handler
        document.getElementById('process-config-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitForm();
        });
    }
    
    getTemplateFields(templateName) {
        const fields = [];
        
        switch (templateName) {
            case 'quick-debate':
                fields.push({
                    name: 'topic',
                    label: 'Debate Topic',
                    type: 'text',
                    required: true,
                    placeholder: 'e.g., AI Ethics, Remote Work, Climate Change'
                });
                fields.push({
                    name: 'rounds',
                    label: 'Number of Rounds',
                    type: 'number',
                    default: 3,
                    min: 1,
                    max: 10
                });
                break;
                
            case 'decision-panel':
                fields.push({
                    name: 'decision',
                    label: 'Decision to Make',
                    type: 'text',
                    required: true,
                    placeholder: 'e.g., Choose cloud provider, Select technology stack'
                });
                fields.push({
                    name: 'options',
                    label: 'Options (comma-separated)',
                    type: 'text',
                    required: true,
                    placeholder: 'e.g., AWS, Azure, GCP'
                });
                fields.push({
                    name: 'require_consensus',
                    label: 'Require Consensus',
                    type: 'checkbox',
                    default: true
                });
                break;
                
            case 'brainstorming':
                fields.push({
                    name: 'topic',
                    label: 'Brainstorming Topic',
                    type: 'text',
                    required: true,
                    placeholder: 'e.g., New product features, Marketing strategies'
                });
                fields.push({
                    name: 'min_turns',
                    label: 'Minimum Turns',
                    type: 'number',
                    default: 3,
                    min: 1
                });
                fields.push({
                    name: 'max_turns',
                    label: 'Maximum Turns',
                    type: 'number',
                    default: 10,
                    max: 20
                });
                break;
                
            case 'code-review':
                fields.push({
                    name: 'language',
                    label: 'Programming Language',
                    type: 'select',
                    options: ['Python', 'JavaScript', 'Java', 'Go', 'Rust', 'Other'],
                    default: 'Python'
                });
                fields.push({
                    name: 'code',
                    label: 'Code to Review',
                    type: 'textarea',
                    required: true,
                    placeholder: 'Paste your code here...'
                });
                break;
                
            case 'research-team':
                fields.push({
                    name: 'topic',
                    label: 'Research Topic',
                    type: 'text',
                    required: true,
                    placeholder: 'e.g., Renewable energy, Machine learning trends'
                });
                fields.push({
                    name: 'aspects',
                    label: 'Aspects to Research (comma-separated)',
                    type: 'text',
                    placeholder: 'e.g., technology, economics, policy, future trends'
                });
                break;
                
            case 'auto':
                fields.push({
                    name: 'task',
                    label: 'Task Description',
                    type: 'textarea',
                    required: true,
                    placeholder: 'Describe what you want to accomplish...'
                });
                fields.push({
                    name: 'num_agents',
                    label: 'Number of Agents',
                    type: 'number',
                    default: 3,
                    min: 1,
                    max: 10
                });
                fields.push({
                    name: 'expected_output',
                    label: 'Expected Output',
                    type: 'text',
                    placeholder: 'What should the result look like?'
                });
                break;
        }
        
        return fields;
    }
    
    renderFormField(field) {
        let html = '<div class="form-group">';
        
        switch (field.type) {
            case 'text':
                html += `
                    <label for="${field.name}">${field.label}${field.required ? ' *' : ''}</label>
                    <input type="text" 
                           id="${field.name}" 
                           name="${field.name}" 
                           ${field.required ? 'required' : ''}
                           ${field.placeholder ? `placeholder="${field.placeholder}"` : ''}
                           ${field.default ? `value="${field.default}"` : ''}
                           class="form-control" />
                `;
                break;
                
            case 'number':
                html += `
                    <label for="${field.name}">${field.label}</label>
                    <input type="number" 
                           id="${field.name}" 
                           name="${field.name}" 
                           ${field.min !== undefined ? `min="${field.min}"` : ''}
                           ${field.max !== undefined ? `max="${field.max}"` : ''}
                           ${field.default ? `value="${field.default}"` : ''}
                           class="form-control" />
                `;
                break;
                
            case 'textarea':
                html += `
                    <label for="${field.name}">${field.label}${field.required ? ' *' : ''}</label>
                    <textarea id="${field.name}" 
                              name="${field.name}" 
                              ${field.required ? 'required' : ''}
                              ${field.placeholder ? `placeholder="${field.placeholder}"` : ''}
                              rows="5"
                              class="form-control"></textarea>
                `;
                break;
                
            case 'select':
                html += `
                    <label for="${field.name}">${field.label}</label>
                    <select id="${field.name}" name="${field.name}" class="form-control">
                        ${field.options.map(opt => `
                            <option value="${opt}" ${opt === field.default ? 'selected' : ''}>${opt}</option>
                        `).join('')}
                    </select>
                `;
                break;
                
            case 'checkbox':
                html += `
                    <label>
                        <input type="checkbox" 
                               id="${field.name}" 
                               name="${field.name}" 
                               ${field.default ? 'checked' : ''} />
                        ${field.label}
                    </label>
                `;
                break;
        }
        
        html += '</div>';
        return html;
    }
    
    async submitForm() {
        const form = document.getElementById('process-config-form');
        const formData = new FormData(form);
        
        // Build request data
        const requestData = {
            template: this.currentTemplate.name,
            auto_execute: formData.get('auto_execute') === 'on'
        };
        
        // Add template-specific fields
        for (let [key, value] of formData.entries()) {
            if (key === 'auto_execute') continue;
            
            // Handle comma-separated values
            if (key === 'options' || key === 'aspects') {
                requestData[key] = value.split(',').map(v => v.trim()).filter(v => v);
            } else if (key === 'require_consensus') {
                requestData[key] = value === 'on';
            } else {
                requestData[key] = value;
            }
        }
        
        try {
            const response = await fetch(`${this.apiBase}/crews/quick-start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            this.showSuccess(result);
            
            // Refresh crew list
            if (window.dashboard) {
                window.dashboard.loadCrews();
            }
            
            // Show live view if auto-executed
            if (result.auto_execute && result.execution_id) {
                this.showLiveView(result.crew_id, result.execution_id);
            }
            
        } catch (error) {
            console.error('Failed to create crew:', error);
            this.showError('Failed to create crew: ' + error.message);
        }
    }
    
    showSuccess(result) {
        const container = document.getElementById('result-message');
        if (!container) return;
        
        container.innerHTML = `
            <div class="alert alert-success">
                <h4>Crew Created Successfully!</h4>
                <p>${result.message}</p>
                <div class="crew-details">
                    <strong>Crew ID:</strong> ${result.crew_id}<br>
                    <strong>Name:</strong> ${result.name}<br>
                    <strong>Status:</strong> ${result.status}<br>
                    <strong>Estimated Time:</strong> ${this.formatTime(result.estimated_time)}
                </div>
                ${result.execution_id ? `
                    <div class="execution-details">
                        <strong>Execution ID:</strong> ${result.execution_id}<br>
                        <button class="btn btn-primary" onclick="processBuilder.showLiveView('${result.crew_id}', '${result.execution_id}')">
                            View Live Execution
                        </button>
                    </div>
                ` : `
                    <div class="action-buttons">
                        <a href="${result.execute_url}" class="btn btn-primary">Execute Now</a>
                    </div>
                `}
            </div>
        `;
        
        container.scrollIntoView({ behavior: 'smooth' });
    }
    
    showError(message) {
        const container = document.getElementById('result-message');
        if (!container) return;
        
        container.innerHTML = `
            <div class="alert alert-error">
                <h4>Error</h4>
                <p>${message}</p>
            </div>
        `;
        
        container.scrollIntoView({ behavior: 'smooth' });
    }
    
    showLiveView(crewId, executionId) {
        // Switch to live conversation view
        const liveViewSection = document.getElementById('live-view-section');
        if (!liveViewSection) return;
        
        liveViewSection.style.display = 'block';
        liveViewSection.innerHTML = `
            <h3>Live Execution View</h3>
            <div class="execution-info">
                <span>Crew: ${crewId}</span>
                <span>Execution: ${executionId}</span>
            </div>
            <div id="conversation-container" class="conversation-view">
                <div class="loading">Connecting to live view...</div>
            </div>
        `;
        
        // Start WebSocket connection for live updates
        this.connectToLiveView(crewId, executionId);
        
        liveViewSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    connectToLiveView(crewId, executionId) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${protocol}//${window.location.host}/ws/${crewId}`);
        
        const container = document.getElementById('conversation-container');
        
        ws.onopen = () => {
            container.innerHTML = '<div class="connected">Connected. Waiting for updates...</div>';
        };
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.appendConversationTurn(container, data);
        };
        
        ws.onerror = (error) => {
            container.innerHTML = '<div class="error">Connection error. Please refresh.</div>';
        };
        
        ws.onclose = () => {
            container.innerHTML += '<div class="disconnected">Execution completed or connection closed.</div>';
        };
        
        // Store WebSocket for cleanup
        this.liveViewWs = ws;
    }
    
    appendConversationTurn(container, data) {
        // Clear loading/waiting messages
        if (container.querySelector('.loading, .connected')) {
            container.innerHTML = '';
        }
        
        const turnDiv = document.createElement('div');
        turnDiv.className = `conversation-turn ${data.type}`;
        
        turnDiv.innerHTML = `
            <div class="turn-header">
                <span class="agent-name">${data.agent || 'System'}</span>
                <span class="timestamp">${new Date().toLocaleTimeString()}</span>
            </div>
            <div class="turn-content">${this.formatMessage(data.message || data.content)}</div>
        `;
        
        container.appendChild(turnDiv);
        container.scrollTop = container.scrollHeight;
    }
    
    formatMessage(message) {
        // Basic formatting - escape HTML and convert newlines
        return message
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;')
            .replace(/\n/g, '<br>');
    }
    
    formatTemplateName(name) {
        return name.split('-').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }
    
    formatTime(seconds) {
        if (seconds < 60) return `${seconds}s`;
        const minutes = Math.floor(seconds / 60);
        return `${minutes}m`;
    }
    
    reset() {
        this.currentTemplate = null;
        this.formData = {};
        document.getElementById('template-config-section').style.display = 'none';
        document.getElementById('result-message').innerHTML = '';
        document.getElementById('live-view-section').style.display = 'none';
        
        if (this.liveViewWs) {
            this.liveViewWs.close();
            this.liveViewWs = null;
        }
    }
    
    setupEventListeners() {
        // Add any global event listeners here
    }
}

// Initialize when DOM is ready
if (typeof window !== 'undefined') {
    window.processBuilder = null;
    
    document.addEventListener('DOMContentLoaded', () => {
        window.processBuilder = new ProcessBuilder();
    });
}
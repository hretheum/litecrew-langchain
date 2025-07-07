// Template Gallery Component

class TemplateGallery {
    constructor() {
        this.apiBase = '/api/v1';
        this.templates = [];
        this.featuredScenarios = [];
        
        this.init();
    }
    
    async init() {
        await this.loadTemplates();
        await this.loadFeaturedScenarios();
        this.setupEventListeners();
    }
    
    async loadTemplates() {
        try {
            const response = await fetch(`${this.apiBase}/process-templates`);
            this.templates = await response.json();
        } catch (error) {
            console.error('Failed to load templates:', error);
        }
    }
    
    async loadFeaturedScenarios() {
        // Pre-built scenarios for popular use cases
        this.featuredScenarios = [
            {
                id: 'ai-ethics-debate',
                title: 'AI Ethics Debate',
                description: 'Explore the ethical implications of artificial intelligence',
                template: 'quick-debate',
                config: {
                    topic: 'Artificial Intelligence Ethics',
                    rounds: 4
                },
                tags: ['AI', 'Ethics', 'Technology'],
                difficulty: 'Beginner',
                estimatedTime: 180,
                icon: '🤖'
            },
            {
                id: 'startup-tech-stack',
                title: 'Startup Tech Stack Decision',
                description: 'Choose the best technology stack for a new startup',
                template: 'decision-panel',
                config: {
                    decision: 'technology stack for a SaaS startup',
                    options: ['MEAN Stack', 'LAMP Stack', 'JAMstack', 'Serverless'],
                    require_consensus: true
                },
                tags: ['Startup', 'Technology', 'Decision'],
                difficulty: 'Intermediate',
                estimatedTime: 300,
                icon: '🚀'
            },
            {
                id: 'product-feature-ideas',
                title: 'Product Feature Brainstorming',
                description: 'Generate innovative ideas for your next product features',
                template: 'brainstorming',
                config: {
                    topic: 'new mobile app features',
                    min_turns: 5,
                    max_turns: 12
                },
                tags: ['Product', 'Innovation', 'Mobile'],
                difficulty: 'Beginner',
                estimatedTime: 240,
                icon: '💡'
            },
            {
                id: 'security-code-review',
                title: 'Security-Focused Code Review',
                description: 'Comprehensive security analysis of your code',
                template: 'code-review',
                config: {
                    language: 'Python',
                    code: '# Paste your code here for security review'
                },
                tags: ['Security', 'Code Review', 'Best Practices'],
                difficulty: 'Advanced',
                estimatedTime: 360,
                icon: '🔒'
            },
            {
                id: 'climate-research',
                title: 'Climate Change Research',
                description: 'Comprehensive research on climate change impacts',
                template: 'research-team',
                config: {
                    topic: 'climate change impact on agriculture',
                    aspects: ['environmental effects', 'economic impact', 'adaptation strategies', 'policy solutions']
                },
                tags: ['Research', 'Climate', 'Environment'],
                difficulty: 'Advanced',
                estimatedTime: 600,
                icon: '🌍'
            },
            {
                id: 'marketing-strategy',
                title: 'Marketing Strategy Development',
                description: 'AI-powered marketing strategy creation',
                template: 'auto',
                config: {
                    task: 'Develop a comprehensive digital marketing strategy for a B2B SaaS company targeting small businesses',
                    num_agents: 4,
                    expected_output: 'Complete marketing strategy with channels, budget allocation, and timeline'
                },
                tags: ['Marketing', 'Strategy', 'B2B'],
                difficulty: 'Intermediate',
                estimatedTime: 420,
                icon: '📈'
            }
        ];
    }
    
    renderGallery() {
        const container = document.getElementById('template-gallery');
        if (!container) return;
        
        let html = `
            <div class="gallery-header">
                <h2>Template Gallery</h2>
                <p>Ready-to-use scenarios for common tasks. Click any template to launch with pre-configured settings.</p>
                
                <div class="gallery-filters">
                    <button class="filter-btn active" data-filter="all">All</button>
                    <button class="filter-btn" data-filter="beginner">Beginner</button>
                    <button class="filter-btn" data-filter="intermediate">Intermediate</button>
                    <button class="filter-btn" data-filter="advanced">Advanced</button>
                </div>
            </div>
            
            <div class="featured-section">
                <h3>Featured Scenarios</h3>
                <div class="scenarios-grid">
                    ${this.featuredScenarios.map(scenario => this.renderScenarioCard(scenario)).join('')}
                </div>
            </div>
            
            <div class="templates-section">
                <h3>All Templates</h3>
                <div class="templates-grid">
                    ${this.templates.map(template => this.renderTemplateCard(template)).join('')}
                </div>
            </div>
        `;
        
        container.innerHTML = html;
        this.setupGalleryEventListeners();
    }
    
    renderScenarioCard(scenario) {
        return `
            <div class="scenario-card" data-difficulty="${scenario.difficulty.toLowerCase()}" data-scenario="${scenario.id}">
                <div class="scenario-icon">${scenario.icon}</div>
                <div class="scenario-content">
                    <h4>${scenario.title}</h4>
                    <p>${scenario.description}</p>
                    
                    <div class="scenario-meta">
                        <div class="scenario-tags">
                            ${scenario.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                        <div class="scenario-info">
                            <span class="difficulty ${scenario.difficulty.toLowerCase()}">${scenario.difficulty}</span>
                            <span class="time">${this.formatTime(scenario.estimatedTime)}</span>
                        </div>
                    </div>
                    
                    <div class="scenario-actions">
                        <button class="btn btn-primary" onclick="templateGallery.launchScenario('${scenario.id}')">
                            Launch Now
                        </button>
                        <button class="btn btn-secondary" onclick="templateGallery.customizeScenario('${scenario.id}')">
                            Customize
                        </button>
                        <button class="btn btn-link" onclick="templateGallery.shareScenario('${scenario.id}')">
                            Share
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderTemplateCard(template) {
        return `
            <div class="template-card-mini" data-template="${template.name}">
                <h4>${this.formatTemplateName(template.name)}</h4>
                <p>${template.description}</p>
                <div class="template-meta-mini">
                    <span class="process-type">${template.process_type}</span>
                    <span class="time">${this.formatTime(template.estimated_time)}</span>
                </div>
                <button class="btn btn-outline" onclick="templateGallery.useTemplate('${template.name}')">
                    Use Template
                </button>
            </div>
        `;
    }
    
    setupGalleryEventListeners() {
        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const filter = e.target.dataset.filter;
                this.filterScenarios(filter);
                
                // Update active filter
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
            });
        });
    }
    
    filterScenarios(filter) {
        const scenarios = document.querySelectorAll('.scenario-card');
        
        scenarios.forEach(card => {
            if (filter === 'all' || card.dataset.difficulty === filter) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    async launchScenario(scenarioId) {
        const scenario = this.featuredScenarios.find(s => s.id === scenarioId);
        if (!scenario) return;
        
        try {
            // Create request with pre-configured settings
            const request = {
                template: scenario.template,
                auto_execute: true,
                ...scenario.config
            };
            
            const response = await fetch(`${this.apiBase}/crews/quick-start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(request)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            this.showLaunchSuccess(scenario, result);
            
            // Track usage analytics
            this.trackScenarioUsage(scenarioId);
            
        } catch (error) {
            console.error('Failed to launch scenario:', error);
            this.showError('Failed to launch scenario: ' + error.message);
        }
    }
    
    customizeScenario(scenarioId) {
        const scenario = this.featuredScenarios.find(s => s.id === scenarioId);
        if (!scenario) return;
        
        // Switch to process builder with pre-filled data
        if (typeof showTab === 'function') {
            showTab('builder');
        }
        
        // Wait for builder to load, then populate
        setTimeout(() => {
            if (window.processBuilder) {
                window.processBuilder.selectTemplate(scenario.template);
                
                // Pre-fill form with scenario config
                setTimeout(() => {
                    this.populateForm(scenario.config);
                }, 500);
            }
        }, 100);
    }
    
    populateForm(config) {
        Object.entries(config).forEach(([key, value]) => {
            const input = document.querySelector(`[name="${key}"]`);
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = value;
                } else if (Array.isArray(value)) {
                    input.value = value.join(', ');
                } else {
                    input.value = value;
                }
            }
        });
    }
    
    async shareScenario(scenarioId) {
        const scenario = this.featuredScenarios.find(s => s.id === scenarioId);
        if (!scenario) return;
        
        try {
            const response = await fetch(`${this.apiBase}/process-templates/share`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    template: scenario.template,
                    scenario_id: scenarioId,
                    ...scenario.config
                })
            });
            
            const result = await response.json();
            this.showShareDialog(scenario, result.share_url);
            
        } catch (error) {
            console.error('Failed to create share link:', error);
            this.showError('Failed to create share link');
        }
    }
    
    useTemplate(templateName) {
        // Switch to process builder
        if (typeof showTab === 'function') {
            showTab('builder');
        }
        
        // Select the template
        setTimeout(() => {
            if (window.processBuilder) {
                window.processBuilder.selectTemplate(templateName);
            }
        }, 100);
    }
    
    showLaunchSuccess(scenario, result) {
        const modal = this.createModal(`
            <h3>🚀 ${scenario.title} Launched!</h3>
            <p>Your crew has been created and execution started.</p>
            
            <div class="launch-details">
                <div><strong>Crew ID:</strong> ${result.crew_id}</div>
                <div><strong>Status:</strong> ${result.status}</div>
                <div><strong>Estimated Time:</strong> ${this.formatTime(scenario.estimatedTime)}</div>
            </div>
            
            <div class="modal-actions">
                <button class="btn btn-primary" onclick="this.closest('.modal-overlay').remove(); templateGallery.showLiveView('${result.crew_id}', '${result.execution_id || ''}')">
                    Watch Live
                </button>
                <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">
                    Continue
                </button>
            </div>
        `);
        
        document.body.appendChild(modal);
    }
    
    showShareDialog(scenario, shareUrl) {
        const modal = this.createModal(`
            <h3>📤 Share ${scenario.title}</h3>
            <p>Share this ready-to-use scenario with others:</p>
            
            <div class="share-url-container">
                <input type="text" value="${shareUrl}" readonly class="share-url-input" />
                <button class="btn btn-primary" onclick="templateGallery.copyToClipboard('${shareUrl}')">
                    Copy
                </button>
            </div>
            
            <div class="share-options">
                <h4>Share Options:</h4>
                <div class="share-buttons">
                    <button class="btn btn-social" onclick="templateGallery.shareToTwitter('${scenario.title}', '${shareUrl}')">
                        Twitter
                    </button>
                    <button class="btn btn-social" onclick="templateGallery.shareToLinkedIn('${scenario.title}', '${shareUrl}')">
                        LinkedIn
                    </button>
                    <button class="btn btn-social" onclick="templateGallery.shareByEmail('${scenario.title}', '${shareUrl}')">
                        Email
                    </button>
                </div>
            </div>
            
            <div class="modal-actions">
                <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">
                    Close
                </button>
            </div>
        `);
        
        document.body.appendChild(modal);
    }
    
    createModal(content) {
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.innerHTML = `
            <div class="modal">
                <div class="modal-content">
                    ${content}
                </div>
            </div>
        `;
        
        // Close on overlay click
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.remove();
            }
        });
        
        return overlay;
    }
    
    showLiveView(crewId, executionId) {
        // Switch to monitoring tab or open live view
        if (typeof showTab === 'function') {
            showTab('monitoring');
        }
        
        // Show live view if process builder is available
        if (window.processBuilder) {
            window.processBuilder.showLiveView(crewId, executionId);
        }
    }
    
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Link copied to clipboard!');
        });
    }
    
    shareToTwitter(title, url) {
        const text = encodeURIComponent(`Check out this AI process: ${title}`);
        const shareUrl = `https://twitter.com/intent/tweet?text=${text}&url=${encodeURIComponent(url)}`;
        window.open(shareUrl, '_blank');
    }
    
    shareToLinkedIn(title, url) {
        const shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;
        window.open(shareUrl, '_blank');
    }
    
    shareByEmail(title, url) {
        const subject = encodeURIComponent(`AI Process: ${title}`);
        const body = encodeURIComponent(`I found this interesting AI process that you might like: ${url}`);
        window.location.href = `mailto:?subject=${subject}&body=${body}`;
    }
    
    showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
    
    showError(message) {
        this.showToast('Error: ' + message);
    }
    
    trackScenarioUsage(scenarioId) {
        // Track usage for analytics (in real app, send to analytics service)
        console.log(`Scenario launched: ${scenarioId}`);
        
        // Update local usage count
        const scenario = this.featuredScenarios.find(s => s.id === scenarioId);
        if (scenario) {
            scenario.usage_count = (scenario.usage_count || 0) + 1;
        }
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
    
    setupEventListeners() {
        // Add any global event listeners here
    }
}

// Initialize when DOM is ready
if (typeof window !== 'undefined') {
    window.templateGallery = null;
    
    document.addEventListener('DOMContentLoaded', () => {
        window.templateGallery = new TemplateGallery();
    });
}
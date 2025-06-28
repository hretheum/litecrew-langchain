CREATE TABLE agents (
    id TEXT PRIMARY KEY DEFAULT (hex(randomblob(16))),
    name TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL,
    config JSON NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    stats JSON DEFAULT '{}',
    
    CHECK (json_valid(config)),
    CHECK (json_valid(stats))
);

CREATE INDEX idx_agents_active ON agents(is_active, name);
CREATE TRIGGER update_agents_timestamp 
    AFTER UPDATE ON agents
    BEGIN
        UPDATE agents SET updated_at = CURRENT_TIMESTAMP 
        WHERE id = NEW.id;
    END;
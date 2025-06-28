#!/bin/bash
# Troubleshooting: Agent not responding

# Check agent status
litecrewai agent status <agent_id>

# View agent logs
litecrewai logs agent <agent_id> --tail 100

# Debug mode
LITECREWAI_DEBUG=true litecrewai agent run <agent_id>
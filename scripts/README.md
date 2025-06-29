# CrewAI Enterprise Features Removal Script

## Overview

This script (`remove_enterprise.sh`) removes all enterprise features from CrewAI, creating a single-user, local-only version that preserves core functionality while eliminating cloud dependencies, multi-tenant features, and enterprise authentication.

## What Gets Removed

### 1. Enterprise Modules
- **Cloud sync/storage**: All cloud deployment capabilities
- **Team collaboration**: Multi-user and organization features
- **RBAC/permissions**: Role-based access control
- **Billing/subscriptions**: Payment and subscription management
- **Multi-tenant features**: Organization switching and management
- **SSO/SAML**: Enterprise authentication (Auth0)

### 2. Enterprise Dependencies
- `auth0-python`: Enterprise authentication library
- Cloud deployment APIs
- Tool repository (cloud-based tool sharing)
- Organization management APIs

### 3. Specific Components Removed
- `/src/crewai/cli/authentication/` - Auth0 authentication module
- `/src/crewai/cli/deploy/` - Cloud deployment functionality
- `/src/crewai/cli/organization/` - Multi-tenant organization management
- `/src/crewai/cli/tools/` - Cloud tool repository
- `/src/crewai/cli/plus_api.py` - CrewAI+ API client
- Enterprise documentation in `/docs/enterprise/`
- Enterprise API specifications
- Related test files

## What Gets Preserved

### Core Functionality
- **Agents**: Full agent creation and management
- **Tasks**: Task definition and execution
- **Tools**: Local tool usage and custom tool creation
- **Memory**: All memory systems (short-term, long-term, contextual, entity)
- **Flows**: Flow management and visualization
- **Knowledge**: Knowledge base and embeddings
- **Basic API**: Core CrewAI API functionality
- **Local execution**: All local crew execution capabilities

## Usage

1. **Run the script**:
   ```bash
   cd /Users/hretheum/dev/bezrobocie/crewAI/scripts
   ./remove_enterprise.sh
   ```

2. **Review the changes**:
   - A detailed report will be generated at `enterprise_removal_report.md`
   - A backup of the original project will be created with timestamp

3. **Update dependencies**:
   ```bash
   cd /Users/hretheum/dev/bezrobocie/crewAI/crewai-fork
   uv sync
   ```

4. **Run tests** (optional):
   ```bash
   pytest tests/
   ```

## Script Features

- **Automatic backup**: Creates a timestamped backup before making changes
- **Detailed reporting**: Generates a comprehensive report with diffs
- **Safe execution**: Uses error handling and validation
- **Color-coded output**: Clear visual feedback during execution
- **Preserves core functionality**: Carefully removes only enterprise features

## Post-Removal State

After running the script, CrewAI will:
- Work entirely offline/locally
- Support single-user operation only
- Have no cloud dependencies
- Retain all core AI orchestration features
- Use a simple local authentication stub (always authenticated)

## Rollback

If you need to restore the original version:
1. The script creates a backup at `crewai-fork.backup.{timestamp}`
2. Simply rename or copy the backup to restore:
   ```bash
   rm -rf crewai-fork
   mv crewai-fork.backup.{timestamp} crewai-fork
   ```

## Notes

- The script is idempotent - running it multiple times is safe
- All changes are logged in the report file
- The script preserves the git history (if present)
- Core CrewAI functionality remains fully operational
# GitLab Setup Instructions

## 🚀 Quick Setup

### 1. Set GitLab Token
```bash
# Get your token from: https://gitlab.com/-/profile/personal_access_tokens
export GITLAB_TOKEN="your-personal-access-token"
```

### 2. Run Setup Scripts
```bash
# Make scripts executable
chmod +x scripts/setup-gitlab-*.sh

# Create labels (21 labels)
./scripts/setup-gitlab-labels.sh

# Create milestones (10 phases)
./scripts/setup-gitlab-milestones.sh
```

### 3. Manual GitLab Settings

#### Protected Branches
1. Go to: Settings → Repository → Protected branches
2. Protect `master` branch:
   - Allowed to merge: Maintainers
   - Allowed to push: No one
   - Require approval: ✓

#### Container Registry
1. Go to: Packages & Registries → Container Registry
2. Should be enabled by default
3. Note the registry URL for CI/CD

#### CI/CD Settings
1. Go to: Settings → CI/CD → Variables
2. Add these variables:
   ```
   CI_REGISTRY_USER     = your-gitlab-username
   CI_REGISTRY_PASSWORD = your-gitlab-token
   DISCORD_WEBHOOK      = (optional) your-discord-webhook
   ```

#### Merge Request Settings
1. Go to: Settings → Merge requests
2. Enable:
   - [ ] Delete source branch after merge
   - [ ] Squash commits by default
   - [ ] Show link to create/view merge request

## 📝 Verification Checklist

### Labels (21 total)
- [ ] 4 Priority labels (P0-P3)
- [ ] 5 Type labels (feature, bug, test, docs, performance)
- [ ] 8 Component labels (agent, task, crew, api, memory, storage, llm, monitoring)
- [ ] 4 Status labels (ready, in-progress, review, blocked)

### Milestones (10 total)
- [ ] Phase 0: Project Setup
- [ ] Phase 1: Core Foundation
- [ ] Phase 2: Core Engine
- [ ] Phase 3: LLM Integration Layer
- [ ] Phase 4: Storage Layer
- [ ] Phase 5: API & Dashboard
- [ ] Phase 6: Production Readiness
- [ ] Phase 7: Advanced Memory & Knowledge
- [ ] Phase 8: Advanced Orchestration
- [ ] Phase 9: Production Features

### Issue Templates (4 total)
- [ ] feature.md
- [ ] bug.md
- [ ] performance.md
- [ ] test.md

### Settings
- [ ] Protected branches configured
- [ ] Container Registry enabled
- [ ] CI/CD variables set
- [ ] Merge request settings configured

## 🎉 Success Metrics

When setup is complete, you should be able to:
1. Create issues with templates
2. Assign labels quickly
3. Track progress with milestones
4. Run CI/CD pipelines
5. Use Container Registry

## 🔗 Useful Links
- Project: https://gitlab.com/eof3/litecrewai
- Labels: https://gitlab.com/eof3/litecrewai/-/labels
- Milestones: https://gitlab.com/eof3/litecrewai/-/milestones
- Issues: https://gitlab.com/eof3/litecrewai/-/issues
- CI/CD: https://gitlab.com/eof3/litecrewai/-/pipelines
# LiteCrew Project Context

## Project Overview
Building a lightweight alternative to CrewAI on LangChain foundation. Target: <0.05s import, <30MB RAM, 100% API compatibility.

## Current Sprint
- **Phase**: Not started (Day 0/45)
- **Block**: Ready to begin Phase 1, Block 1.1
- **Status**: Project structure prepared
- **Sprint**: Awaiting sprint start

## Repository Structure
```
litecrew/
├── litecrew-langchain/     # Active development
│   ├── src/               # Source code (basic structure ready)
│   ├── tests/             # Test suite (empty)
│   ├── benchmarks/        # Performance tests (empty)
│   └── docs/              # Documentation
│       ├── IMPLEMENTATION_ROADMAP.md  # 45-day plan
│       ├── PROJECT_WORKFLOW.md        # How to work
│       └── VIBE_CODING_GUIDE.md      # This coding guide
└── [archived materials]
```

## Completed Setup
- [x] Project restructuring done
- [x] Basic package structure created
- [x] Initial LiteAgent, LiteTask, LiteCrew stubs
- [x] Documentation consolidated
- [x] Git repository cleaned and organized
- [x] Roadmap integrated (45-day plan)

## Current Metrics
- Import time: ~0.008s ✅ (LangChain baseline)
- Memory usage: ~17MB ✅ (LangChain baseline)
- Test coverage: 0% (no tests yet)
- Code size: <1MB ✅

## Next Up (Phase 1, Block 1.1)
1. [ ] Create project structure with src/, tests/, benchmarks/
2. [ ] Configure Poetry/pip with minimal requirements.txt
3. [ ] Setup pre-commit hooks (black, mypy, ruff)
4. [ ] Configure pytest with coverage
5. [ ] Create CI/CD pipeline (GitLab CI)

## Known Issues
- No active issues yet
- No CI/CD pipeline configured
- No Docker setup yet

## Dependencies Status
- LangChain: Not yet pinned (need to choose version)
- Python: 3.12 (specified in roadmap)
- Other deps: To be determined

## Performance Baseline
From benchmark results:
- CrewAI: 3.3s import, 208MB RAM
- LangChain: 0.008s import, 17MB RAM
- Target: <0.05s import, <30MB RAM

## Last Session (2025-01-03)
### Completed
- Consolidated 3 implementation plans into IMPLEMENTATION_ROADMAP.md
- Created PROJECT_WORKFLOW.md with container-first approach
- Created VIBE_CODING_GUIDE.md for Claude collaboration
- Cleaned up project structure

### Next Session Should
1. Start Phase 1, Block 1.1
2. Setup development containers
3. Create initial CI/CD pipeline
4. Begin test-first development

## GitLab Status
- Repo: https://gitlab.com/eof3/litecrewai
- Last push: Implementation roadmap consolidation
- Pipeline: Not configured yet
- Issues: Not created yet

## Quick Commands
```bash
# Start new sprint
/sprint-start 1 1.1

# Check current task
/task-check

# End sprint block
/sprint-end
```

---
*Remember: Always update this file before ending a work session!*
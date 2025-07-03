# LiteCrew Project Context

## Project Overview
Building a lightweight alternative to CrewAI on LangChain foundation. Target: <0.05s import, <30MB RAM, 100% API compatibility.

## Current Sprint
- **Phase**: 1 - Core Foundation COMPLETED ✅
- **Block**: All blocks completed with validation
- **Status**: Phase 1 Complete (with issues to fix in Phase 2)
- **Sprint**: Ready for Phase 2

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
- [x] Roadmap integrated (48-day plan with Phase 0)
- [x] GitLab infrastructure configured (milestones, labels, templates)
- [x] Development environment ready (Docker, devcontainer)
- [x] CI/CD pipeline configured

## Current Metrics (Validated)
- Import time: 504ms ❌ (target <50ms) - langchain_openai issue
- Memory usage: 84.6MB ❌ (target <30MB) - heavy dependencies
- Test coverage: 46.9% (15/32 tests pass)
- Code size: <1MB ✅
- Task creation: <1ms ✅
- Context passing: <0.1ms ✅

## Next Up (Phase 2)
### Critical Issues to Fix First:
1. [ ] Remove langchain_openai dependency (causing slow imports)
2. [ ] Make LLM optional/mockable for tests
3. [ ] Reduce memory footprint

### Phase 2 Block 2.1: LiteCrew Orchestration
1. [ ] Create LiteCrew class with agents and tasks
2. [ ] Implement process types (sequential, hierarchical)
3. [ ] Add basic task routing

## Known Issues
- Import time too high (504ms) due to langchain_openai
- Memory usage exceeds target (84.6MB vs 30MB)
- Agent tests require OPENAI_API_KEY
- Mock validation errors in some tests

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
- Phase 0: All setup blocks ✅
- Phase 1 Block 1.1: Project Infrastructure ✅
- Phase 1 Block 1.2: LiteAgent Implementation ✅  
- Phase 1 Block 1.3: LiteTask Implementation ✅
- Validation of all metrics with mixed results
- Fixed task_id validation bug

### Phase 1 Validation Summary:
- ✅ Task performance meets all targets
- ❌ Import/memory issues due to heavy dependencies
- ❌ Agent tests need API key mocking
- 46.9% test coverage (15/32 pass)

### Next Session Should
1. Fix import time by removing langchain_openai
2. Make LLM optional for testing
3. Start Phase 2 Block 2.1 (LiteCrew Orchestration)
4. Improve test coverage to >90%

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
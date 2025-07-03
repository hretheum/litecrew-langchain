# LiteCrew Project

This repository contains the LiteCrew project - a lightweight alternative to CrewAI built on LangChain.

## Current Status

After extensive benchmarking revealed that:
- CrewAI has 3.3s import time and 208MB memory overhead
- LangChain has 0.008s import time and 17MB memory overhead
- Our fork attempt failed (increased size instead of reducing)

We decided to build a new implementation on top of LangChain.

## Project Structure

```
litecrew/
├── litecrew-langchain/     # New implementation (active development)
│   ├── src/               # Source code
│   ├── tests/             # Test suite
│   ├── benchmarks/        # Performance tests
│   └── docs/              # Documentation and plans
├── benchmark-archive/      # Historical benchmark data
├── masterplan/            # Original planning documents
└── scripts/               # Utility scripts
```

## Active Development

All active development is happening in the `litecrew-langchain/` directory.

See [litecrew-langchain/README.md](./litecrew-langchain/README.md) for details.

## Documentation

- [Implementation Plan](./litecrew-langchain/docs/IMPLEMENTATION_PLAN_EXTENDED.md)
- [Feature Comparison](./litecrew-langchain/docs/CREWAI_FEATURES_COMPARISON.md)
- [Benchmark Results](./litecrew-langchain/docs/benchmark-results/)

## Repository

- GitLab: https://gitlab.com/eof3/litecrewai
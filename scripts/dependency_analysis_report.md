# CrewAI Dependency Analysis Report
Generated on: 2025-06-29 13:15:20

## Executive Summary
- Total dependencies analyzed: 21
- Total estimated size: 263.04 MB
- Core dependencies: 7
- Optional dependencies: 4
- Replaceable dependencies: 4
- Removable dependencies: 6

## CORE Dependencies
These dependencies are absolutely required for basic CrewAI functionality.

### pydantic >=2.4.2
- **Size**: 2.5 MB
- **Reason**: Data validation and settings management - CORE framework requirement

### click >=8.1.7
- **Size**: 0.6 MB
- **Reason**: CLI framework - required for crewai command

### python-dotenv >=1.0.0
- **Size**: 0.02 MB
- **Reason**: Environment variable management - security requirement

### jsonref >=1.1.0
- **Size**: 0.02 MB
- **Reason**: JSON reference resolution - required for configuration

### tomli >=2.0.2
- **Size**: 0.02 MB
- **Reason**: TOML parsing for Python < 3.11

### blinker >=1.9.0
- **Size**: 0.02 MB
- **Reason**: Event dispatching system - core functionality

### tomli-w >=1.1.0
- **Size**: 0.01 MB
- **Reason**: TOML writing capability

## OPTIONAL Dependencies
These dependencies enable specific features but aren't required for core functionality.

### tokenizers >=0.20.3
- **Size**: 15.0 MB
- **Reason**: Text tokenization - optional for embeddings

### openai >=1.13.3
- **Size**: 0.8 MB
- **Reason**: OpenAI API integration - can use other LLMs

### instructor >=1.3.3
- **Size**: 0.5 MB
- **Reason**: Structured output from LLMs - optional feature

### regex >=2024.9.11
- **Size**: 0.4 MB
- **Reason**: Advanced regex - could use standard re module

## REPLACEABLE Dependencies
These dependencies can be replaced with lighter alternatives.

### onnxruntime ==1.22.0
- **Size**: 150.0 MB
- **Reason**: Large ML runtime
- **Alternatives**: onnxruntime-mobile, custom implementation
- **Potential size reduction**: ~70%

### chromadb >=0.5.23
- **Size**: 45.0 MB
- **Reason**: Heavy vector database
- **Alternatives**: faiss-cpu, annoy, simple in-memory solution
- **Potential size reduction**: ~90%

### litellm ==1.72.6
- **Size**: 15.0 MB
- **Reason**: Large LLM abstraction
- **Alternatives**: direct API calls, minimal wrapper
- **Potential size reduction**: ~80%

### pdfplumber >=0.11.4
- **Size**: 5.0 MB
- **Reason**: Heavy PDF processing
- **Alternatives**: pypdf, pdftotext
- **Potential size reduction**: ~50%

## REMOVABLE Dependencies
These dependencies can be removed without affecting core functionality.

### uv >=0.4.25
- **Size**: 25.0 MB
- **Reason**: Package installer - only needed for development

### openpyxl >=3.1.5
- **Size**: 2.5 MB
- **Reason**: Excel processing - specific use case

### pyvis >=0.3.2
- **Size**: 0.5 MB
- **Reason**: Network visualization - rarely used feature

### json-repair >=0.25.2
- **Size**: 0.1 MB
- **Reason**: JSON repair - edge case handling

### json5 >=0.10.0
- **Size**: 0.03 MB
- **Reason**: JSON5 format support - rarely needed

### appdirs >=1.4.4
- **Size**: 0.02 MB
- **Reason**: App directory paths - can be hardcoded

## Optimization Recommendations

### Quick Wins (High Impact, Low Effort)
1. **Remove unnecessary dependencies**: Save ~28.15 MB
   - Remove: openpyxl, pyvis, appdirs, json-repair, uv, json5

2. **Make heavy dependencies optional**:
   - Move tokenizers (15.0 MB) to optional group

### Medium-term Optimizations
1. **Replace heavy dependencies with lighter alternatives**:
   - Replace litellm (15.0 MB) → ~80% reduction
   - Replace pdfplumber (5.0 MB) → ~50% reduction
   - Replace chromadb (45.0 MB) → ~90% reduction
   - Replace onnxruntime (150.0 MB) → ~70% reduction

2. **Implement lazy loading for optional features**
3. **Create minimal installation profiles** (core, standard, full)

## Proposed Dependency Groups

### crewai-core (Minimal)
```toml
[project]
dependencies = [
    "pydantic>=2.4.2",
    "python-dotenv>=1.0.0",
    "click>=8.1.7",
    "jsonref>=1.1.0",
    "tomli-w>=1.1.0",
    "tomli>=2.0.2",
    "blinker>=1.9.0",
]
```

### Optional Feature Groups
```toml
[project.optional-dependencies]
llm = [
    "openai>=1.13.3",
    "instructor>=1.3.3",
]
embeddings = [
    "tokenizers>=0.20.3",
    "onnxruntime==1.22.0",
    "chromadb>=0.5.23",
]
documents = [
    "pdfplumber>=0.11.4",
]
```
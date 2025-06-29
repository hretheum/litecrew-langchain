# CrewAI Dependency Optimization Guide

## Executive Summary

The CrewAI fork currently has a total dependency footprint of **263 MB**. Through strategic optimization, this can be reduced to approximately **75 MB** (71.5% reduction) while maintaining core functionality.

## Quick Wins (Immediate Implementation)

### 1. Remove Unnecessary Dependencies (Save 28.1 MB)

Remove the following dependencies from `pyproject.toml`:

```toml
# Remove these from [project] dependencies:
- "appdirs>=1.4.4"      # 20 KB - App paths can be hardcoded
- "json-repair>=0.25.2" # 100 KB - Edge case handling, rarely needed
- "json5>=0.10.0"       # 30 KB - JSON5 format rarely used
- "uv>=0.4.25"         # 25 MB - Development tool, not needed at runtime
- "pyvis>=0.3.2"       # 500 KB - Visualization rarely used
- "openpyxl>=3.1.5"    # 2.5 MB - Excel support, make optional
```

### 2. Move Heavy Dependencies to Optional Groups

Update `pyproject.toml` to reorganize dependencies:

```toml
[project]
dependencies = [
    # Core only
    "pydantic>=2.4.2",
    "python-dotenv>=1.0.0",
    "click>=8.1.7",
    "jsonref>=1.1.0",
    "tomli-w>=1.1.0",
    "tomli>=2.0.2",
    "blinker>=1.9.0",
]

[project.optional-dependencies]
llm = [
    "openai>=1.13.3",
    "litellm==1.72.6",
    "instructor>=1.3.3",
]
embeddings = [
    "chromadb>=0.5.23",
    "tokenizers>=0.20.3",
    "onnxruntime==1.22.0",
]
documents = [
    "pdfplumber>=0.11.4",
    "openpyxl>=3.1.5",
]
advanced = [
    "regex>=2024.9.11",  # Can use stdlib re for most cases
    "pyvis>=0.3.2",
]
```

## Medium-term Optimizations

### 3. Replace Heavy Dependencies (Save 160 MB)

#### Replace onnxruntime (Save 105 MB)
- **Current**: onnxruntime (150 MB)
- **Alternative**: onnxruntime-mobile (45 MB) or custom embedding solution
- **Implementation**: Create abstraction layer that can use different backends

#### Replace chromadb (Save 40.5 MB)
- **Current**: chromadb (45 MB)
- **Alternatives**:
  - faiss-cpu (5 MB) - Facebook's vector similarity library
  - annoy (1 MB) - Spotify's approximate nearest neighbors
  - Simple in-memory solution for small datasets
- **Implementation**: Create vector store interface with pluggable backends

#### Replace litellm (Save 12 MB)
- **Current**: litellm (15 MB)
- **Alternative**: Direct API calls or minimal wrapper (3 MB)
- **Implementation**: Create thin abstraction for LLM providers

#### Replace pdfplumber (Save 2.5 MB)
- **Current**: pdfplumber (5 MB)
- **Alternatives**:
  - pypdf (2 MB) - Lighter PDF reader
  - pdftotext (500 KB) - Simple text extraction
- **Implementation**: Use simpler library for basic PDF text extraction

## Implementation Strategy

### Phase 1: Immediate (1 day)
1. Remove unnecessary dependencies
2. Test core functionality
3. Update documentation

### Phase 2: Reorganization (1 week)
1. Move dependencies to optional groups
2. Update installation instructions
3. Create installation profiles:
   ```bash
   pip install crewai              # Core only (3.2 MB)
   pip install crewai[llm]         # With LLM support (19 MB)
   pip install crewai[embeddings]  # With embeddings (213 MB)
   pip install crewai[all]         # Everything
   ```

### Phase 3: Replacements (2-4 weeks)
1. Create abstraction interfaces for:
   - Vector stores
   - LLM providers
   - Document processors
2. Implement lighter alternatives
3. Maintain backward compatibility with configuration flags

## Installation Profiles

### Minimal (3.2 MB)
```bash
pip install crewai-core
```
- Basic agent orchestration
- Configuration management
- CLI tools

### Standard (20 MB)
```bash
pip install crewai[llm]
```
- All minimal features
- OpenAI/LLM integration
- Structured outputs

### Full (75 MB with optimizations)
```bash
pip install crewai[llm,embeddings-light,documents]
```
- All features with optimized dependencies
- Vector search with faiss-cpu
- Document processing with pypdf

### Legacy (263 MB)
```bash
pip install crewai[all-legacy]
```
- All original dependencies
- For backward compatibility

## Testing Strategy

1. **Unit Tests**: Ensure core functionality works with minimal deps
2. **Integration Tests**: Test each optional feature group
3. **Performance Tests**: Verify no regression in speed
4. **Compatibility Tests**: Ensure existing code continues to work

## Migration Guide for Users

### For Existing Users
```python
# Add this to handle missing optional dependencies gracefully
try:
    import chromadb
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    
# Use feature flags
if EMBEDDINGS_AVAILABLE:
    # Use vector search features
else:
    # Fallback to simple search
```

### For New Users
```bash
# Start minimal
pip install crewai

# Add features as needed
pip install crewai[llm]  # When you need LLM features
```

## Monitoring and Metrics

Track these metrics after optimization:
- Installation time
- Docker image size
- Import time
- Memory usage at startup
- User adoption of different profiles

## Conclusion

By implementing these optimizations, CrewAI can:
- Reduce default installation size by 71.5%
- Improve installation speed
- Lower barrier to entry for new users
- Maintain full functionality through optional dependencies
- Better support containerized deployments

The modular approach allows users to choose only what they need, making CrewAI more accessible and efficient.
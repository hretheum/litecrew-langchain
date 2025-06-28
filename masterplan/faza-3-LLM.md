## 📦 FAZA 3: INTEGRACJA LLM I ROUTING

[← Powrót do README](./README.md) | [← Faza 2: Core Engine](./faza-2-core-engine.md) | [Następna faza: Storage →](./faza-4-storage.md)

### Blok 3.1: LLM Integration Layer

**Czas**: 10h
**Cel**: Uniwersalna warstwa integracji LLM

#### Zadania Atomowe:

##### Task 3.1.1: Design LLM Abstraction Layer (3h)

**Cel**: Unified interface dla różnych LLM providers

**Prompt dla AI Agent**:

```
Zaprojektuj abstraction layer dla LLM w LiteCrewAI.

Wymagania:
1. Base LLM interface:
   - generate(prompt, **kwargs)
   - stream_generate(prompt, **kwargs)
   - embed(text)
   - count_tokens(text)
   - get_model_info()

2. Provider implementations:
   - OllamaProvider (local)
   - OpenAIProvider
   - GroqProvider
   - HuggingFaceProvider
   - CustomProvider (dla własnych modeli)

3. Configuration:
   - Model selection
   - Temperature, top_p, etc.
   - Timeout handling
   - Retry logic
   - Context window management

4. Response handling:
   - Unified response format
   - Error normalization
   - Token usage tracking
   - Latency measurement

5. Advanced features:
   - Response caching
   - Prompt templates
   - Multi-turn conversations
   - Function calling support

Przykład użycia:
[→ Zobacz plik: example_llm_provider_usage.py](./src/faza-3/example_llm_provider_usage.py)

Design powinien być extensible i testable.

```
**Metryki Sukcesu**:
- ✅ Unified interface works
- ✅ All providers implement same API
- ✅ <100ms overhead
- ✅ Proper error handling

**Walidacja**:
[→ Zobacz plik: validate_llm_abstraction.py](./src/faza-3/validate_llm_abstraction.py)

##### Task 3.1.2: Implement Ollama Integration (4h)

**Cel**: Pełna integracja z lokalnym Ollama

**Prompt dla AI Agent**:

```
Zaimplementuj kompletną integrację Ollama dla LiteCrewAI.

Funkcjonalności:
1. Model management:
   - List available models
   - Pull new models
   - Delete unused models
   - Model info/stats
   - Auto-pull if missing

2. Generation features:
   - Text generation
   - Streaming support
   - Embeddings
   - Multi-modal (images)
   - JSON mode

3. Performance optimization:
   - Connection pooling
   - Request batching
   - Keep-alive connections
   - Parallel inference
   - GPU utilization tracking

4. Advanced features:
   - Custom model loading
   - Fine-tuned models
   - Model switching
   - Context caching
   - Conversation management

5. Monitoring:
   - Request metrics
   - Token usage
   - GPU/CPU usage
   - Model performance
   - Error rates

6. Configuration:
   - Server URL (default localhost)
   - Timeout settings
   - Retry configuration
   - Model preferences
   - Resource limits

Przykład:
[→ Zobacz plik: example_ollama_provider.py](./src/faza-3/example_ollama_provider.py)

Include health checks and graceful degradation.

```
**Metryki Sukcesu**:
- ✅ All Ollama features work
- ✅ <50ms latency overhead
- ✅ Streaming smooth
- ✅ Auto-recovery works

**Walidacja**:
[→ Zobacz plik: validate_ollama_integration.py](./src/faza-3/validate_ollama_integration.py)

##### Task 3.1.3: Add External LLM Providers (3h)

**Cel**: Wsparcie dla OpenAI, Groq i innych

**Prompt dla AI Agent**:

```
Dodaj wsparcie dla zewnętrznych LLM providers w LiteCrewAI.

Providers do implementacji:
1. OpenAI:
   - GPT-4, GPT-3.5
   - Embeddings (ada-002)
   - Function calling
   - Vision support
   - Assistants API (optional)

2. Groq:
   - Mixtral, Llama2
   - Ultra-fast inference
   - Streaming
   - Token counting

3. Google (Gemini):
   - Gemini Pro
   - Multi-modal
   - Safety settings
   - Grounding

4. Anthropic (Claude):
   - Claude 3
   - Long context
   - Constitutional AI
   - Vision

5. Cohere:
   - Command model
   - Embeddings
   - Reranking
   - RAG support

Wspólne features:
- API key management (from env vars)
- Rate limiting per provider
- Cost tracking
- Fallback chains
- Request logging
- Error standardization

Przykład konfiguracji:
[→ Zobacz plik: config_llm_providers.yaml](./src/faza-3/config_llm_providers.yaml)

Implementacja powinna być modułowa - każdy provider jako osobny moduł.

```
**Metryki Sukcesu**:
- ✅ All providers work
- ✅ Seamless fallback
- ✅ Cost tracking accurate
- ✅ <100ms switching time

**Walidacja**:
[→ Zobacz plik: validate_external_providers.py](./src/faza-3/validate_external_providers.py)

### Blok 3.2: Intelligent Routing System

**Czas**: 8h
**Cel**: Inteligentny routing między LLM

#### Zadania Atomowe:

##### Task 3.2.1: Build Cost-Aware Router (3h)

**Cel**: Router minimalizujący koszty

**Prompt dla AI Agent**:

```
Zbuduj inteligentny router dla LiteCrewAI który minimalizuje koszty.

Komponenty:
1. Cost calculation:
   - Per-token costs dla każdego modelu
   - Ukryte koszty (API calls, embeddings)
   - Walutowe przeliczniki
   - Historical cost tracking

2. Decision factors:
   - Task complexity analysis
   - Required capabilities (vision, functions, etc)
   - Context length needs
   - Quality requirements
   - Latency requirements
   - Budget remaining

3. Routing strategies:
   - Greedy (zawsze najtańszy)
   - Quality-first (budget allowing)
   - Balanced (cost/quality ratio)
   - Time-based (tańsze modele w nocy)
   - Usage-based (premium dla ważnych zadań)

4. Budget management:
   - Daily/monthly limits
   - Per-user budgets
   - Per-task budgets
   - Alerts and warnings
   - Automatic downgrade

5. Optimization features:
   - Prompt compression
   - Response caching
   - Batch processing
   - Model-specific prompt optimization

Przykład:
[→ Zobacz plik: example_cost_aware_router.py](./src/faza-3/example_cost_aware_router.py)

```
**Metryki Sukcesu**:
- ✅ Cost estimation ±10%
- ✅ Budget never exceeded
- ✅ Intelligent routing works
- ✅ <50ms routing decision

**Walidacja**:
[→ Zobacz plik: validate_cost_router.py](./src/faza-3/validate_cost_router.py)

##### Task 3.2.2: Implement Quality-Based Selection (3h)

**Cel**: Wybór modelu based on quality needs

**Prompt dla AI Agent**:

```
Zaimplementuj system wyboru modelu bazujący na wymaganiach jakościowych.

Komponenty:
1. Quality metrics:
   - Accuracy score (0-1)
   - Creativity score (0-1)
   - Reasoning ability (0-1)
   - Language quality (0-1)
   - Instruction following (0-1)
   - Domain expertise (per domain)

2. Model capabilities:
   - Capability matrix per model
   - Benchmark results
   - User feedback integration
   - A/B test results
   - Dynamic scoring updates

3. Task requirements:
   - Required capabilities
   - Minimum quality threshold
   - Domain specificity
   - Output format needs
   - Language requirements

4. Matching algorithm:
   - Weighted scoring
   - Constraint satisfaction
   - Pareto optimization
   - Fallback strategies

5. Quality monitoring:
   - Output validation
   - User satisfaction tracking
   - Automatic reranking
   - Model performance decay detection

Przykład:
[→ Zobacz plik: example_quality_selector.py](./src/faza-3/example_quality_selector.py)

System powinien uczyć się z każdego użycia.

```
**Metryki Sukcesu**:
- ✅ Quality prediction ±15%
- ✅ Right model 90%+ time
- ✅ Learning improves selection
- ✅ Fast selection <100ms

**Walidacja**:
[→ Zobacz plik: validate_quality_selector.py](./src/faza-3/validate_quality_selector.py)

##### Task 3.2.3: Create Fallback Mechanisms (2h)

**Cel**: Niezawodny system fallback

**Prompt dla AI Agent**:

```
Stwórz comprehensive fallback system dla LiteCrewAI.

Komponenty:
1. Fallback triggers:
   - Timeout (configurable)
   - Error responses
   - Rate limits hit
   - Quality below threshold
   - Cost exceeded
   - Model unavailable

2. Fallback strategies:
   - Simple retry with backoff
   - Switch to alternate model
   - Degrade gracefully
   - Queue for later
   - Return cached response
   - Use local model

3. Fallback chains:
   - Primary → Secondary → Emergency
   - Cost-ordered fallbacks
   - Quality-ordered fallbacks
   - Latency-ordered fallbacks
   - Geographic fallbacks

4. State preservation:
   - Maintain context
   - Transfer conversation
   - Adjust parameters
   - Log transition reason

5. Recovery mechanisms:
   - Auto-recovery detection
   - Gradual restoration
   - Health monitoring
   - Circuit breaker pattern

Przykład:
[→ Zobacz plik: example_fallback_chain.py](./src/faza-3/example_fallback_chain.py)

System powinien być transparent i debuggable.

```
**Metryki Sukcesu**:
- ✅ 99.9% success rate
- ✅ Smooth transitions
- ✅ Context preserved
- ✅ Fast recovery <5s

**Walidacja**:
[→ Zobacz plik: validate_fallback_system.py](./src/faza-3/validate_fallback_system.py)

---

## 

---

[← Powrót do README](./README.md) | [← Faza 2: Core Engine](./faza-2-core-engine.md) | [Następna faza: Storage →](./faza-4-storage.md)

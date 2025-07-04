# Plan Naprawy Testów - LiteCrew LangChain

## 🎯 Cel: Osiągnięcie 70%+ coverage i <15 failed tests

### Status startowy:
- 54 failed, 159 passed, 2 skipped
- Coverage: ~28%
- Główne problemy: Mock LLM, API execution, task storage

## 🚀 Plan wykonania - Krok po kroku

### **ETAP 1: LangChain Mock LLM (Priorytet 1)** ⏱️ 30-45 min
```
Problem: SimpleFakeLLM nie jest kompatybilny z LangChain Runnable
Plan:
1. Zbadaj LangChain FakeChatModel/FakeStreamingLLM  
2. Stwórz prawdziwy BaseChatModel subclass dla testów
3. Dodaj obsługę streaming, bind(), with_structured_output()
4. Przetestuj z create_react_agent()
Pliki: src/litecrew/agent.py
Testy: test_api.py execution tests, test_basic.py
```

### **ETAP 2: API Execution Engine (Priorytet 2)** ⏱️ 45-60 min  
```
Problem: /execute endpoint failuje bo crew.kickoff_async() nie działa
Plan:
1. Zaimplementuj kickoff_async() w LiteCrew
2. Napraw error handling w API
3. Dodaj proper task result storage  
4. Fix execution status tracking
Pliki: src/litecrew/crew.py, src/litecrew/api/routers/crews.py
Testy: test_api.py TestTaskSubmissionAPI
```

### **ETAP 3: Task Storage Integration (Priorytet 3)** ⏱️ 30 min
```
Problem: Task endpoints 404, brak integracji z storage
Plan:
1. Napraw task creation w crews endpoint
2. Implementuj task tracking podczas execution
3. Fix get_task endpoint w tasks.py
4. Dodaj task status updates
Pliki: src/litecrew/api/routers/tasks.py, src/litecrew/api/storage.py
Testy: test_api.py TestTaskSubmissionAPI::test_get_task_status
```

### **ETAP 4: Rate Limiting & Agent Methods (Priorytet 4)** ⏱️ 20-30 min
```
Problem: _call_llm attribute missing, rate limiting tests fail
Plan:
1. Dodaj _call_llm method do Agent class
2. Implementuj proper rate limiting hooks
3. Fix token counting integration
4. Update method signatures
Pliki: src/litecrew/agent.py, tests/test_rate_limiting.py
Testy: test_rate_limiting.py
```

### **ETAP 5: State Management (Priorytet 5)** ⏱️ 30 min
```
Problem: Snapshot integrity check failures
Plan:
1. Fix state serialization/deserialization
2. Implementuj proper checksums
3. Fix incremental updates logic
4. Add error recovery
Pliki: src/litecrew/state/
Testy: test_state_management.py
```

### **ETAP 6: Performance Optimizations (Priorytet 6)** ⏱️ 30-45 min
```
Problem: Event dispatch 5.5ms > 2ms, storage 78ms > 50ms
Plan:
1. Profile event system bottlenecks
2. Optimize batch operations in storage
3. Add async optimizations
4. Cache frequently accessed data
Pliki: src/litecrew/events/, src/litecrew/storage/
Testy: test_event_system.py, test_storage.py
```

### **ETAP 7: UI/CLI Polish (Priorytet 7)** ⏱️ 15-20 min
```
Problem: Missing fields, error messages
Plan:
1. Add memory_mb to dashboard metrics
2. Fix CLI error message formatting  
3. Update health endpoint with proper metrics
4. Polish API responses
Pliki: src/litecrew/api/, src/litecrew/cli/
Testy: test_dashboard.py, test_cli.py
```

## 📊 Oczekiwane rezultaty:
- **Po Etapie 1-3**: Coverage 50-60%, failed tests 30-40
- **Po Etapie 4-5**: Coverage 65-75%, failed tests 15-25  
- **Po Etapie 6-7**: Coverage 70%+, failed tests <15

## 🎯 Metryki sukcesu:
- [x] LiteAgent constructor fixed
- [x] WebSocket tests fixed  
- [x] Cache tests fixed
- [ ] Mock LLM compatible with LangChain
- [ ] API execution working
- [ ] Task storage integration
- [ ] Rate limiting functional
- [ ] State integrity checks pass
- [ ] Performance under limits
- [ ] All UI metrics present

---
Created: 2025-01-04
Last Updated: 2025-01-04
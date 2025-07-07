# 🎯 LiteCrew Multi-Agent Process Types - Roadmap Enhancement

## Executive Summary

Rozszerzenie LiteCrew o różne typy procesów i agentów, które użytkownik może wybierać przez API. Zamiast tylko `process="sequential"` czy `process="hierarchical"`, dajemy pełną kontrolę nad typem interakcji między agentami.

## 🔄 Proponowane Process Types

### 1. **conversational** - Agenci prowadzą naturalną dyskusję
```python
crew = LiteCrew(
    agents=[architect, strategist, critic],
    tasks=[analyze_task],
    process="conversational",
    process_config={
        "min_turns": 3,        # Minimum wypowiedzi per agent
        "style": "debate",     # debate/brainstorm/socratic
        "moderator": True      # Czy dodać moderatora
    }
)
```

### 2. **debate** - Strukturalna debata z tezami i kontrargumentami
```python
crew = LiteCrew(
    process="debate",
    process_config={
        "rounds": 3,
        "time_per_round": 300,  # sekundy
        "voting": True,
        "devil_advocate": True   # Jeden agent zawsze kontruje
    }
)
```

### 3. **brainstorm** - Kreatywna burza mózgów
```python
crew = LiteCrew(
    process="brainstorm", 
    process_config={
        "phases": ["divergent", "convergent"],
        "ideas_per_agent": 5,
        "build_on_others": True
    }
)
```

### 4. **consensus** - Dochodzenie do wspólnego stanowiska
```python
crew = LiteCrew(
    process="consensus",
    process_config={
        "voting_mechanism": "weighted",
        "min_agreement": 0.7,
        "max_rounds": 5
    }
)
```

### 5. **panel** - Panel ekspertów z moderatorem
```python
crew = LiteCrew(
    process="panel",
    process_config={
        "moderator_agent": moderator,
        "question_rounds": 3,
        "audience_questions": True
    }
)
```

### 6. **socratic** - Metoda sokratejska (pytania prowadzące)
```python
crew = LiteCrew(
    process="socratic",
    process_config={
        "teacher_agent": socrates,
        "depth_levels": 5,
        "challenge_assumptions": True
    }
)
```

### 7. **stream_of_consciousness** - Strumień świadomości
```python
crew = LiteCrew(
    process="stream_of_consciousness",
    process_config={
        "min_words_per_thought": 500,
        "show_internal_debate": True,
        "include_doubts": True
    }
)
```

## 🤖 Proponowane Agent Types

### 1. **ConversationalAgent** - Agent z pamięcią konwersacji
```python
agent = LiteAgent(
    type="conversational",
    memory_type="full",  # full/summary/buffer
    conversation_style="friendly"  # friendly/formal/socratic
)
```

### 2. **DebateAgent** - Specjalista od argumentacji
```python
agent = LiteAgent(
    type="debate",
    stance="pro",  # pro/contra/neutral
    argumentation_style="logical"  # logical/emotional/empirical
)
```

### 3. **CriticAgent** - Zawsze szuka dziur
```python
agent = LiteAgent(
    type="critic",
    criticism_level="harsh",  # gentle/moderate/harsh
    focus_areas=["logic", "evidence", "assumptions"]
)
```

### 4. **ModeratorAgent** - Kieruje dyskusją
```python
agent = LiteAgent(
    type="moderator",
    style="active",  # passive/active/strict
    enforce_rules=True
)
```

### 5. **ThinkingAgent** - Myśli na głos
```python
agent = LiteAgent(
    type="thinking",
    verbosity="extreme",  # minimal/moderate/extreme
    show_process=True,
    include_memories=True
)
```

## 📋 Modyfikacje Roadmapy

### FAZA 6.5: Multi-Process Engine (Nowy blok - 3 dni) 🆕

**Kiedy**: Zaraz po ukończonej Fazie 6, przed Fazą 7

#### Zadania atomowe:
- [ ] Refactor LiteCrew aby przyjmował różne process executors
- [ ] Implementuj ConversationalProcess class
- [ ] Implementuj DebateProcess class  
- [ ] Implementuj BrainstormProcess class
- [ ] Implementuj ConsensusProcess class
- [ ] Dodaj process_config validation
- [ ] Napisz testy dla każdego process type

#### Metryki sukcesu:
- Switching między procesami: <10ms
- Overhead per process type: <5%
- Wszystkie procesy działają z tymi samymi agentami

### FAZA 6.6: Agent Type System (Nowy blok - 2 dni) 🆕

**Kiedy**: Po Fazie 6.5, jako ostatni element przed Fazą 7

#### Zadania atomowe:
- [ ] Stwórz BaseAgent z type system
- [ ] Implementuj ConversationalAgent z LangChain
- [ ] Implementuj DebateAgent z stance management
- [ ] Implementuj CriticAgent z criticism strategies
- [ ] Implementuj ModeratorAgent z flow control
- [ ] Dodaj agent type w API
- [ ] Napisz testy type-specific behaviors

#### Metryki sukcesu:
- Agent creation z type: <20ms
- Type-specific behaviors: działają
- Backward compatibility: 100%

### Rozszerzenie istniejącego REST API ✅

Skoro API już istnieje (Faza 5 completed), dodajemy nowe endpointy:
- [ ] GET /api/v1/process-types - lista dostępnych procesów
- [ ] GET /api/v1/agent-types - lista typów agentów
- [ ] PUT /api/v1/crews/{id}/process - zmiana procesu w runtime
- [ ] Websocket events dla conversational processes

Przykład API:
```python
POST /api/v1/crews
{
    "name": "Expert Panel",
    "process": "panel",
    "process_config": {
        "moderator_agent": "agent_id_123",
        "question_rounds": 3
    },
    "agents": [
        {
            "role": "AI Architect",
            "type": "thinking",
            "type_config": {
                "verbosity": "extreme"
            }
        }
    ]
}
```

### Modyfikacja FAZY 7.3: Entity & Contextual Memory

Dodać:
- [ ] Conversation flow memory (kto z kim rozmawiał)
- [ ] Debate points tracking
- [ ] Consensus history storage

### Modyfikacja FAZY 8: Advanced Orchestration

Zmienić fokus na:
- [ ] Dynamic process switching (np. z debate na consensus)
- [ ] Multi-phase processes (brainstorm → debate → consensus)
- [ ] Parallel sub-conversations

## 🏗️ Architektura

```python
# litecrew/processes/base.py
class BaseProcess(ABC):
    @abstractmethod
    async def execute(self, agents: List[Agent], tasks: List[Task]) -> ProcessResult:
        pass

# litecrew/processes/conversational.py  
class ConversationalProcess(BaseProcess):
    def __init__(self, min_turns: int, style: str):
        self.min_turns = min_turns
        self.style = style
    
    async def execute(self, agents, tasks):
        # Implementacja naturalnej konwersacji
        conversation = []
        for turn in range(self.min_turns):
            for agent in agents:
                response = await agent.respond(conversation)
                conversation.append(response)
        return ProcessResult(conversation)

# litecrew/crew.py
class LiteCrew:
    def __init__(self, process="sequential", process_config=None):
        self.process_executor = ProcessFactory.create(process, process_config)
```

## 📊 Priorytety Implementacji

1. **CRITICAL** (Faza 6.5):
   - conversational
   - debate
   - panel

2. **HIGH** (Faza 6.6):
   - ConversationalAgent
   - ThinkingAgent
   - ModeratorAgent

3. **MEDIUM** (Po Fazie 6.6):
   - brainstorm
   - consensus
   - socratic

4. **LOW** (Opcjonalne/Faza 8+):
   - stream_of_consciousness
   - custom processes via plugins

## 🎯 Korzyści

1. **Elastyczność** - Użytkownik wybiera jak agenci współpracują
2. **Naturalność** - Konwersacje zamiast sztywnych task chains
3. **Debugowanie** - ThinkingAgent pokazuje proces myślowy
4. **Innowacja** - Unikalne features vs CrewAI
5. **Monetyzacja** - Premium process types w paid tiers

## ⚡ Quick Wins

Zacznij od prostego ConversationalProcess który:
1. Pozwala agentom odpowiadać na siebie nawzajem
2. Nie wymaga narzędzi (tools)
3. Generuje naturalny dialog
4. Łatwy do zrozumienia dla użytkowników

## 🚀 Przykład Użycia

```python
# Debata o architekturze
critics = [
    LiteAgent(role="Security Expert", type="critic"),
    LiteAgent(role="Performance Guru", type="critic"),
    LiteAgent(role="UX Designer", type="debate", stance="user-first")
]

architect = LiteAgent(role="Solution Architect", type="thinking")

crew = LiteCrew(
    agents=[architect] + critics,
    tasks=[LiteTask("Design a new authentication system")],
    process="debate",
    process_config={
        "rounds": 3,
        "architect_goes_first": True,
        "voting": True
    }
)

result = crew.kickoff()
# Generuje pełną debatę z argumentami i kontrargumentami
```

## 🚦 Status Projektu & Next Steps

### Obecny stan (Fazy 1-6 ✅ COMPLETED):
- ✅ Core engine z sequential/hierarchical
- ✅ Multi-LLM support 
- ✅ Storage & caching
- ✅ REST API & Dashboard
- ✅ Production features (rate limiting, events, structured outputs)
- ✅ 72.7% test coverage
- ✅ Deployed na api.litecrew.app

### Proponowana kolejność implementacji:

1. **FAZA 6.5** (3 dni) - Multi-Process Engine
   - Priorytet: ConversationalProcess (najprostszy, największy impact)
   - Potem: DebateProcess, PanelProcess
   - Opcjonalnie: BrainstormProcess

2. **FAZA 6.6** (2 dni) - Agent Type System  
   - Priorytet: ConversationalAgent i ThinkingAgent
   - Potem: ModeratorAgent, CriticAgent

3. **Później** - Możemy pominąć Fazy 7-9 i skupić się na:
   - Więcej process types na życzenie użytkowników
   - Integracja z istniejącym API
   - Marketing nowych features

### 🎯 Quick Win Implementation Plan

**Tydzień 1**: Minimalny ConversationalProcess
```python
# Prosty proof of concept
crew = LiteCrew(
    agents=[agent1, agent2, agent3],
    tasks=[discussion_task],
    process="conversational"  # Nowy!
)
# Generuje naturalny dialog zamiast sztywnych odpowiedzi
```

**Tydzień 2**: Rozbudowa i testy
- Dodanie process_config
- Integracja z API
- Dashboard pokazujący konwersację

---

**Rekomendacja**: Zacznij od Fazy 6.5 z fokusem na ConversationalProcess. To da natychmiastową wartość i wyróżni LiteCrew na tle CrewAI. Fazy 7-9 (Advanced Memory, Orchestration) można odłożyć - użytkownicy bardziej potrzebują naturalnych konwersacji niż skomplikowanego RAG.
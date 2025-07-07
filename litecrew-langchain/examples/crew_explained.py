"""
🎯 JAK DZIAŁA CREW - PRZYKŁAD
"""

# CREW = ZESPÓŁ SPECJALISTÓW

# Przykład 1: Zespół do tworzenia contentu
content_crew = {
    "name": "Zespół Contentowy",
    "agents": [
        {
            "role": "SEO Specialist",
            "goal": "Znajdź najlepsze słowa kluczowe",
            "backstory": "Ekspert SEO z 5-letnim doświadczeniem"
        },
        {
            "role": "Researcher", 
            "goal": "Zbadaj temat dogłębnie",
            "backstory": "Analityk z dostępem do najnowszych źródeł"
        },
        {
            "role": "Copywriter",
            "goal": "Napisz angażujący artykuł",
            "backstory": "Kreatywny pisarz z portfolio 500+ artykułów"
        },
        {
            "role": "Editor",
            "goal": "Dopracuj i popraw tekst",
            "backstory": "Redaktor z okiem sokoła"
        }
    ],
    "tasks": [
        {
            "description": "Znajdź 10 najlepszych słów kluczowych dla tematu: {topic}",
            "agent_role": "SEO Specialist",  # <-- TO ZADANIE WYKONA SEO SPECIALIST
            "expected_output": "Lista słów kluczowych z wolumenem wyszukiwań"
        },
        {
            "description": "Zbadaj temat wykorzystując słowa kluczowe",
            "agent_role": "Researcher",  # <-- TO ZADANIE WYKONA RESEARCHER
            "expected_output": "Kompletny research z 10+ źródłami",
            "context": [0]  # <-- Użyje wyników z zadania 0 (słowa kluczowe)
        },
        {
            "description": "Napisz artykuł 1500 słów na podstawie research",
            "agent_role": "Copywriter",  # <-- TO ZADANIE WYKONA COPYWRITER
            "expected_output": "Gotowy artykuł z SEO",
            "context": [0, 1]  # <-- Użyje słów kluczowych I research
        },
        {
            "description": "Zredaguj artykuł, popraw błędy, dodaj CTA",
            "agent_role": "Editor",  # <-- TO ZADANIE WYKONA EDITOR
            "expected_output": "Finalny artykuł gotowy do publikacji",
            "context": [2]  # <-- Użyje artykułu od Copywritera
        }
    ],
    "process": "sequential"  # Zadania wykonywane po kolei
}

# Przykład 2: Zespół programistyczny
dev_crew = {
    "name": "Zespół Developerski",
    "agents": [
        {
            "role": "Architect",
            "goal": "Zaprojektuj architekturę rozwiązania",
            "backstory": "Senior architect z 15+ lat doświadczenia"
        },
        {
            "role": "Backend Developer",
            "goal": "Zaimplementuj logikę biznesową",
            "backstory": "Ekspert Python/Node.js"
        },
        {
            "role": "Frontend Developer", 
            "goal": "Stwórz interfejs użytkownika",
            "backstory": "Specialist React/Vue"
        },
        {
            "role": "QA Engineer",
            "goal": "Przetestuj i znajdź błędy",
            "backstory": "Tester z obsesją na punkcie jakości"
        },
        {
            "role": "DevOps",
            "goal": "Zdeployuj i monitoruj",
            "backstory": "Ekspert Docker/Kubernetes"
        }
    ],
    "tasks": [
        # Każdy agent dostaje swoje zadanie!
        # Współpracują przekazując sobie wyniki
    ]
}

# Przykład 3: Zespół analityczny
analysis_crew = {
    "name": "Zespół Analityczny",
    "agents": [
        {
            "role": "Data Collector",
            "goal": "Zbierz wszystkie dostępne dane"
        },
        {
            "role": "Data Analyst", 
            "goal": "Przeanalizuj dane i znajdź wzorce"
        },
        {
            "role": "Statistician",
            "goal": "Przeprowadź analizę statystyczną"
        },
        {
            "role": "Business Analyst",
            "goal": "Przełóż dane na wnioski biznesowe"
        },
        {
            "role": "Report Writer",
            "goal": "Stwórz czytelny raport dla zarządu"
        }
    ]
}

"""
JAK TO DZIAŁA:

1. CREW = Zespół specjalistów (jak w prawdziwej firmie)
2. Każdy AGENT = Ekspert w swojej dziedzinie
3. Każdy TASK = Konkretne zadanie przypisane do eksperta
4. CONTEXT = Agenci przekazują sobie wyniki pracy
5. PROCESS = Kolejność wykonywania (sequential/hierarchical)

PRZYKŁAD DZIAŁANIA:
- SEO Specialist znajduje słowa kluczowe
- Researcher używa tych słów do research
- Copywriter pisze na podstawie research
- Editor finalizuje artykuł

TO JAK WORKFLOW W FIRMIE! 🚀
"""
#!/usr/bin/env python3
"""
Przykład użycia LiteCrew w Pythonie
"""

import os
from litecrew import LiteAgent, LiteCrew, LiteTask

# Opcja 1: Lokalnie (jeśli masz zainstalowany pakiet)
def local_example():
    # Utwórz agentów
    researcher = LiteAgent(
        role="Researcher",
        goal="Znajdź dokładne informacje na temat",
        backstory="Ekspert w research i analizie danych",
        verbose=True
    )
    
    writer = LiteAgent(
        role="Writer",
        goal="Napisz angażującą treść",
        backstory="Profesjonalny copywriter",
        verbose=True
    )
    
    # Zdefiniuj zadania
    research_task = LiteTask(
        description="Zbadaj najlepsze praktyki w {topic}",
        agent=researcher,
        expected_output="Lista 10 najlepszych praktyk z opisami"
    )
    
    write_task = LiteTask(
        description="Napisz poradnik na podstawie research",
        agent=writer,
        context=[research_task],
        expected_output="Poradnik 1000+ słów"
    )
    
    # Stwórz i uruchom crew
    crew = LiteCrew(
        agents=[researcher, writer],
        tasks=[research_task, write_task],
        process="sequential",
        verbose=True
    )
    
    # Wykonaj z inputami
    result = crew.kickoff(inputs={
        "topic": "automatyzacja procesów biznesowych z AI"
    })
    
    print("\n🎉 Wynik:")
    print(result.raw)
    
    # Dostęp do poszczególnych wyników
    for task_output in result.tasks_output:
        print(f"\n📌 {task_output.task}: {task_output.raw[:200]}...")


# Opcja 2: Przez API
def api_example():
    import requests
    
    API_KEY = os.getenv("LITECREW_API_KEY", "your-api-key-here")
    API_URL = "https://api.litecrew.app/api/v1"
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Przykład prostego zadania
    single_task_crew = {
        "name": "Quick Analysis Crew",
        "agents": [{
            "role": "Analyst",
            "goal": "Analyze data and provide insights",
            "backstory": "Data science expert"
        }],
        "tasks": [{
            "description": "Analyze the impact of {topic} on {industry}",
            "agent_role": "Analyst",
            "expected_output": "Detailed analysis with pros, cons, and recommendations"
        }],
        "process": "sequential"
    }
    
    # Utwórz crew
    response = requests.post(
        f"{API_URL}/crews",
        json=single_task_crew,
        headers=headers
    )
    crew_id = response.json()["crew_id"]
    
    # Wykonaj
    execution = requests.post(
        f"{API_URL}/crews/{crew_id}/execute",
        json={
            "inputs": {
                "topic": "AI agents",
                "industry": "customer service"
            }
        },
        headers=headers
    )
    
    print(execution.json()["result"]["raw"])


if __name__ == "__main__":
    # Wybierz metodę
    print("Wybierz metodę:")
    print("1. Lokalnie (wymaga instalacji)")
    print("2. Przez API")
    
    choice = input("Wybór (1/2): ")
    
    if choice == "1":
        local_example()
    else:
        api_example()
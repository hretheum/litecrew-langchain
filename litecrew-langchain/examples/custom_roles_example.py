"""
🎨 TY DEFINIUJESZ WSZYSTKIE ROLE I ZADANIA!
"""

# PRZYKŁAD 1: Standardowe role (możesz użyć typowych nazw)
standard_crew = {
    "agents": [
        {
            "role": "Researcher",       # <-- TY to wymyślasz
            "goal": "Find information", # <-- TY decydujesz
            "backstory": "Expert at research" # <-- TY opisujesz
        }
    ]
}

# PRZYKŁAD 2: Całkowicie własne role! 
pizza_crew = {
    "name": "Pizza Delivery Optimization Crew",
    "agents": [
        {
            "role": "Pizza Route Optimizer",  # <-- Twoja własna rola!
            "goal": "Znajdź najszybszą trasę dostawy dla 10 pizz",
            "backstory": "Były kurier z 10-letnim doświadczeniem w Warszawie"
        },
        {
            "role": "Customer Happiness Specialist",  # <-- Inna własna rola!
            "goal": "Zaproponuj sposób na zwiększenie satysfakcji klientów",
            "backstory": "Psycholog biznesu specializujący się w food delivery"
        },
        {
            "role": "Pizza Cost Analyst",  # <-- Jeszcze inna!
            "goal": "Oblicz optymalną cenę z marżą 40%",
            "backstory": "Ekonomista z doświadczeniem w gastronomii"
        }
    ],
    "tasks": [
        {
            "description": "Zaplanuj trasę dla 10 dostaw w Warszawie (adresy: {addresses})",
            "agent_role": "Pizza Route Optimizer",  # <-- Musi pasować do roli agenta!
            "expected_output": "Optymalna trasa z czasem przejazdu"
        },
        {
            "description": "Zaproponuj 5 sposobów na poprawę doświadczenia klienta",
            "agent_role": "Customer Happiness Specialist",
            "expected_output": "Lista 5 konkretnych działań z uzasadnieniem"
        }
    ]
}

# PRZYKŁAD 3: Kreatywne role dla projektu gry
game_crew = {
    "name": "Indie Game Development Crew",
    "agents": [
        {
            "role": "Lore Master",  # <-- Wymyślona rola!
            "goal": "Stwórz fascynującą historię świata gry",
            "backstory": "Fan Tolkiena i Sapkowskiego, twórca 3 powieści fantasy"
        },
        {
            "role": "Gameplay Mechanic Wizard",  # <-- Inna wymyślona!
            "goal": "Zaprojektuj innowacyjne mechaniki rozgrywki",
            "backstory": "Gracz od 20 lat, analizuje mechaniki we wszystkich grach"
        },
        {
            "role": "Monetization Strategist",  # <-- Kolejna własna!
            "goal": "Zaproponuj etyczny model monetyzacji",
            "backstory": "Były product manager z mobilnego gamingu"
        }
    ]
}

# PRZYKŁAD 4: Nietypowe role dla osobistego projektu
personal_crew = {
    "name": "Mój Osobisty Asystent Crew",
    "agents": [
        {
            "role": "Prokrastynation Killer",  # <-- Zabawna własna rola!
            "goal": "Znajdź sposób jak przestać odkładać zadania",
            "backstory": "Life coach specjalizujący się w produktywności"
        },
        {
            "role": "Motivation Booster",
            "goal": "Przygotuj codzienny plan motywacyjny",
            "backstory": "Trener mentalny pracujący ze sportowcami"
        },
        {
            "role": "Reality Checker",
            "goal": "Oceń realność moich planów",
            "backstory": "Pragmatyk z 20-letnim doświadczeniem w zarządzaniu projektami"
        }
    ]
}

"""
ZASADY:

1. ROLE - możesz wymyślić DOWOLNE!
   ✅ "Senior Developer"
   ✅ "Pizza Optimizer" 
   ✅ "Meme Creator"
   ✅ "Alien Communication Specialist"
   ✅ "Chocolate Quality Inspector"

2. GOAL - Ty decydujesz co agent ma osiągnąć

3. BACKSTORY - Ty tworzysz "osobowość" agenta

4. TASK agent_role - MUSI pasować do role agenta!
   
   ❌ ŹLE:
   agent.role = "Writer"
   task.agent_role = "Researcher"  # Nie pasuje!
   
   ✅ DOBRZE:
   agent.role = "Writer"
   task.agent_role = "Writer"  # Pasuje!

MOŻESZ BYĆ KREATYWNY! 
LiteCrew zaakceptuje każdą rolę którą wymyślisz 🚀
"""
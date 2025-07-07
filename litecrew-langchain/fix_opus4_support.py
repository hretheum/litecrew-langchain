"""
Jak dodać wsparcie dla Opus 4 w LiteCrew
"""

# OPCJA 1: Minimalny fix - dodaj model do listy w utils.py
def fix_utils():
    """
    W pliku src/litecrew/llm/utils.py dodaj Opus 4 do listy:
    """
    context_lengths = {
        "anthropic": {
            "claude-3-opus": 200000,
            "claude-3-opus-20240229": 200000,
            "claude-opus-4-20250514": 200000,  # <-- DODAJ TO!
            "claude-3-sonnet": 200000,
            "claude-3-haiku": 200000,
        }
    }

# OPCJA 2: Update langchain-anthropic
"""
Problem: langchain-anthropic może nie mieć jeszcze wsparcia dla Opus 4
Rozwiązanie: Update do najnowszej wersji

W requirements.txt zmień:
langchain-anthropic>=0.1.0

Na:
langchain-anthropic>=0.2.0  # lub najnowsza wersja
"""

# OPCJA 3: Monkey patch (szybki fix bez rebuildu)
def monkey_patch_on_server():
    """
    Możesz dodać to do kodu startowego API:
    """
    import os
    
    # Force model name mapping
    if os.getenv("LITECREW_DEFAULT_MODEL") == "claude-opus-4-20250514":
        # Możemy próbować przekazać jako jest
        # LangChain powinien to przyjąć jeśli API Anthropic to wspiera
        pass
    
    # Alternatywnie - podmień na znany model
    # os.environ["LITECREW_DEFAULT_MODEL"] = "claude-3-opus-20240229"

# NAJLEPSZE ROZWIĄZANIE:
"""
1. Sprawdź czy najnowszy langchain-anthropic wspiera Opus 4:
   pip install langchain-anthropic --upgrade
   
2. Jeśli tak - tylko dodaj model do utils.py
3. Jeśli nie - możemy użyć bezpośrednio Anthropic SDK:
"""

def use_direct_anthropic():
    """
    Alternatywa - użyj bezpośrednio Anthropic SDK
    """
    from anthropic import Anthropic
    
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    
    response = client.messages.create(
        model="claude-opus-4-20250514",  # <-- Opus 4!
        max_tokens=1000,
        messages=[
            {"role": "user", "content": "Hello Opus 4!"}
        ]
    )
    
    return response.content[0].text

# QUICK TEST:
"""
Sprawdź czy LangChain przyjmie Opus 4:

from langchain_anthropic import ChatAnthropic

chat = ChatAnthropic(
    model_name="claude-opus-4-20250514",
    anthropic_api_key="sk-ant-..."
)

response = chat.invoke("Test Opus 4")
print(response.content)
"""
#!/usr/bin/env python3
# test_litecrew.py
import sys
print(f"Python: {sys.executable}")

try:
    import crewai
    print(f"CrewAI version: {crewai.__version__}")
    print(f"CrewAI location: {crewai.__file__}")
    
    # Test basic functionality
    agent = crewai.Agent(
        role="Test Agent",
        goal="Verify installation",
        backstory="A test agent"
    )
    print("✅ LiteCrew fork works!")
except Exception as e:
    print(f"❌ Error: {e}")
#!/usr/bin/env python3
# test_litecrew_simple.py
import sys
print(f"Python: {sys.executable}")

try:
    # Test only core imports
    sys.path.insert(0, '/Users/hretheum/dev/bezrobocie/litecrew/crewai-fork/src')
    
    # Import version info
    from crewai import __version__
    print(f"✅ LiteCrew version: {__version__}")
    print(f"✅ LiteCrew fork is accessible!")
    
    # Test basic imports without heavy dependencies
    from crewai.process import Process
    from crewai.tasks.task_output import TaskOutput
    print("✅ Core modules imported successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
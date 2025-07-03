#\!/bin/bash
# Prosty benchmark na droplet

apt-get update -qq
apt-get install -y python3.11 python3.11-venv python3-pip git

cd /root

# Test 1: CrewAI Official
python3.11 -m venv test_crewai
source test_crewai/bin/activate
pip install crewai==0.134.0
python3 -c "
import time
import sys
import os
start = time.time()
import crewai
print(f'CrewAI import time: {time.time()-start:.3f}s')
print(f'CrewAI size: {sum(os.path.getsize(os.path.join(dirpath,filename)) for dirpath, dirnames, filenames in os.walk(sys.prefix) for filename in filenames)/1024/1024:.1f}MB')
"
deactivate

# Test 2: LangChain  
python3.11 -m venv test_langchain
source test_langchain/bin/activate
pip install langchain langchain-openai
python3 -c "
import time
import sys
import os
start = time.time()
import langchain
print(f'LangChain import time: {time.time()-start:.3f}s')
print(f'LangChain size: {sum(os.path.getsize(os.path.join(dirpath,filename)) for dirpath, dirnames, filenames in os.walk(sys.prefix) for filename in filenames)/1024/1024:.1f}MB')
"
deactivate

# Test 3: PyAutoGen
python3.11 -m venv test_autogen
source test_autogen/bin/activate
pip install pyautogen
python3 -c "
import time
import sys
import os
start = time.time()
import autogen
print(f'AutoGen import time: {time.time()-start:.3f}s')
print(f'AutoGen size: {sum(os.path.getsize(os.path.join(dirpath,filename)) for dirpath, dirnames, filenames in os.walk(sys.prefix) for filename in filenames)/1024/1024:.1f}MB')
"
deactivate

echo "BENCHMARK COMPLETED"
EOF < /dev/null
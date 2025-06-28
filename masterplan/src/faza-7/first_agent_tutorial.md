# docs/tutorials/first-agent.md

# Tutorial: Building Your First Agent

## Goal

Create an agent that can research topics and write summaries.

## Step 1: Setup

```bash
# Create project directory
mkdir my-first-agent
cd my-first-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install LiteCrewAI
pip install litecrewai
```

## Step 2: Create the Agent

Create `research_agent.py`:

```python
import asyncio
from litecrewai import Agent, Task
from litecrewai.tools import WebSearch, FileWriter

async def main():
    # Create research agent
    researcher = Agent(
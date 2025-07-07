# Agent Type System Documentation

## Overview

LiteCrew's Agent Type System allows you to create specialized agents with predefined behaviors, personalities, and interaction styles. This system extends the base Agent functionality with type-specific enhancements that make agents more effective for particular roles.

## Available Agent Types

### 1. ConversationalAgent
**Purpose**: Optimized for natural, flowing conversations and dialogue management.

**Key Features**:
- Maintains conversation context and builds on previous topics
- Uses friendly, engaging communication style
- Asks clarifying questions when appropriate
- Ensures responses flow naturally in dialogue

**Configuration Options**:
```python
type_config = {
    "conversation_style": "friendly"  # Options: formal, friendly, casual, adaptive
}
```

**Use Cases**:
- Customer service bots
- Interview agents
- Social conversation partners
- Educational tutors

### 2. ThinkingAgent
**Purpose**: Shows detailed reasoning and thought processes in responses.

**Key Features**:
- Explicit step-by-step reasoning
- Considers multiple alternatives
- Shows work and justifications
- Verbose output with detailed analysis

**Configuration Options**:
```python
type_config = {
    "thinking_verbosity": 7  # Scale 1-10 (higher = more detailed)
}
```

**Use Cases**:
- Problem solving and analysis
- Research and investigation
- Code review and debugging
- Strategic planning

### 3. ModeratorAgent
**Purpose**: Facilitates discussions and ensures productive dialogue between multiple participants.

**Key Features**:
- Keeps discussions on track
- Ensures fair participation
- Summarizes key points
- Manages time and flow
- Resolves conflicts diplomatically

**Configuration Options**:
```python
type_config = {
    "moderation_style": "balanced"  # Options: strict, balanced, permissive
}
```

**Use Cases**:
- Panel discussions
- Team meetings
- Debate moderation
- Workshop facilitation

### 4. CriticAgent
**Purpose**: Provides constructive criticism and identifies areas for improvement.

**Key Features**:
- Balanced feedback (acknowledges positives and negatives)
- Specific, actionable suggestions
- Evidence-based criticism
- Prioritized feedback by importance

**Configuration Options**:
```python
type_config = {
    "criticism_level": "moderate"  # Options: mild, moderate, harsh
}
```

**Use Cases**:
- Code review
- Content editing
- Design critique
- Performance evaluation

## Using Agent Types

### Creating a Typed Agent

```python
from litecrew import Agent

# Create a conversational agent
assistant = Agent(
    role="Customer Support",
    goal="Help customers with their inquiries",
    backstory="Experienced support specialist with a friendly demeanor",
    type="conversational",
    type_config={
        "conversation_style": "friendly"
    }
)

# Create a thinking agent
analyst = Agent(
    role="Data Analyst",
    goal="Analyze data and provide insights",
    backstory="Expert analyst with attention to detail",
    type="thinking",
    type_config={
        "thinking_verbosity": 8
    }
)
```

### Via API

```bash
# Create a critic agent
curl -X POST "http://localhost:8000/api/v1/agents" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "role": "Code Reviewer",
    "goal": "Review code for quality and best practices",
    "backstory": "Senior developer with high standards",
    "type": "critic",
    "type_config": {
      "criticism_level": "moderate"
    }
  }'

# List available agent types
curl "http://localhost:8000/api/v1/agents/types" \
  -H "X-API-Key: your-api-key"

# Get info about a specific type
curl "http://localhost:8000/api/v1/agents/types/moderator" \
  -H "X-API-Key: your-api-key"
```

### In Crew Configuration

```python
crew = Crew(
    agents=[
        {
            "role": "Discussion Leader",
            "goal": "Facilitate productive team discussion",
            "backstory": "Experienced facilitator",
            "type": "moderator",
            "type_config": {
                "moderation_style": "balanced"
            }
        },
        {
            "role": "Devil's Advocate",
            "goal": "Challenge assumptions and identify weaknesses",
            "backstory": "Critical thinker who questions everything",
            "type": "critic",
            "type_config": {
                "criticism_level": "harsh"
            }
        }
    ],
    tasks=[...]
)
```

## Personality System

Each agent type has an associated personality profile that influences behavior:

### Personality Traits

- **ANALYTICAL**: Focuses on data and logic
- **CREATIVE**: Generates novel ideas and solutions
- **CRITICAL**: Questions and evaluates rigorously
- **SUPPORTIVE**: Encourages and assists others
- **DETAIL_ORIENTED**: Pays attention to specifics
- **BIG_PICTURE**: Focuses on overall strategy
- **COLLABORATIVE**: Works well with others
- **INDEPENDENT**: Self-directed and autonomous
- **OPTIMISTIC**: Positive outlook
- **SKEPTICAL**: Questions claims and assumptions
- **METHODICAL**: Systematic approach
- **SPONTANEOUS**: Flexible and adaptive

### Default Personalities by Type

- **ConversationalAgent**: Collaborative, Supportive
- **ThinkingAgent**: Analytical, Methodical, Detail-Oriented
- **ModeratorAgent**: Collaborative, Big-Picture, Methodical
- **CriticAgent**: Critical, Analytical, Detail-Oriented, Skeptical

## Behavior Modifiers

Agent types use behavior modifiers to enhance responses:

### CriticalThinkingBehavior
- Adds analytical perspective
- Identifies strengths and weaknesses
- Levels: mild, moderate, harsh

### VerboseThinkingBehavior
- Expands on reasoning process
- Shows step-by-step analysis
- Verbosity scale: 1-10

### ModerationBehavior
- Adds facilitation elements
- Manages discussion flow
- Styles: strict, balanced, permissive

### ConversationalBehavior
- Enhances conversational flow
- Adds engagement elements
- Styles: formal, friendly, casual, adaptive

## Type Validation

Agent type configurations are validated to ensure correctness:

```python
# Validate an agent's type configuration
agent = Agent(
    role="Moderator",
    goal="Facilitate discussion",
    backstory="Experienced facilitator",
    type="moderator",
    type_config={"moderation_style": "balanced"}
)

# Check if configuration is valid
is_valid = agent.validate_type_config()  # Returns True/False

# Get type information
type_info = agent.get_type_info()
# Returns: {
#     "name": "moderator",
#     "description": "Facilitates discussions...",
#     "configurable_options": [...],
#     "personality": {...}
# }
```

## Custom Agent Types

While LiteCrew provides four built-in agent types, you can extend the system:

```python
from litecrew.agent_types import AgentType, AgentTypeConfig, AgentTypeFactory

class ResearcherAgent(AgentType):
    @classmethod
    def get_default_config(cls) -> AgentTypeConfig:
        return AgentTypeConfig(
            name="researcher",
            description="Conducts thorough research and fact-checking",
            system_prompt_template="...",
            require_reasoning=True,
            min_response_length=300
        )
    
    def enhance_prompt(self, base_prompt: str, context: Dict[str, Any]) -> str:
        return base_prompt + "\n\nProvide sources and citations for all claims."
    
    def process_response(self, response: str, context: Dict[str, Any]) -> str:
        # Add citation formatting
        return response

# Register the custom type
AgentTypeFactory.register_type("researcher", ResearcherAgent)
```

## Best Practices

1. **Choose the Right Type**: Select agent types that match the task requirements
2. **Configure Appropriately**: Adjust type configurations based on your needs
3. **Combine Types**: Use multiple typed agents in crews for complementary skills
4. **Monitor Performance**: Track metrics to ensure agents perform as expected
5. **Iterate**: Adjust configurations based on results

## Performance Considerations

- Agent type system adds <5ms overhead to agent creation
- Type validation happens once during initialization
- Behavior modifiers add minimal processing time (<1ms per response)
- Memory usage increases by ~1KB per typed agent

## Integration with Processes

Different agent types work best with specific process types:

- **ConversationalAgent** → ConversationalProcess
- **ModeratorAgent** → DebateProcess, PanelProcess
- **CriticAgent** → ConsensusProcess, SocraticProcess
- **ThinkingAgent** → BrainstormProcess, SequentialProcess

## Examples

### Customer Support Crew
```python
support_crew = Crew(
    agents=[
        Agent(role="Greeter", type="conversational", 
              type_config={"conversation_style": "friendly"}),
        Agent(role="Problem Solver", type="thinking",
              type_config={"thinking_verbosity": 7}),
        Agent(role="Quality Checker", type="critic",
              type_config={"criticism_level": "mild"})
    ],
    process="sequential"
)
```

### Research Panel
```python
research_panel = Crew(
    agents=[
        Agent(role="Moderator", type="moderator",
              type_config={"moderation_style": "balanced"}),
        Agent(role="Domain Expert", type="thinking",
              type_config={"thinking_verbosity": 9}),
        Agent(role="Skeptic", type="critic",
              type_config={"criticism_level": "harsh"})
    ],
    process="panel"
)
```

## Troubleshooting

**Issue**: Agent not behaving according to type
- Check type configuration is valid
- Verify type name is correct
- Ensure LLM supports instruction following

**Issue**: Type validation fails
- Review configuration options for the type
- Check value ranges (e.g., verbosity 1-10)
- Ensure all required fields are present

**Issue**: Performance degradation
- Reduce thinking verbosity for faster responses
- Use simpler types for basic tasks
- Consider caching for repeated queries
# Example LLM Provider Usage

# Initialize provider
llm = LLMProvider.create("ollama/mistral")

# Simple generation
response = llm.generate("Explain quantum computing")

# Streaming
for chunk in llm.stream_generate("Write a story"):
    print(chunk.text, end="")

# With parameters
response = llm.generate(
    "Translate to French: Hello",
    temperature=0.3,
    max_tokens=100
)
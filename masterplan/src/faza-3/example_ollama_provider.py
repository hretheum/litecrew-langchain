# Example Ollama Provider Usage

ollama = OllamaProvider(
    base_url="http://localhost:11434",
    default_model="mistral",
    timeout=30
)

# Check available models
models = ollama.list_models()

# Pull if needed
if "llama2" not in models:
    ollama.pull_model("llama2")

# Generate with specific model
response = ollama.generate(
    "Explain AI",
    model="llama2",
    temperature=0.7,
    format="json"  # Force JSON output
)

# Stream generation
for chunk in ollama.stream_generate("Write a poem"):
    print(chunk.text, end="", flush=True)

# Get embeddings
embeddings = ollama.embed(["text1", "text2"])
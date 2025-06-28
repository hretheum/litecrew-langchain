# Example Fallback Chain Usage

# Configure fallback chain
fallback = FallbackChain([
    ModelConfig("openai/gpt-4", retry_times=2),
    ModelConfig("anthropic/claude-3", retry_times=1),
    ModelConfig("groq/mixtral", retry_times=3),
    ModelConfig("ollama/mistral", retry_times=5)  # Local last resort
])

# Execute with automatic fallback
result = fallback.execute(
    task="Complex analysis",
    timeout=30,
    min_quality=0.8
)

print(f"Success: {result.success}")
print(f"Final model: {result.model_used}")
print(f"Attempts: {result.total_attempts}")
print(f"Fallback reasons: {result.fallback_trail}")

# Check health status
health = fallback.get_health_status()
for model, status in health.items():
    print(f"{model}: {status.state} (success rate: {status.success_rate:.1%})")
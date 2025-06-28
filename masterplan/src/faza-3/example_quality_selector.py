# Example Quality-Based Selector Usage

selector = QualityBasedSelector()

# Define task requirements
requirements = TaskRequirements(
    domain="medical",
    min_accuracy=0.95,
    needs_citations=True,
    output_format="structured",
    language="en"
)

# Get best model
model = selector.select_best_model(
    task="Explain treatment options for diabetes",
    requirements=requirements
)

print(f"Selected: {model.name}")
print(f"Expected quality: {model.expected_quality}")
print(f"Capabilities: {model.capabilities}")

# Execute with quality validation
response = selector.execute_with_validation(
    task="...",
    model=model,
    validate_output=True
)

if response.quality_score < requirements.min_accuracy:
    # Automatic retry with better model
    response = selector.escalate_and_retry(response)
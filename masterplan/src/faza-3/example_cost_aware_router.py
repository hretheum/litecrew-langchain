# Example Cost-Aware Router Usage

router = CostAwareRouter(
    monthly_budget=30.0,
    strategy="balanced"
)

# Analyze task and route
task = "Write a 500 word essay on AI"
model = router.select_model(
    task=task,
    min_quality=0.8,
    max_cost=0.10
)
print(f"Selected: {model} (est. cost: ${router.estimate_cost(task, model)})")

# Execute with budget tracking
response = router.execute(task)
print(f"Actual cost: ${response.cost}")
print(f"Budget remaining: ${router.budget_remaining}")

# Get recommendations
if router.budget_remaining < 5:
    print("Low budget! Switching to economy mode...")
    router.strategy = "greedy"
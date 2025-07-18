#!/bin/bash
# run_full_benchmark.sh - Główny skrypt uruchamiający pełny benchmark

set -e

# Kolory
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           LiteCrew Full Benchmark Suite v2.0               ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║  Testing: CrewAI, LangChain, PyAutoGen, LiteCrew Fork     ║${NC}"
echo -e "${BLUE}║  Metrics: Memory, CPU, Latency, Concurrency, Errors       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

# Sprawdź czy jesteśmy na droplecie
if [ ! -f /root/.droplet_benchmark ]; then
    echo -e "\n${RED}❌ This script should run on benchmark droplet!${NC}"
    echo "First run: ./infrastructure/setup_droplet.sh"
    exit 1
fi

# Funkcje pomocnicze
log_section() {
    echo -e "\n${YELLOW}═══ $1 ═══${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. Setup środowiska
log_section "Environment Setup"

# Python environment
if [ ! -d "benchmark_env" ]; then
    python3.11 -m venv benchmark_env
    log_success "Virtual environment created"
fi

source benchmark_env/bin/activate
pip install --quiet -r requirements-benchmark.txt
log_success "Dependencies installed"

# 2. Start monitoring stack
log_section "Starting Monitoring Stack"

cd infrastructure
docker-compose up -d
cd ..

# Wait for services
echo -n "Waiting for Prometheus..."
while ! curl -s http://localhost:9090/-/ready > /dev/null; do
    echo -n "."
    sleep 2
done
log_success "Prometheus ready"

echo -n "Waiting for Grafana..."
while ! curl -s http://localhost:3000/api/health > /dev/null; do
    echo -n "."
    sleep 2
done
log_success "Grafana ready (admin/benchmark123)"

# 3. Framework Installation
log_section "Installing Frameworks"

# CrewAI
python -m venv envs/crewai
source envs/crewai/bin/activate
pip install --quiet crewai==0.134.0
deactivate
log_success "CrewAI installed"

# LangChain
python -m venv envs/langchain
source envs/langchain/bin/activate
pip install --quiet langchain langchain-openai
deactivate
log_success "LangChain installed"

# PyAutoGen
python -m venv envs/ag2
source envs/ag2/bin/activate
pip install --quiet ag2
deactivate
log_success "PyAutoGen installed"

# LiteCrew Fork
if [ -d "../crewai-fork" ]; then
    python -m venv envs/litecrew
    source envs/litecrew/bin/activate
    pip install --quiet -e ../crewai-fork
    deactivate
    log_success "LiteCrew Fork installed"
else
    log_error "LiteCrew Fork not found - skipping"
fi

# 4. Run Benchmarks
log_section "Running Benchmarks"

source benchmark_env/bin/activate

# Start metrics collector
python -m test_scenarios.benchmark_suite &
METRICS_PID=$!
log_success "Metrics collector started (PID: $METRICS_PID)"

# Run each framework
FRAMEWORKS=("crewai" "langchain" "ag2" "litecrew")
ITERATIONS=3

for framework in "${FRAMEWORKS[@]}"; do
    echo -e "\n${BLUE}Testing $framework...${NC}"
    
    if [ -d "envs/$framework" ]; then
        # Create adapter runner
        cat > run_framework_test.py << EOF
import sys
sys.path.append('.')

from framework_adapters.${framework}_adapter import ${framework^}Adapter
from test_scenarios.benchmark_suite import FrameworkBenchmark
from pathlib import Path

# Initialize
adapter = ${framework^}Adapter()
benchmark = FrameworkBenchmark("$framework", adapter)

# Run tests
results = benchmark.run_all_tests(iterations=$ITERATIONS)

# Save results
benchmark.save_results(Path("results/raw-data"))

print(f"\n✅ {len(results)} test results collected")
EOF

        # Run in framework environment
        source envs/$framework/bin/activate
        python run_framework_test.py
        deactivate
        
        # Cool down between frameworks
        sleep 30
        
    else
        log_error "$framework environment not found - skipping"
    fi
done

# 5. Generate Reports
log_section "Generating Reports"

source benchmark_env/bin/activate

python << EOF
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load all results
results_dir = Path("results/raw-data")
all_results = []

for result_file in results_dir.glob("*.json"):
    with open(result_file) as f:
        data = json.load(f)
        all_results.extend(data["results"])

# Convert to DataFrame
df = pd.DataFrame(all_results)

# Generate summary report
summary = df.groupby(['framework', 'test_name']).agg({
    'duration_seconds': ['mean', 'std'],
    'memory_peak_mb': ['mean', 'max'],
    'cpu_percent': ['mean', 'max'],
    'success': 'mean'
}).round(2)

# Save summary
summary.to_csv("results/benchmark_summary.csv")
print("📊 Summary saved to results/benchmark_summary.csv")

# Generate plots
plt.style.use('dark_background')
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# 1. Response Time
df.boxplot(column='duration_seconds', by='framework', ax=axes[0,0])
axes[0,0].set_title('Response Time by Framework')

# 2. Memory Usage
df.boxplot(column='memory_peak_mb', by='framework', ax=axes[0,1])
axes[0,1].set_title('Peak Memory Usage by Framework')

# 3. Success Rate
success_rates = df.groupby('framework')['success'].mean()
success_rates.plot(kind='bar', ax=axes[1,0])
axes[1,0].set_title('Success Rate by Framework')

# 4. Test Performance Heatmap
pivot = df.pivot_table(values='duration_seconds', index='test_name', columns='framework', aggfunc='mean')
sns.heatmap(pivot, annot=True, fmt='.2f', ax=axes[1,1])
axes[1,1].set_title('Test Duration Heatmap (seconds)')

plt.tight_layout()
plt.savefig('results/benchmark_overview.png', dpi=300)
print("📈 Plots saved to results/benchmark_overview.png")
EOF

# 6. Export Prometheus data
log_section "Exporting Metrics"

# Query Prometheus for detailed metrics
curl -s "http://localhost:9090/api/v1/query_range?query=framework_response_time_seconds&start=$(date -u -d '1 hour ago' +%s)&end=$(date +%s)&step=15s" \
    > results/prometheus_response_times.json

curl -s "http://localhost:9090/api/v1/query_range?query=framework_memory_usage_mb&start=$(date -u -d '1 hour ago' +%s)&end=$(date +%s)&step=15s" \
    > results/prometheus_memory_usage.json

log_success "Prometheus metrics exported"

# 7. Generate final report
log_section "Final Report"

cat > results/BENCHMARK_REPORT.md << 'EOF'
# 📊 Full Benchmark Report

Generated: $(date)

## Executive Summary

TODO: Add summary from CSV

## Detailed Results

See attached files:
- `benchmark_summary.csv` - Statistical summary
- `benchmark_overview.png` - Visual comparison
- `prometheus_*.json` - Time series data
- `raw-data/` - Complete test results

## Recommendations

Based on the comprehensive testing:

1. **Best Overall**: [Framework] - [Reason]
2. **Best for Memory**: [Framework] - [Usage]
3. **Best for Speed**: [Framework] - [Usage]
4. **Best for Scale**: [Framework] - [Usage]

## Next Steps

1. Migration guide for selected framework
2. Optimization opportunities
3. Production deployment plan

EOF

log_success "Report generated: results/BENCHMARK_REPORT.md"

# 8. Cleanup
log_section "Cleanup"

# Stop metrics collector
kill $METRICS_PID 2>/dev/null || true

# Create archive
tar -czf "benchmark_results_$(date +%Y%m%d_%H%M%S).tar.gz" results/
log_success "Results archived"

# Final summary
echo -e "\n${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ BENCHMARK COMPLETE!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo "📊 View results:"
echo "  - Grafana: http://$(curl -s ifconfig.me):3000 (admin/benchmark123)"
echo "  - Report: results/BENCHMARK_REPORT.md"
echo "  - Archive: benchmark_results_*.tar.gz"
echo ""
echo "🧹 To cleanup:"
echo "  - Stop monitoring: cd infrastructure && docker-compose down"
echo "  - Destroy droplet: doctl compute droplet delete [droplet-id] --force"
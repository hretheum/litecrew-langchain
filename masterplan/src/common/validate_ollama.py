# validate_ollama.py
import requests
import time
import psutil
import subprocess

def test_ollama_service():
    """Test Ollama service status"""
    result = subprocess.run(["systemctl", "is-active", "ollama"], capture_output=True, text=True)
    assert result.stdout.strip() == "active", "Ollama service not active"
    print("✅ Ollama service active")

def test_ollama_models():
    """Test required models are installed"""
    response = requests.get("http://localhost:11434/api/tags")
    assert response.status_code == 200, "Ollama API not responding"
    
    models = response.json()["models"]
    model_names = [m["name"] for m in models]
    
    required = ["mistral:7b", "phi-2", "nomic-embed-text"]
    for model in required:
        assert any(model in name for name in model_names), f"Missing model: {model}"
    
    print("✅ All required models installed")

def test_ollama_performance():
    """Test generation performance"""
    prompt = "Explain quantum computing in exactly 50 words."
    
    start_time = time.time()
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral:7b",
        "prompt": prompt,
        "stream": False
    })
    generation_time = time.time() - start_time
    
    assert response.status_code == 200, "Generation failed"
    assert generation_time < 3.0, f"Generation too slow: {generation_time:.2f}s"
    
    print(f"✅ Generation performance: {generation_time:.2f}s")

def test_resource_limits():
    """Test Ollama resource limits"""
    # Get Ollama process
    for proc in psutil.process_iter(['pid', 'name']):
        if 'ollama' in proc.info['name']:
            ollama_proc = psutil.Process(proc.info['pid'])
            
            # Check memory usage
            mem_info = ollama_proc.memory_info()
            mem_mb = mem_info.rss / 1024 / 1024
            assert mem_mb < 1500, f"Memory usage too high: {mem_mb:.0f}MB"
            
            # Check CPU cores
            cpu_affinity = ollama_proc.cpu_affinity()
            assert len(cpu_affinity) <= 2, f"Too many CPU cores: {len(cpu_affinity)}"
            
            print(f"✅ Resource limits OK: {mem_mb:.0f}MB RAM, {len(cpu_affinity)} cores")
            break

if __name__ == "__main__":
    test_ollama_service()
    test_ollama_models()
    test_ollama_performance()
    test_resource_limits()
    print("✅ All Ollama checks passed!")
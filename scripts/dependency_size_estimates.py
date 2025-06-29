#!/usr/bin/env python3
"""
Package size estimates based on typical PyPI package sizes.
These are approximate sizes for common packages.
"""

# Package sizes in MB (approximate)
PACKAGE_SIZES = {
    # Core Dependencies
    "pydantic": 2.5,
    "python-dotenv": 0.02,
    "click": 0.6,
    "jsonref": 0.02,
    "tomli-w": 0.01,
    "tomli": 0.02,
    "blinker": 0.02,
    
    # LLM/AI Dependencies (typically large)
    "openai": 0.8,
    "litellm": 15.0,  # Very large due to included models
    "instructor": 0.5,
    
    # Document Processing
    "pdfplumber": 5.0,  # Large due to pdfminer dependencies
    "openpyxl": 2.5,
    
    # ML/Data Processing
    "chromadb": 45.0,  # Very large - includes onnx, sentence-transformers
    "tokenizers": 15.0,  # Large compiled extension
    "onnxruntime": 150.0,  # Extremely large - ML runtime
    "regex": 0.4,  # Compiled extension
    
    # Visualization
    "pyvis": 0.5,
    
    # Utilities
    "appdirs": 0.02,
    "json-repair": 0.1,
    "json5": 0.03,
    "uv": 25.0,  # Large - Rust-based package manager
    
    # Optional dependencies
    "crewai-tools": 5.0,
    "tiktoken": 2.0,
    "agentops": 1.0,
    "pandas": 30.0,
    "mem0ai": 10.0,
    "docling": 20.0,
    "aisuite": 5.0,
    
    # Dev dependencies
    "ruff": 8.0,
    "mypy": 15.0,
    "pre-commit": 0.5,
    "pillow": 3.0,
    "cairosvg": 2.0,
    "pytest": 1.5,
    "pytest-asyncio": 0.1,
    "pytest-subprocess": 0.05,
    "pytest-recording": 0.1,
    "pytest-randomly": 0.05,
    "pytest-timeout": 0.05,
}

def get_size_estimate(package_name: str) -> float:
    """Get estimated size in MB for a package"""
    return PACKAGE_SIZES.get(package_name, 0.5)  # Default 0.5 MB for unknown packages

def format_size(size_mb: float) -> str:
    """Format size for display"""
    if size_mb < 1:
        return f"{int(size_mb * 1024)} KB"
    else:
        return f"{size_mb:.1f} MB"

if __name__ == "__main__":
    # Print size estimates
    print("Package Size Estimates")
    print("=" * 50)
    
    categories = {
        "Core": ["pydantic", "python-dotenv", "click", "jsonref", "tomli-w", "tomli", "blinker"],
        "LLM/AI": ["openai", "litellm", "instructor"],
        "Heavy Dependencies": ["chromadb", "onnxruntime", "tokenizers", "uv", "pandas"],
        "Document Processing": ["pdfplumber", "openpyxl"],
        "Removable": ["appdirs", "json-repair", "json5", "pyvis"],
    }
    
    total_size = 0
    for category, packages in categories.items():
        print(f"\n{category}:")
        category_size = 0
        for package in packages:
            size = get_size_estimate(package)
            category_size += size
            total_size += size
            print(f"  {package:20} {format_size(size):>10}")
        print(f"  {'Subtotal:':20} {format_size(category_size):>10}")
    
    print(f"\n{'Total Estimated Size:':20} {format_size(total_size):>10}")
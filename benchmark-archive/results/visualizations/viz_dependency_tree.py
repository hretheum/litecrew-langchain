#!/usr/bin/env python3
"""
Dependency Tree Visualization
Creates an interactive network graph of package dependencies
"""

import networkx as nx
import pyvis.network as net
import json
import pandas as pd

# Dependency data from benchmarks
dependencies_data = {
    'CrewAI': {
        'direct': ['langchain', 'openai', 'chromadb', 'click', 'pydantic', 'litellm'],
        'total_count': 155,
        'major_deps': {
            'chromadb': 348,  # MB
            'langchain': 97,
            'openai': 12,
            'pydantic': 8,
            'click': 5,
            'litellm': 125
        }
    },
    'LiteCrew+ChromaDB': {
        'direct': ['chromadb', 'openai', 'pydantic', 'click', 'redis'],
        'total_count': 98,
        'major_deps': {
            'chromadb': 348,
            'openai': 12,
            'pydantic': 8,
            'click': 5,
            'redis': 2
        }
    },
    'LiteCrew+Faiss': {
        'direct': ['faiss-cpu', 'openai', 'pydantic', 'click', 'redis'],
        'total_count': 45,
        'major_deps': {
            'faiss-cpu': 5,
            'openai': 12,
            'pydantic': 8,
            'click': 5,
            'redis': 2
        }
    },
    'LiteCrew Slim': {
        'direct': ['openai', 'pydantic', 'click', 'redis'],
        'total_count': 32,
        'major_deps': {
            'openai': 12,
            'pydantic': 8,
            'click': 5,
            'redis': 2
        }
    }
}

# Create dependency network for CrewAI (worst case)
def create_dependency_network(framework_name, data):
    # Create network
    network = net.Network(height='800px', width='100%', bgcolor='#222222', 
                         font_color='white', directed=True)
    
    # Add physics for better layout
    network.set_options("""
    var options = {
      "physics": {
        "enabled": true,
        "forceAtlas2Based": {
          "gravitationalConstant": -100,
          "springLength": 200,
          "springConstant": 0.08
        },
        "solver": "forceAtlas2Based"
      },
      "edges": {
        "arrows": "to",
        "smooth": {
          "type": "continuous"
        }
      }
    }
    """)
    
    # Add root node
    network.add_node(framework_name, 
                    label=f"{framework_name}\n({data['total_count']} deps)",
                    size=50,
                    color='#FF6B6B',
                    font={'size': 20})
    
    # Add major dependencies
    for dep, size_mb in data['major_deps'].items():
        # Node size based on package size
        node_size = max(20, min(60, size_mb / 5))
        
        # Color based on size
        if size_mb > 100:
            color = '#FF4444'  # Red for large deps
        elif size_mb > 50:
            color = '#FFA500'  # Orange for medium
        else:
            color = '#44FF44'  # Green for small
            
        network.add_node(dep,
                        label=f"{dep}\n{size_mb}MB",
                        size=node_size,
                        color=color,
                        font={'size': 14})
        
        # Add edge with weight
        network.add_edge(framework_name, dep, 
                        width=max(1, size_mb / 50),
                        color='#CCCCCC')
    
    # Add second-level dependencies for ChromaDB (if present)
    if 'chromadb' in data['major_deps']:
        chromadb_deps = {
            'onnxruntime': 168,
            'torch': 150,
            'pandas': 24,
            'numpy': 20,
            'requests': 2
        }
        
        for dep, size_mb in chromadb_deps.items():
            node_size = max(15, min(40, size_mb / 8))
            network.add_node(f"chromadb/{dep}",
                           label=f"{dep}\n{size_mb}MB",
                           size=node_size,
                           color='#FFAA44',
                           font={'size': 12})
            network.add_edge('chromadb', f"chromadb/{dep}",
                           width=max(0.5, size_mb / 100),
                           color='#999999')
    
    return network

# Create networks for each framework
print("Creating dependency networks...")

# CrewAI network (full horror)
crewai_net = create_dependency_network('CrewAI Official', dependencies_data['CrewAI'])
crewai_net.save_graph('benchmark/results/visualizations/deps_crewai.html')

# LiteCrew Slim network (minimal)
litecrew_net = create_dependency_network('LiteCrew Slim', dependencies_data['LiteCrew Slim'])
litecrew_net.save_graph('benchmark/results/visualizations/deps_litecrew_slim.html')

print("✅ Dependency networks created!")

# Create comparison chart using networkx and matplotlib
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# CrewAI dependency tree
G1 = nx.DiGraph()
G1.add_node("CrewAI\n595.7MB", size=3000, color='#FF6B6B')
for dep, size in dependencies_data['CrewAI']['major_deps'].items():
    G1.add_node(f"{dep}\n{size}MB", size=size*10, color='#4ECDC4')
    G1.add_edge("CrewAI\n595.7MB", f"{dep}\n{size}MB", weight=size/50)

pos1 = nx.spring_layout(G1, k=3, iterations=50)
node_sizes1 = [G1.nodes[node].get('size', 100) for node in G1.nodes()]
node_colors1 = [G1.nodes[node].get('color', '#CCCCCC') for node in G1.nodes()]

nx.draw(G1, pos1, ax=ax1, 
        node_size=node_sizes1, 
        node_color=node_colors1,
        with_labels=True,
        font_size=10,
        font_weight='bold',
        arrows=True,
        edge_color='gray',
        width=[G1[u][v]['weight'] for u, v in G1.edges()])

ax1.set_title('CrewAI Dependencies (595.7MB)', fontsize=16, fontweight='bold')
ax1.axis('off')

# LiteCrew Slim dependency tree
G2 = nx.DiGraph()
G2.add_node("LiteCrew\n9.6MB", size=1000, color='#FECA57')
for dep, size in dependencies_data['LiteCrew Slim']['major_deps'].items():
    G2.add_node(f"{dep}\n{size}MB", size=size*20, color='#96CEB4')
    G2.add_edge("LiteCrew\n9.6MB", f"{dep}\n{size}MB", weight=1)

pos2 = nx.spring_layout(G2, k=2, iterations=50)
node_sizes2 = [G2.nodes[node].get('size', 100) for node in G2.nodes()]
node_colors2 = [G2.nodes[node].get('color', '#CCCCCC') for node in G2.nodes()]

nx.draw(G2, pos2, ax=ax2,
        node_size=node_sizes2,
        node_color=node_colors2,
        with_labels=True,
        font_size=10,
        font_weight='bold',
        arrows=True,
        edge_color='gray')

ax2.set_title('LiteCrew Slim Dependencies (9.6MB)', fontsize=16, fontweight='bold')
ax2.axis('off')

plt.suptitle('Dependency Tree Comparison: 98.4% Reduction!', fontsize=20, fontweight='bold')
plt.tight_layout()
plt.savefig('benchmark/results/visualizations/dependency_comparison.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('benchmark/results/visualizations/dependency_comparison.pdf', bbox_inches='tight', facecolor='white')
print("✅ Dependency comparison chart created!")

# Create dependency count comparison
fig3, ax3 = plt.subplots(figsize=(10, 6))

frameworks = list(dependencies_data.keys())
dep_counts = [data['total_count'] for data in dependencies_data.values()]
colors = ['#FF6B6B', '#4ECDC4', '#96CEB4', '#FECA57']

bars = ax3.bar(frameworks, dep_counts, color=colors, edgecolor='black', linewidth=2)

# Add value labels
for bar, count in zip(bars, dep_counts):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 2,
            f'{count}',
            ha='center', va='bottom', fontsize=14, fontweight='bold')

ax3.set_ylabel('Number of Dependencies', fontsize=14, fontweight='bold')
ax3.set_xlabel('Framework', fontsize=14, fontweight='bold')
ax3.set_title('Total Dependency Count by Framework\n79% Reduction in Dependencies!', 
             fontsize=16, fontweight='bold')
ax3.set_ylim(0, max(dep_counts) * 1.15)
ax3.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('benchmark/results/visualizations/dependency_count.png', dpi=300, bbox_inches='tight')
print("✅ Dependency count chart created!")

print("\n🎉 All dependency visualizations created successfully!")
print("Files created:")
print("  - deps_crewai.html (interactive network)")
print("  - deps_litecrew_slim.html (interactive network)")
print("  - dependency_comparison.png/pdf")
print("  - dependency_count.png")
#!/usr/bin/env python3
"""
Size Comparison Visualization
Creates waterfall chart showing package size reduction
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Data from benchmarks
data = {
    'Framework': ['CrewAI\nOfficial', 'LiteCrew+\nChromaDB', 'LangChain', 'LiteCrew+\nFaiss', 'LiteCrew\nSlim'],
    'Size (MB)': [595.7, 350, 97.3, 15, 9.6],
    'Reduction': ['0%', '-41%', '-84%', '-97.5%', '-98.4%']
}

df = pd.DataFrame(data)

# Create figure with larger size for better readability
fig, ax = plt.subplots(figsize=(12, 8))

# Create bar chart
bars = ax.bar(df['Framework'], df['Size (MB)'], 
               color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57'],
               edgecolor='black', linewidth=2)

# Add value labels on bars
for bar, size, reduction in zip(bars, df['Size (MB)'], df['Reduction']):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 10,
            f'{size:.1f} MB\n{reduction}',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

# Add horizontal lines for reference
ax.axhline(y=100, color='red', linestyle='--', alpha=0.3, label='100MB threshold')
ax.axhline(y=50, color='orange', linestyle='--', alpha=0.3, label='50MB threshold')

# Customize the plot
ax.set_ylabel('Package Size (MB)', fontsize=14, fontweight='bold')
ax.set_xlabel('Framework / Configuration', fontsize=14, fontweight='bold')
ax.set_title('AI Agent Framework Size Comparison\n98.4% Size Reduction Achieved! 🚀', 
             fontsize=18, fontweight='bold', pad=20)

# Set y-axis limit to show all data
ax.set_ylim(0, max(df['Size (MB)']) * 1.15)

# Add grid
ax.grid(axis='y', alpha=0.3)

# Add legend
ax.legend(loc='upper right', fontsize=10)

# Add annotation for the achievement
ax.annotate('98.4% SMALLER!', 
            xy=(4, 9.6), xytext=(3.5, 200),
            arrowprops=dict(arrowstyle='->', color='green', lw=2),
            fontsize=16, color='green', fontweight='bold',
            ha='center')

# Add watermark
plt.text(0.99, 0.01, 'LiteCrew Benchmark Results', 
         transform=ax.transAxes, ha='right', va='bottom',
         fontsize=8, alpha=0.5)

# Adjust layout
plt.tight_layout()

# Save in multiple formats
plt.savefig('benchmark/results/visualizations/size_reduction_waterfall.png', dpi=300, bbox_inches='tight')
plt.savefig('benchmark/results/visualizations/size_reduction_waterfall.pdf', bbox_inches='tight')
plt.savefig('benchmark/results/visualizations/size_reduction_waterfall.svg', bbox_inches='tight')

print("✅ Size comparison chart created successfully!")

# Create a second chart - horizontal bar for better readability
fig2, ax2 = plt.subplots(figsize=(10, 8))

# Sort data by size for better visual
df_sorted = df.sort_values('Size (MB)', ascending=True)

# Create horizontal bar chart
bars2 = ax2.barh(df_sorted['Framework'], df_sorted['Size (MB)'],
                  color=['#FECA57', '#96CEB4', '#45B7D1', '#4ECDC4', '#FF6B6B'],
                  edgecolor='black', linewidth=2)

# Add value labels
for bar, size, reduction in zip(bars2, df_sorted['Size (MB)'], df_sorted['Reduction']):
    width = bar.get_width()
    ax2.text(width + 10, bar.get_y() + bar.get_height()/2.,
             f'{size:.1f} MB ({reduction})',
             ha='left', va='center', fontsize=12, fontweight='bold')

# Customize
ax2.set_xlabel('Package Size (MB)', fontsize=14, fontweight='bold')
ax2.set_ylabel('Framework / Configuration', fontsize=14, fontweight='bold')
ax2.set_title('From 595.7 MB to 9.6 MB: The LiteCrew Journey', 
              fontsize=18, fontweight='bold', pad=20)
ax2.set_xlim(0, max(df['Size (MB)']) * 1.2)

# Add vertical reference lines
ax2.axvline(x=100, color='red', linestyle='--', alpha=0.3)
ax2.axvline(x=50, color='orange', linestyle='--', alpha=0.3)

# Grid
ax2.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('benchmark/results/visualizations/size_comparison_horizontal.png', dpi=300, bbox_inches='tight')

print("✅ Horizontal size comparison chart created successfully!")
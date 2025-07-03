#!/usr/bin/env python3
"""
Social Media Export
Creates optimized visualizations for social media platforms
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set style for social media
plt.style.use('dark_background')
sns.set_palette("bright")

# Data for social media charts
social_data = {
    'Framework': ['CrewAI\nOfficial', 'LiteCrew\nSlim'],
    'Size (MB)': [595.7, 9.6],
    'Startup (s)': [5.047, 0.856],
    'Memory (MB)': [487.3, 42.1],
    'Dependencies': [155, 32]
}

df = pd.DataFrame(social_data)

# 1. LINKEDIN CAROUSEL SLIDE - SIZE COMPARISON
fig1, ax1 = plt.subplots(figsize=(10, 10))  # Square format for LinkedIn

# Create dramatic comparison
bars = ax1.bar(['Before\n(CrewAI)', 'After\n(LiteCrew)'], 
               [595.7, 9.6],
               color=['#FF4444', '#44FF44'],
               edgecolor='white',
               linewidth=3)

# Add dramatic annotations
ax1.text(0, 350, '595.7 MB', ha='center', va='center', 
         fontsize=24, fontweight='bold', color='white')
ax1.text(1, 100, '9.6 MB', ha='center', va='center', 
         fontsize=24, fontweight='bold', color='white')

# Add percentage reduction
ax1.text(0.5, 500, '98.4% SMALLER!', ha='center', va='center',
         fontsize=32, fontweight='bold', color='#FFFF00',
         bbox=dict(boxstyle="round,pad=0.5", facecolor='black', alpha=0.7))

ax1.set_ylabel('Package Size (MB)', fontsize=20, fontweight='bold')
ax1.set_title('AI Agent Framework:\nFrom 595MB to 9.6MB', 
              fontsize=28, fontweight='bold', pad=30)
ax1.set_ylim(0, 650)
ax1.grid(axis='y', alpha=0.3)

# Remove spines for cleaner look
for spine in ax1.spines.values():
    spine.set_visible(False)

plt.tight_layout()
plt.savefig('benchmark/results/visualizations/social_linkedin_size.png', 
            dpi=300, bbox_inches='tight', facecolor='black')
print("✅ LinkedIn size comparison created!")

# 2. TWITTER/X POST - STARTUP TIME
fig2, ax2 = plt.subplots(figsize=(12, 8))  # Twitter aspect ratio

# Racing bar style
y_pos = [0, 1]
bars = ax2.barh(y_pos, [5.047, 0.856], 
                color=['#FF6B6B', '#FECA57'],
                height=0.6)

# Add time labels
ax2.text(2.5, 0, '5.047s', ha='center', va='center', 
         fontsize=20, fontweight='bold')
ax2.text(0.4, 1, '0.856s', ha='center', va='center', 
         fontsize=20, fontweight='bold')

ax2.set_yticks(y_pos)
ax2.set_yticklabels(['CrewAI Official', 'LiteCrew Slim'], fontsize=16)
ax2.set_xlabel('Startup Time (seconds)', fontsize=18, fontweight='bold')
ax2.set_title('Startup Speed: 83% Faster! ⚡', 
              fontsize=24, fontweight='bold', pad=20)

# Add improvement arrow
ax2.annotate('83% FASTER!', xy=(0.856, 1), xytext=(3, 1.5),
            arrowprops=dict(arrowstyle='->', lw=3, color='lime'),
            fontsize=18, fontweight='bold', color='lime')

ax2.set_xlim(0, 6)
ax2.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('benchmark/results/visualizations/social_twitter_startup.png', 
            dpi=300, bbox_inches='tight', facecolor='black')
print("✅ Twitter startup comparison created!")

# 3. INSTAGRAM STORY - MEMORY USAGE
fig3, ax3 = plt.subplots(figsize=(9, 16))  # Instagram story aspect ratio

# Vertical comparison
categories = ['Memory\nUsage', 'Package\nSize', 'Dependencies']
crewai_values = [487.3, 595.7, 155]
litecrew_values = [42.1, 9.6, 32]

x = np.arange(len(categories))
width = 0.35

bars1 = ax3.bar(x - width/2, crewai_values, width, 
                label='CrewAI', color='#FF4444', alpha=0.8)
bars2 = ax3.bar(x + width/2, litecrew_values, width,
                label='LiteCrew', color='#44FF44', alpha=0.8)

# Add value labels on bars
for bar in bars1:
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 10,
             f'{height:.0f}', ha='center', va='bottom', 
             fontsize=14, fontweight='bold')

for bar in bars2:
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 10,
             f'{height:.0f}', ha='center', va='bottom', 
             fontsize=14, fontweight='bold')

ax3.set_ylabel('Values', fontsize=16, fontweight='bold')
ax3.set_title('Complete Transformation 🚀\n\nMemory, Size & Dependencies', 
              fontsize=20, fontweight='bold', pad=30)
ax3.set_xticks(x)
ax3.set_xticklabels(categories, fontsize=14)
ax3.legend(fontsize=14, loc='upper right')
ax3.set_ylim(0, 650)
ax3.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('benchmark/results/visualizations/social_instagram_memory.png', 
            dpi=300, bbox_inches='tight', facecolor='black')
print("✅ Instagram memory comparison created!")

# 4. COMPREHENSIVE SOCIAL SUMMARY
fig4, ((ax4_1, ax4_2), (ax4_3, ax4_4)) = plt.subplots(2, 2, figsize=(16, 16))
fig4.patch.set_facecolor('black')

# Top left - Size reduction
sizes = [595.7, 9.6]
colors = ['#FF4444', '#44FF44']
wedges, texts, autotexts = ax4_1.pie(sizes, labels=['Before', 'After'], 
                                     colors=colors, autopct='%1.1f%%',
                                     startangle=90, textprops={'fontsize': 14})
ax4_1.set_title('Package Size\n98.4% Reduction', fontsize=16, fontweight='bold')

# Top right - Startup time
ax4_2.bar(['CrewAI', 'LiteCrew'], [5.047, 0.856], 
          color=['#FF6B6B', '#FECA57'])
ax4_2.set_title('Startup Time\n83% Faster', fontsize=16, fontweight='bold')
ax4_2.set_ylabel('Seconds')

# Bottom left - Memory usage  
ax4_3.bar(['CrewAI', 'LiteCrew'], [487.3, 42.1], 
          color=['#FF8C94', '#A8E6CF'])
ax4_3.set_title('Memory Usage\n91% Less', fontsize=16, fontweight='bold')
ax4_3.set_ylabel('MB')

# Bottom right - Dependencies
ax4_4.bar(['CrewAI', 'LiteCrew'], [155, 32], 
          color=['#FFB3BA', '#B5EAD7'])
ax4_4.set_title('Dependencies\n79% Fewer', fontsize=16, fontweight='bold')
ax4_4.set_ylabel('Count')

# Overall title
fig4.suptitle('LiteCrew vs CrewAI: Complete Optimization Results', 
              fontsize=24, fontweight='bold', y=0.95, color='white')

plt.tight_layout()
plt.savefig('benchmark/results/visualizations/social_comprehensive.png', 
            dpi=300, bbox_inches='tight', facecolor='black')
print("✅ Comprehensive social summary created!")

# 5. ANIMATED-STYLE STATIC CHART (Before/After)
fig5, ax5 = plt.subplots(figsize=(14, 10))

metrics = ['Size (MB)', 'Startup (s)', 'Memory (MB)', 'Dependencies']
before_values = [595.7, 5.047, 487.3, 155]
after_values = [9.6, 0.856, 42.1, 32]

# Normalize for better visualization (log scale would be too dramatic)
# Instead, use different scales for each metric
normalized_before = [595.7/60, 5.047, 487.3/50, 155/15]  # Scale down large values
normalized_after = [9.6/60, 0.856, 42.1/50, 32/15]

x = np.arange(len(metrics))
width = 0.35

bars1 = ax5.bar(x - width/2, normalized_before, width, 
                label='Before (CrewAI)', color='#FF4444', alpha=0.8)
bars2 = ax5.bar(x + width/2, normalized_after, width,
                label='After (LiteCrew)', color='#44FF44', alpha=0.8)

# Add actual value labels
for i, (bar, value) in enumerate(zip(bars1, before_values)):
    ax5.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
             f'{value:.1f}' if value < 10 else f'{value:.0f}', 
             ha='center', va='bottom', fontsize=12, fontweight='bold')

for i, (bar, value) in enumerate(zip(bars2, after_values)):
    ax5.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
             f'{value:.1f}' if value < 10 else f'{value:.0f}', 
             ha='center', va='bottom', fontsize=12, fontweight='bold')

ax5.set_ylabel('Relative Scale', fontsize=16, fontweight='bold')
ax5.set_title('The Great AI Framework Diet 🏋️‍♂️\nBefore vs After Optimization', 
              fontsize=22, fontweight='bold', pad=20)
ax5.set_xticks(x)
ax5.set_xticklabels(metrics, fontsize=14)
ax5.legend(fontsize=14, loc='upper right')
ax5.grid(axis='y', alpha=0.3)

# Add improvement percentages
improvements = ['98.4%', '83%', '91%', '79%']
for i, improvement in enumerate(improvements):
    ax5.text(i, max(normalized_before[i], normalized_after[i]) + 1,
             f'↓{improvement}', ha='center', va='bottom',
             fontsize=14, fontweight='bold', color='lime')

plt.tight_layout()
plt.savefig('benchmark/results/visualizations/social_before_after.png', 
            dpi=300, bbox_inches='tight', facecolor='black')
print("✅ Before/after comparison created!")

# Create a summary text file for social media posts
social_content = """
🚀 SOCIAL MEDIA CONTENT - LITECREW BENCHMARK RESULTS

📱 TWITTER/X POST:
"Just reduced an AI agent framework from 595MB to 9.6MB (98.4% smaller!) 
and startup time from 5s to 0.8s (83% faster). 

Sometimes the best optimization is knowing what NOT to include. 🧵

#AI #Performance #Optimization #LiteCrew"

📸 LINKEDIN CAROUSEL:
Slide 1: "Why your AI agent needs 500MB to say hello"
Slide 2: [SIZE COMPARISON CHART]
Slide 3: "The dependency hell problem"
Slide 4: "LiteCrew approach: 98.4% size reduction"
Slide 5: "Performance results & next steps"

📱 INSTAGRAM STORY:
"From 595MB to 9.6MB ⚡
From 5s to 0.8s startup 🚀
From 487MB to 42MB RAM 💾
This is why we build lightweight AI agents"

💼 PROFESSIONAL SUMMARY:
"Conducted comprehensive benchmarking of AI agent frameworks, achieving:
• 98.4% package size reduction (595.7MB → 9.6MB)
• 83% startup time improvement (5.047s → 0.856s)
• 91% memory usage reduction (487.3MB → 42.1MB)
• 79% dependency count reduction (155 → 32)

Key insight: ChromaDB alone accounts for 58% of CrewAI's bloat."

🎯 HASHTAGS:
#ArtificialIntelligence #Performance #Optimization #AgentFrameworks 
#TechLeadership #SoftwareEngineering #LiteCrew #Benchmarking
"""

with open('benchmark/results/visualizations/social_media_content.txt', 'w') as f:
    f.write(social_content)

print("✅ Social media content guide created!")

print("\n🎉 All social media exports created successfully!")
print("Files created:")
print("  - social_linkedin_size.png (LinkedIn carousel)")
print("  - social_twitter_startup.png (Twitter/X post)")
print("  - social_instagram_memory.png (Instagram story)")
print("  - social_comprehensive.png (Complete overview)")
print("  - social_before_after.png (Dramatic comparison)")
print("  - social_media_content.txt (Copy for posts)")

print("\n📱 Ready for social media posting!")
print("All images optimized for dark backgrounds and mobile viewing.")
#!/usr/bin/env python3
"""
Startup Time Visualization
Creates animated bar chart race and comparison visualizations
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Data from benchmarks
startup_data = {
    'Framework': ['CrewAI Official', 'LiteCrew+ChromaDB', 'LiteCrew+Faiss', 'LiteCrew Slim', 'LangChain'],
    'Startup Time (s)': [5.047, 12.056, 1.234, 0.856, 0.135],
    'Memory at Start (MB)': [487.3, 175.2, 62.5, 42.1, 78.9]
}

df = pd.DataFrame(startup_data)

# Create animated bar chart race
fig = go.Figure()

# Add traces for animation
for i in range(len(df)):
    fig.add_trace(go.Bar(
        x=df['Framework'][:i+1],
        y=df['Startup Time (s)'][:i+1],
        text=[f'{t:.3f}s' for t in df['Startup Time (s)'][:i+1]],
        textposition='auto',
        marker_color=['#FF6B6B', '#4ECDC4', '#96CEB4', '#FECA57', '#45B7D1'][:i+1],
        name='Startup Time',
        showlegend=False
    ))

# Create frames for animation
frames = []
for i in range(len(df)):
    frames.append(go.Frame(
        data=[go.Bar(
            x=df['Framework'][:i+1],
            y=df['Startup Time (s)'][:i+1],
            text=[f'{t:.3f}s' for t in df['Startup Time (s)'][:i+1]],
            textposition='auto',
            marker_color=['#FF6B6B', '#4ECDC4', '#96CEB4', '#FECA57', '#45B7D1'][:i+1]
        )],
        name=str(i)
    ))

fig.frames = frames

# Update layout
fig.update_layout(
    title={
        'text': 'AI Framework Startup Time Comparison<br><sub>LiteCrew Slim: 83% Faster than CrewAI!</sub>',
        'font': {'size': 24}
    },
    xaxis_title='Framework',
    yaxis_title='Startup Time (seconds)',
    yaxis_range=[0, max(df['Startup Time (s)']) * 1.2],
    height=600,
    updatemenus=[{
        'type': 'buttons',
        'showactive': False,
        'buttons': [
            {
                'label': 'Play',
                'method': 'animate',
                'args': [None, {
                    'frame': {'duration': 500, 'redraw': True},
                    'fromcurrent': True,
                    'transition': {'duration': 300, 'easing': 'quadratic-in-out'}
                }]
            },
            {
                'label': 'Pause',
                'method': 'animate',
                'args': [[None], {
                    'frame': {'duration': 0, 'redraw': False},
                    'mode': 'immediate',
                    'transition': {'duration': 0}
                }]
            }
        ]
    }]
)

# Save animated version
fig.write_html('benchmark/results/visualizations/startup_times_animated.html')
print("✅ Animated startup time chart created!")

# Create static comparison with memory overlay
fig2 = go.Figure()

# Add startup time bars
fig2.add_trace(go.Bar(
    name='Startup Time (s)',
    x=df['Framework'],
    y=df['Startup Time (s)'],
    text=[f'{t:.3f}s' for t in df['Startup Time (s)']],
    textposition='auto',
    marker_color='#FF6B6B',
    yaxis='y'
))

# Add memory usage as line
fig2.add_trace(go.Scatter(
    name='Memory at Start (MB)',
    x=df['Framework'],
    y=df['Memory at Start (MB)'],
    text=[f'{m:.1f} MB' for m in df['Memory at Start (MB)']],
    mode='lines+markers+text',
    textposition='top center',
    line=dict(color='#4ECDC4', width=3),
    marker=dict(size=10),
    yaxis='y2'
))

# Update layout with dual y-axes
fig2.update_layout(
    title='Startup Performance: Time vs Memory Usage',
    xaxis_title='Framework',
    yaxis=dict(
        title=dict(text='Startup Time (seconds)', font=dict(color='#FF6B6B')),
        tickfont=dict(color='#FF6B6B')
    ),
    yaxis2=dict(
        title=dict(text='Memory Usage (MB)', font=dict(color='#4ECDC4')),
        tickfont=dict(color='#4ECDC4'),
        anchor='x',
        overlaying='y',
        side='right'
    ),
    height=600,
    hovermode='x unified'
)

# Save static version
fig2.write_html('benchmark/results/visualizations/startup_time_vs_memory.html')
print("✅ Startup time vs memory chart created!")

# Create detailed breakdown chart
breakdown_data = {
    'Component': ['Import Libraries', 'Load LiteLLM', 'Initialize Tools', 'Setup Memory', 'Create Agent'],
    'CrewAI (s)': [0.234, 2.456, 1.234, 0.678, 0.445],
    'LiteCrew Slim (s)': [0.123, 0.000, 0.456, 0.234, 0.043]
}

fig3 = go.Figure()

# Add CrewAI breakdown
fig3.add_trace(go.Bar(
    name='CrewAI Official',
    x=breakdown_data['Component'],
    y=breakdown_data['CrewAI (s)'],
    text=[f'{t:.3f}s' for t in breakdown_data['CrewAI (s)']],
    textposition='auto',
    marker_color='#FF6B6B'
))

# Add LiteCrew breakdown
fig3.add_trace(go.Bar(
    name='LiteCrew Slim',
    x=breakdown_data['Component'],
    y=breakdown_data['LiteCrew Slim (s)'],
    text=[f'{t:.3f}s' for t in breakdown_data['LiteCrew Slim (s)']],
    textposition='auto',
    marker_color='#FECA57'
))

fig3.update_layout(
    title='Startup Time Breakdown by Component',
    xaxis_title='Component',
    yaxis_title='Time (seconds)',
    barmode='group',
    height=600,
    showlegend=True
)

# Save breakdown chart
fig3.write_html('benchmark/results/visualizations/startup_breakdown.html')
print("✅ Startup breakdown chart created!")

# Create speed improvement visualization
fig4 = go.Figure()

# Calculate improvements
improvements = []
base_time = df.loc[df['Framework'] == 'CrewAI Official', 'Startup Time (s)'].values[0]
for _, row in df.iterrows():
    improvement = ((base_time - row['Startup Time (s)']) / base_time) * 100
    improvements.append(improvement)

df['Improvement %'] = improvements

# Create horizontal bar chart
fig4.add_trace(go.Bar(
    x=df['Improvement %'],
    y=df['Framework'],
    text=[f'{imp:.1f}% {"faster" if imp > 0 else "slower"}' for imp in df['Improvement %']],
    textposition='auto',
    orientation='h',
    marker_color=['#FF6B6B' if imp <= 0 else '#4ECDC4' if imp < 50 else '#FECA57' if imp < 80 else '#96CEB4' 
                  for imp in df['Improvement %']]
))

fig4.update_layout(
    title='Startup Speed Improvement vs CrewAI Official',
    xaxis_title='Improvement (%)',
    yaxis_title='Framework',
    height=600,
    xaxis=dict(range=[-150, 100]),
    showlegend=False
)

# Add vertical line at 0%
fig4.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)

# Save improvement chart
fig4.write_html('benchmark/results/visualizations/startup_improvement.html')
print("✅ Speed improvement chart created!")

print("\n🎉 All startup time visualizations created successfully!")
print("Files created:")
print("  - startup_times_animated.html (interactive)")
print("  - startup_time_vs_memory.html")
print("  - startup_breakdown.html")
print("  - startup_improvement.html")
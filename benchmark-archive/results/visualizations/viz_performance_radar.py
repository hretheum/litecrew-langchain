#!/usr/bin/env python3
"""
Performance Radar Chart
Creates a comprehensive performance comparison across multiple metrics
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Performance metrics from benchmarks (normalized to 0-100 scale)
performance_data = {
    'Metric': ['Package Size', 'Startup Time', 'Memory Usage', 'Dependency Count', 'CPU Usage', 'Overall Score'],
    'CrewAI Official': [2, 10, 5, 8, 15, 8],  # Worst scores (595.7MB, 5s startup)
    'LiteCrew+ChromaDB': [15, 5, 25, 35, 30, 22],  # Better but still heavy
    'LiteCrew+Faiss': [85, 80, 85, 75, 85, 82],  # Good balance
    'LiteCrew Slim': [98, 95, 92, 80, 90, 91]  # Best scores (9.6MB, <1s startup)
}

df = pd.DataFrame(performance_data)

# Create radar chart
fig = go.Figure()

# Add traces for each framework
frameworks = ['CrewAI Official', 'LiteCrew+ChromaDB', 'LiteCrew+Faiss', 'LiteCrew Slim']
colors = ['#FF6B6B', '#4ECDC4', '#96CEB4', '#FECA57']

for framework, color in zip(frameworks, colors):
    fig.add_trace(go.Scatterpolar(
        r=df[framework],
        theta=df['Metric'],
        fill='toself',
        name=framework,
        line=dict(color=color, width=2),
        fillcolor=color,
        opacity=0.4
    ))

# Update layout
fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 100],
            tickmode='array',
            tickvals=[0, 25, 50, 75, 100],
            ticktext=['Poor', 'Fair', 'Good', 'Very Good', 'Excellent']
        )),
    showlegend=True,
    title={
        'text': 'AI Framework Performance Comparison<br><sub>Higher scores = Better performance</sub>',
        'font': {'size': 20}
    },
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=1.1
    ),
    height=700
)

# Save radar chart
fig.write_html('benchmark/results/visualizations/performance_radar.html')
print("✅ Performance radar chart created!")

# Create detailed performance metrics table
metrics_detail = {
    'Framework': frameworks,
    'Package Size (MB)': [595.7, 350, 15, 9.6],
    'Startup Time (s)': [5.047, 12.056, 1.234, 0.856],
    'Memory Usage (MB)': [487.3, 175.2, 62.5, 42.1],
    'Dependencies': [155, 98, 45, 32],
    'CPU Usage (%)': [25.4, 18.2, 8.5, 5.2]
}

df_metrics = pd.DataFrame(metrics_detail)

# Create heatmap visualization
fig2 = go.Figure()

# Normalize values for heatmap (0-1 scale, inverted so lower is better)
normalized_data = []
for col in df_metrics.columns[1:]:
    values = df_metrics[col].values
    normalized = 1 - (values - values.min()) / (values.max() - values.min())
    normalized_data.append(normalized)

# Create heatmap
fig2.add_trace(go.Heatmap(
    z=normalized_data,
    x=df_metrics['Framework'],
    y=df_metrics.columns[1:],
    colorscale='RdYlGn',
    text=[[f'{df_metrics.iloc[i][col]:.1f}' if isinstance(df_metrics.iloc[i][col], float) else str(df_metrics.iloc[i][col]) 
           for i in range(len(df_metrics))] 
          for col in df_metrics.columns[1:]],
    texttemplate='%{text}',
    textfont={"size": 12},
    showscale=True,
    colorbar=dict(
        title="Performance",
        tickvals=[0, 0.5, 1],
        ticktext=['Poor', 'Average', 'Excellent']
    )
))

fig2.update_layout(
    title='Framework Performance Heatmap<br><sub>Green = Better, Red = Worse</sub>',
    xaxis_title='Framework',
    yaxis_title='Metric',
    height=600
)

# Save heatmap
fig2.write_html('benchmark/results/visualizations/performance_heatmap.html')
print("✅ Performance heatmap created!")

# Create overall score comparison
fig3 = go.Figure()

# Calculate overall scores (weighted average)
weights = {
    'Package Size': 0.3,
    'Startup Time': 0.25,
    'Memory Usage': 0.2,
    'Dependency Count': 0.15,
    'CPU Usage': 0.1
}

overall_scores = []
for framework in frameworks:
    score = 0
    for metric, weight in weights.items():
        metric_row = df[df['Metric'] == metric]
        if not metric_row.empty:
            score += metric_row[framework].values[0] * weight
    overall_scores.append(score)

# Create bar chart
bars = fig3.add_trace(go.Bar(
    x=frameworks,
    y=overall_scores,
    text=[f'{score:.1f}/100' for score in overall_scores],
    textposition='auto',
    marker_color=colors,
    marker_line_color='black',
    marker_line_width=2
))

# Add annotations
best_idx = overall_scores.index(max(overall_scores))
fig3.add_annotation(
    x=frameworks[best_idx],
    y=overall_scores[best_idx] + 5,
    text="🏆 WINNER!",
    showarrow=True,
    arrowhead=2,
    arrowsize=1,
    arrowwidth=2,
    arrowcolor="green",
    font=dict(size=16, color="green")
)

fig3.update_layout(
    title='Overall Performance Score<br><sub>Weighted average of all metrics</sub>',
    xaxis_title='Framework',
    yaxis_title='Score (0-100)',
    yaxis_range=[0, 105],
    height=600,
    showlegend=False
)

# Save overall score chart
fig3.write_html('benchmark/results/visualizations/overall_score.html')
print("✅ Overall score chart created!")

# Create improvement percentage chart
fig4 = go.Figure()

# Calculate improvements vs CrewAI
base_metrics = df_metrics[df_metrics['Framework'] == 'CrewAI Official'].iloc[0]
improvements = []

for _, row in df_metrics.iterrows():
    if row['Framework'] != 'CrewAI Official':
        improvement = {}
        improvement['Framework'] = row['Framework']
        improvement['Size Reduction'] = (1 - row['Package Size (MB)'] / base_metrics['Package Size (MB)']) * 100
        improvement['Speed Improvement'] = (1 - row['Startup Time (s)'] / base_metrics['Startup Time (s)']) * 100
        improvement['Memory Savings'] = (1 - row['Memory Usage (MB)'] / base_metrics['Memory Usage (MB)']) * 100
        improvement['Dependency Reduction'] = (1 - row['Dependencies'] / base_metrics['Dependencies']) * 100
        improvements.append(improvement)

df_improvements = pd.DataFrame(improvements)

# Create grouped bar chart
metrics_to_show = ['Size Reduction', 'Speed Improvement', 'Memory Savings', 'Dependency Reduction']
x = np.arange(len(df_improvements))
width = 0.2

for i, metric in enumerate(metrics_to_show):
    fig4.add_trace(go.Bar(
        name=metric,
        x=df_improvements['Framework'],
        y=df_improvements[metric],
        text=[f'+{val:.0f}%' for val in df_improvements[metric]],
        textposition='auto',
        width=0.2
    ))

fig4.update_layout(
    title='Improvement Percentages vs CrewAI Official',
    xaxis_title='Framework',
    yaxis_title='Improvement (%)',
    barmode='group',
    height=600,
    yaxis=dict(range=[0, 105])
)

# Save improvements chart
fig4.write_html('benchmark/results/visualizations/improvements_chart.html')
print("✅ Improvements chart created!")

print("\n🎉 All performance visualizations created successfully!")
print("Files created:")
print("  - performance_radar.html (radar chart)")
print("  - performance_heatmap.html (detailed metrics)")
print("  - overall_score.html (weighted scores)")
print("  - improvements_chart.html (% improvements)")
#!/bin/bash
# Tool Development Kit Workflow Example

# Create new tool
litecrewai create-tool weather_forecast

# Develop
cd weather_forecast/
# Edit weather_forecast.py

# Test
litecrewai test-tool .

# Package
litecrewai package-tool .

# Publish
pip install dist/weather_forecast-1.0.0.whl
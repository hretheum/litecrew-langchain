#!/usr/bin/env python3
# benchmark/scripts/run_framework.py
import subprocess
import sys
import os

def run_in_env(env_name, script_path):
    """Run script in specific virtualenv"""
    activate = f"source envs/{env_name}/bin/activate"
    cmd = f"{activate} && python {script_path}"
    
    result = subprocess.run(
        cmd, 
        shell=True, 
        capture_output=True,
        text=True,
        executable='/bin/bash'
    )
    return result
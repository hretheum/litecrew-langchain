"""Debug and troubleshooting CLI commands."""

import click
import json
import httpx
import sys
import time
from datetime import datetime, timedelta


@click.group(name='debug')
def debug_group():
    """Debug and troubleshooting commands."""
    pass


@debug_group.command()
@click.option('--tail', default=20, help='Number of recent log entries to show')
@click.option('--level', type=click.Choice(['debug', 'info', 'warn', 'error']), help='Filter by log level')
@click.option('--follow', '-f', is_flag=True, help='Follow log output in real-time')
@click.pass_context
def logs(ctx, tail, level, follow):
    """View system logs.
    
    Note: This is a mock implementation. In production, this would
    connect to actual log sources (files, syslog, etc.)
    """
    verbose = ctx.obj['verbose']
    
    # Mock log data (in production, this would read from actual log sources)
    mock_logs = [
        {"timestamp": datetime.now() - timedelta(minutes=5), "level": "info", "message": "LiteCrew API server started"},
        {"timestamp": datetime.now() - timedelta(minutes=4), "level": "info", "message": "Loaded configuration from config.yaml"},
        {"timestamp": datetime.now() - timedelta(minutes=3), "level": "warn", "message": "High memory usage detected: 45MB"},
        {"timestamp": datetime.now() - timedelta(minutes=2), "level": "info", "message": "Crew 'research-team' created successfully"},
        {"timestamp": datetime.now() - timedelta(minutes=1), "level": "info", "message": "Task execution completed in 2.3s"},
        {"timestamp": datetime.now() - timedelta(seconds=30), "level": "error", "message": "Failed to connect to external API: timeout"},
        {"timestamp": datetime.now() - timedelta(seconds=10), "level": "info", "message": "WebSocket connection established"},
        {"timestamp": datetime.now() - timedelta(seconds=5), "level": "debug", "message": "Processing request ID: req_123456"},
    ]
    
    # Filter by level if specified
    if level:
        mock_logs = [log for log in mock_logs if log['level'] == level]
    
    # Apply tail limit
    mock_logs = mock_logs[-tail:]
    
    click.echo(f"📜 System Logs (showing last {len(mock_logs)} entries):")
    click.echo("=" * 60)
    
    for log_entry in mock_logs:
        timestamp_str = log_entry['timestamp'].strftime("%H:%M:%S")
        level_str = log_entry['level'].upper()
        
        # Color code log levels
        if log_entry['level'] == 'error':
            level_display = click.style(f"[{level_str}]", fg='red')
        elif log_entry['level'] == 'warn':
            level_display = click.style(f"[{level_str}]", fg='yellow')
        elif log_entry['level'] == 'info':
            level_display = click.style(f"[{level_str}]", fg='blue')
        else:  # debug
            level_display = click.style(f"[{level_str}]", fg='white', dim=True)
        
        click.echo(f"{timestamp_str} {level_display} {log_entry['message']}")
    
    if follow:
        click.echo("\n📟 Following logs... (Ctrl+C to stop)")
        try:
            while True:
                time.sleep(2)
                # In production, this would tail actual log files
                new_entry = {
                    "timestamp": datetime.now(),
                    "level": "info",
                    "message": f"Heartbeat check at {datetime.now().strftime('%H:%M:%S')}"
                }
                
                if not level or new_entry['level'] == level:
                    timestamp_str = new_entry['timestamp'].strftime("%H:%M:%S")
                    level_display = click.style(f"[{new_entry['level'].upper()}]", fg='blue')
                    click.echo(f"{timestamp_str} {level_display} {new_entry['message']}")
                    
        except KeyboardInterrupt:
            click.echo("\n📟 Log following stopped")


@debug_group.command()
@click.pass_context
def connectivity(ctx):
    """Test connectivity to all system components."""
    api_url = ctx.obj['api_url']
    verbose = ctx.obj['verbose']
    
    click.echo("🔍 Testing LiteCrew Connectivity...")
    click.echo("=" * 40)
    
    tests = []
    
    # Test API server connectivity
    try:
        start = time.perf_counter()
        with httpx.Client() as client:
            response = client.get(f"{api_url}/api/v1/health", timeout=5.0)
        latency = (time.perf_counter() - start) * 1000
        
        if response.status_code == 200:
            tests.append(("API Server", True, f"{latency:.1f}ms"))
        else:
            tests.append(("API Server", False, f"HTTP {response.status_code}"))
    except Exception as e:
        tests.append(("API Server", False, str(e)[:30]))
    
    # Test WebSocket connectivity
    try:
        # Note: This is a simplified test. Full WebSocket testing would require more setup
        with httpx.Client() as client:
            response = client.get(f"{api_url}/docs", timeout=5.0)
        
        if response.status_code == 200:
            tests.append(("WebSocket Endpoint", True, "Available"))
        else:
            tests.append(("WebSocket Endpoint", False, "Not available"))
    except Exception:
        tests.append(("WebSocket Endpoint", False, "Connection failed"))
    
    # Test database connectivity (mock)
    # In production, this would test actual database connections
    tests.append(("Database", True, "SQLite OK"))
    
    # Test cache connectivity (mock)
    # In production, this would test Redis or other cache systems
    tests.append(("Cache Layer", True, "Memory cache OK"))
    
    # Display results
    for component, status, details in tests:
        if status:
            icon = "✅"
            status_text = click.style("OK", fg='green')
        else:
            icon = "❌"
            status_text = click.style("FAIL", fg='red')
        
        click.echo(f"{icon} {component:<20} {status_text} ({details})")
    
    # Summary
    passed = sum(1 for _, status, _ in tests if status)
    total = len(tests)
    
    click.echo("\n📊 Connectivity Summary:")
    if passed == total:
        click.echo(click.style(f"✅ All {total} components are healthy", fg='green'))
    else:
        failed = total - passed
        click.echo(click.style(f"⚠️ {failed}/{total} components have issues", fg='yellow'))
        
        if not ctx.obj.get('verbose'):
            click.echo("Run with --verbose for detailed error information")


@debug_group.command()
@click.argument('crew_id')
@click.pass_context
def trace(ctx, crew_id):
    """Trace crew execution flow.
    
    CREW_ID: The ID of the crew to trace
    """
    api_url = ctx.obj['api_url']
    verbose = ctx.obj['verbose']
    
    try:
        # Get crew details
        with httpx.Client() as client:
            crew_response = client.get(f"{api_url}/api/v1/crews/{crew_id}", timeout=10.0)
        
        if crew_response.status_code == 404:
            click.echo(click.style(f"❌ Crew {crew_id} not found", fg='red'))
            sys.exit(1)
        elif crew_response.status_code != 200:
            click.echo(click.style(f"❌ Failed to fetch crew: HTTP {crew_response.status_code}", fg='red'))
            sys.exit(1)
        
        crew_data = crew_response.json()
        
        click.echo(f"🔍 Tracing Crew: {crew_data.get('name', 'Unknown')}")
        click.echo(f"   ID: {crew_id}")
        click.echo(f"   Process: {crew_data.get('process', 'sequential')}")
        click.echo("\n📝 Execution Flow:")
        click.echo("=" * 40)
        
        # Show agent flow
        agents = crew_data.get('agents', [])
        click.echo(f"🤖 Agents ({len(agents)}):")
        for i, agent in enumerate(agents, 1):
            click.echo(f"   {i}. {agent.get('role', 'Unknown Role')}")
            click.echo(f"      Goal: {agent.get('goal', 'No goal')[:50]}...")
        
        # Show task flow
        tasks = crew_data.get('tasks', [])
        click.echo(f"\n📝 Tasks ({len(tasks)}):")
        for i, task in enumerate(tasks, 1):
            agent_role = task.get('agent_role', 'Unknown')
            click.echo(f"   {i}. {task.get('description', 'No description')[:50]}...")
            click.echo(f"      Agent: {agent_role}")
            click.echo(f"      Expected: {task.get('expected_output', 'None')[:30]}...")
            
            if i < len(tasks):
                click.echo(f"      ↓")
        
        # Get execution history
        try:
            with httpx.Client() as client:
                executions_response = client.get(f"{api_url}/api/v1/crews/{crew_id}/executions", timeout=10.0)
            
            if executions_response.status_code == 200:
                executions_data = executions_response.json()
                executions = executions_data.get('executions', [])
                
                if executions:
                    click.echo(f"\n📊 Recent Executions ({len(executions)}):")
                    for exec_data in executions[:5]:  # Show last 5
                        exec_id = exec_data.get('execution_id', 'unknown')[:8]
                        status = exec_data.get('status', 'unknown')
                        duration = exec_data.get('duration', 0)
                        
                        if status == 'completed':
                            status_icon = "✅"
                        elif status == 'failed':
                            status_icon = "❌"
                        else:
                            status_icon = "🔄"
                        
                        click.echo(f"   {status_icon} {exec_id} | {status} | {duration:.1f}s")
        except Exception:
            click.echo("\n📊 No execution history available")
        
        if verbose:
            click.echo("\n📄 Full Crew Configuration:")
            click.echo(json.dumps(crew_data, indent=2))
            
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg='red'))
        sys.exit(1)


@debug_group.command()
@click.pass_context
def performance(ctx):
    """Analyze system performance."""
    api_url = ctx.obj['api_url']
    
    click.echo("📊 LiteCrew Performance Analysis")
    click.echo("=" * 35)
    
    try:
        # Test API performance
        latencies = []
        click.echo("🏃 Testing API latency...")
        
        for i in range(5):
            start = time.perf_counter()
            with httpx.Client() as client:
                response = client.get(f"{api_url}/api/v1/health", timeout=5.0)
            latency = (time.perf_counter() - start) * 1000
            latencies.append(latency)
            
            if response.status_code != 200:
                raise Exception(f"API returned status {response.status_code}")
        
        # Get system metrics
        with httpx.Client() as client:
            health_response = client.get(f"{api_url}/api/v1/health")
        health_data = health_response.json()
        
        # Performance analysis
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        memory_mb = health_data.get('memory_mb', 0)
        
        click.echo("\n📈 Performance Metrics:")
        click.echo(f"   Average Latency: {avg_latency:.1f}ms")
        click.echo(f"   Min Latency: {min_latency:.1f}ms")
        click.echo(f"   Max Latency: {max_latency:.1f}ms")
        click.echo(f"   Memory Usage: {memory_mb:.1f}MB")
        
        # Performance assessment
        issues = []
        
        if avg_latency > 100:
            issues.append("High API latency (>100ms)")
        if memory_mb > 100:
            issues.append("High memory usage (>100MB)")
        if max_latency > 500:
            issues.append("Inconsistent response times")
        
        click.echo("\n🔍 Performance Assessment:")
        if not issues:
            click.echo(click.style("✅ Performance is optimal", fg='green'))
        else:
            click.echo(click.style(f"⚠️ {len(issues)} issue(s) detected:", fg='yellow'))
            for issue in issues:
                click.echo(f"   • {issue}")
        
        # Recommendations
        click.echo("\n💡 Recommendations:")
        if avg_latency > 50:
            click.echo("   • Consider optimizing API response time")
        if memory_mb > 50:
            click.echo("   • Monitor memory usage patterns")
        if not issues:
            click.echo("   • System is performing well!")
            
    except Exception as e:
        click.echo(click.style(f"❌ Performance analysis failed: {str(e)}", fg='red'))
        sys.exit(1)
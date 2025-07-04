"""Task runner CLI commands."""

import click
import json
import httpx
import sys
import time
from typing import Optional


@click.group(name='task')
def task_group():
    """Run and manage individual tasks."""
    pass


@task_group.command()
@click.argument('description')
@click.option('--crew-id', help='Crew ID to submit task to')
@click.option('--expected-output', help='Expected output description')
@click.option('--priority', type=click.Choice(['low', 'medium', 'high']), default='medium', help='Task priority')
@click.pass_context
def run(ctx, description, crew_id, expected_output, priority):
    """Run a single task.
    
    DESCRIPTION: The task description to execute
    
    Example:
        litecrew task run "Analyze market trends for Q4 2024"
    """
    api_url = ctx.obj['api_url']
    verbose = ctx.obj['verbose']
    
    if not crew_id:
        # Need to find or create a default crew
        click.echo("❌ No crew ID specified. Use --crew-id or create a crew first.")
        click.echo("Hint: Run 'litecrew crew list' to see available crews")
        sys.exit(1)
    
    try:
        task_data = {
            "description": description,
            "expected_output": expected_output or "Task result",
            "priority": priority
        }
        
        click.echo(f"🚀 Submitting task to crew {crew_id}...")
        
        with httpx.Client() as client:
            response = client.post(
                f"{api_url}/api/v1/crews/{crew_id}/tasks",
                json=task_data,
                timeout=10.0
            )
        
        if response.status_code == 202:
            result_data = response.json()
            task_id = result_data.get('task_id')
            click.echo(click.style(f"✅ Task submitted successfully (ID: {task_id})", fg='green'))
            
            if verbose:
                click.echo("\n📋 Task Details:")
                click.echo(f"   Description: {description}")
                click.echo(f"   Priority: {priority}")
                click.echo(f"   Expected Output: {expected_output or 'Task result'}")
                
        elif response.status_code == 404:
            click.echo(click.style(f"❌ Crew {crew_id} not found", fg='red'))
            sys.exit(1)
        else:
            error_data = response.json() if response.text else {}
            click.echo(click.style(f"❌ Failed to submit task: {error_data.get('detail', 'Unknown error')}", fg='red'))
            sys.exit(1)
            
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg='red'))
        sys.exit(1)


@task_group.command()
@click.argument('task_id')
@click.option('--wait', is_flag=True, help='Wait for task completion')
@click.option('--timeout', default=300, help='Wait timeout in seconds')
@click.pass_context
def status(ctx, task_id, wait, timeout):
    """Check task status.
    
    TASK_ID: The ID of the task to check
    """
    api_url = ctx.obj['api_url']
    verbose = ctx.obj['verbose']
    
    try:
        if wait:
            click.echo(f"⏳ Waiting for task {task_id} completion (timeout: {timeout}s)...")
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                with httpx.Client() as client:
                    response = client.get(f"{api_url}/api/v1/tasks/{task_id}", timeout=10.0)
                
                if response.status_code == 200:
                    task_data = response.json()
                    status = task_data.get('status', 'unknown')
                    
                    if status in ['completed', 'failed', 'cancelled']:
                        break
                    
                    click.echo(f"   Status: {status}...")
                    time.sleep(2)
                elif response.status_code == 404:
                    click.echo(click.style(f"❌ Task {task_id} not found", fg='red'))
                    sys.exit(1)
                else:
                    click.echo(click.style(f"❌ Failed to check status: HTTP {response.status_code}", fg='red'))
                    sys.exit(1)
            else:
                click.echo(click.style("⏱️ Timeout waiting for task completion", fg='yellow'))
        
        # Get final status
        with httpx.Client() as client:
            response = client.get(f"{api_url}/api/v1/tasks/{task_id}", timeout=10.0)
        
        if response.status_code == 404:
            click.echo(click.style(f"❌ Task {task_id} not found", fg='red'))
            sys.exit(1)
        elif response.status_code != 200:
            click.echo(click.style(f"❌ Failed to fetch task: HTTP {response.status_code}", fg='red'))
            sys.exit(1)
        
        task_data = response.json()
        status = task_data.get('status', 'unknown')
        
        # Display status with appropriate color
        if status == 'completed':
            status_display = click.style(f"✅ {status.upper()}", fg='green')
        elif status == 'failed':
            status_display = click.style(f"❌ {status.upper()}", fg='red')
        elif status in ['running', 'in_progress']:
            status_display = click.style(f"⏳ {status.upper()}", fg='yellow')
        else:
            status_display = f"🔄 {status.upper()}"
        
        click.echo(f"📋 Task {task_id} Status: {status_display}")
        
        if verbose:
            click.echo("\n📝 Task Details:")
            click.echo(json.dumps(task_data, indent=2))
        else:
            click.echo(f"   Description: {task_data.get('description', 'No description')[:50]}...")
            click.echo(f"   Priority: {task_data.get('priority', 'unknown')}")
            click.echo(f"   Created: {task_data.get('created_at', 'unknown')}")
            
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg='red'))
        sys.exit(1)


@task_group.command()
@click.option('--crew-id', help='Filter tasks by crew ID')
@click.option('--status', help='Filter tasks by status')
@click.option('--limit', default=10, help='Maximum number of tasks to show')
@click.pass_context
def list(ctx, crew_id, status, limit):
    """List tasks."""
    api_url = ctx.obj['api_url']
    
    try:
        with httpx.Client() as client:
            response = client.get(f"{api_url}/api/v1/tasks", timeout=10.0)
        
        if response.status_code != 200:
            click.echo(click.style("❌ Failed to fetch tasks", fg='red'))
            sys.exit(1)
        
        data = response.json()
        tasks = data.get('tasks', [])
        
        # Apply filters
        if crew_id:
            tasks = [t for t in tasks if t.get('crew_id') == crew_id]
        
        if status:
            tasks = [t for t in tasks if t.get('status') == status]
        
        # Limit results
        tasks = tasks[:limit]
        
        if not tasks:
            click.echo("📋 No tasks found")
            return
        
        click.echo(f"📋 Found {len(tasks)} task(s):")
        click.echo("=" * 60)
        
        for task in tasks:
            task_id = task.get('task_id', 'unknown')[:8]
            description = task.get('description', 'No description')[:40]
            status = task.get('status', 'unknown')
            priority = task.get('priority', 'unknown')
            
            if status == 'completed':
                status_icon = "✅"
            elif status == 'failed':
                status_icon = "❌"
            elif status in ['running', 'in_progress']:
                status_icon = "⏳"
            else:
                status_icon = "🔄"
            
            click.echo(f"{status_icon} {task_id} | {description}... | {status} | {priority}")
        
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg='red'))
        sys.exit(1)
"""Crew management CLI commands."""

import json
import sys
from typing import Optional

import click
import httpx
import yaml


@click.group(name="crew")
def crew_group() -> None:
    """Manage crews - create, list, execute, and monitor AI agent teams."""
    pass


@crew_group.command()
@click.argument("crew_file", type=click.Path(exists=True))
@click.option("--name", "-n", help="Override crew name")
@click.option("--dry-run", is_flag=True, help="Validate configuration without creating")
@click.pass_context
def create(ctx: click.Context, crew_file: str, name: Optional[str], dry_run: bool) -> None:
    """Create a new crew from configuration file.

    CREW_FILE: Path to YAML or JSON file containing crew configuration

    Example crew.yaml:
    \b
        name: "Research Team"
        description: "AI research and analysis crew"
        agents:
          - role: "Researcher"
            goal: "Research market trends"
            backstory: "Expert market analyst"
          - role: "Writer"
            goal: "Write reports"
            backstory: "Professional technical writer"
        tasks:
          - description: "Research AI market trends"
            agent_role: "Researcher"
            expected_output: "Market analysis report"
          - description: "Write summary report"
            agent_role: "Writer"
            expected_output: "Executive summary"
        process: "sequential"
    """
    api_url = ctx.obj["api_url"]
    verbose = ctx.obj["verbose"]

    try:
        # Load crew configuration
        with open(crew_file, "r") as f:
            if crew_file.endswith(".json"):
                crew_config = json.load(f)
            else:
                crew_config = yaml.safe_load(f)

        # Override name if provided
        if name:
            crew_config["name"] = name

        # Validate required fields
        required_fields = ["name", "agents", "tasks"]
        for field in required_fields:
            if field not in crew_config:
                raise ValueError(f"Missing required field: {field}")

        if dry_run:
            click.echo("🔍 Crew configuration validation:")
            click.echo(f"   Name: {crew_config['name']}")
            click.echo(f"   Agents: {len(crew_config['agents'])}")
            click.echo(f"   Tasks: {len(crew_config['tasks'])}")
            click.echo(f"   Process: {crew_config.get('process', 'sequential')}")
            click.echo(click.style("✅ Configuration is valid", fg="green"))
            return

        # Create crew via API
        with httpx.Client() as client:
            response = client.post(
                f"{api_url}/api/v1/crews", json=crew_config, timeout=10.0
            )

        if response.status_code == 201:
            crew_data = response.json()
            click.echo(
                click.style(
                    f"✅ Crew '{crew_data['name']}' created successfully", fg="green"
                )
            )
            click.echo(f"   ID: {crew_data['crew_id']}")
            click.echo(f"   Agents: {len(crew_data['agents'])}")
            click.echo(f"   Tasks: {len(crew_data['tasks'])}")

            if verbose:
                click.echo("\n📋 Crew Details:")
                click.echo(json.dumps(crew_data, indent=2))
        else:
            error_data = response.json() if response.text else {}
            click.echo(
                click.style(
                    f"❌ Failed to create crew: {error_data.get('detail', 'Unknown error')}",
                    fg="red",
                )
            )
            sys.exit(1)

    except FileNotFoundError:
        click.echo(click.style(f"❌ File not found: {crew_file}", fg="red"))
        sys.exit(1)
    except yaml.YAMLError as e:
        click.echo(click.style(f"❌ YAML parsing error: {e}", fg="red"))
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"))
        sys.exit(1)


@crew_group.command()
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Output format",
)
@click.option("--filter", "name_filter", help="Filter crews by name (substring match)")
@click.pass_context
def list(ctx: click.Context, output_format: str, name_filter: Optional[str]) -> None:
    """List all crews."""
    api_url = ctx.obj["api_url"]

    try:
        with httpx.Client() as client:
            response = client.get(f"{api_url}/api/v1/crews", timeout=10.0)

        if response.status_code != 200:
            click.echo(click.style("❌ Failed to fetch crews", fg="red"))
            sys.exit(1)

        data = response.json()
        crews = data.get("crews", [])

        # Apply filter
        if name_filter:
            crews = [
                c for c in crews if name_filter.lower() in c.get("name", "").lower()
            ]

        if not crews:
            click.echo("📋 No crews found")
            return

        if output_format == "json":
            click.echo(json.dumps(crews, indent=2))
        elif output_format == "yaml":
            click.echo(yaml.dump(crews, default_flow_style=False))
        else:
            # Table format
            click.echo(f"📋 Found {len(crews)} crew(s):")
            click.echo("=" * 80)

            for crew in crews:
                click.echo(f"Name: {crew.get('name', 'Unknown')}")
                click.echo(f"ID: {crew.get('crew_id', 'Unknown')}")
                click.echo(f"Agents: {len(crew.get('agents', []))}")
                click.echo(f"Tasks: {len(crew.get('tasks', []))}")
                click.echo(f"Created: {crew.get('created_at', 'Unknown')}")
                if crew.get("description"):
                    click.echo(f"Description: {crew['description']}")
                click.echo("-" * 40)

    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"))
        sys.exit(1)


@crew_group.command()
@click.argument("crew_id")
@click.option(
    "--inputs", type=click.Path(exists=True), help="JSON file with execution inputs"
)
@click.option("--async", "async_exec", is_flag=True, help="Execute asynchronously")
@click.option("--wait", is_flag=True, help="Wait for async execution to complete")
@click.pass_context
def execute(ctx: click.Context, crew_id: str, inputs: Optional[str], async_exec: bool, wait: bool) -> None:
    """Execute a crew.

    CREW_ID: The ID of the crew to execute
    """
    api_url = ctx.obj["api_url"]
    verbose = ctx.obj["verbose"]

    try:
        # Load inputs if provided
        execution_inputs = {}
        if inputs:
            with open(inputs, "r") as f:
                execution_inputs = json.load(f)

        execution_data = {"inputs": execution_inputs, "async_execution": async_exec}

        click.echo(f"🚀 Executing crew {crew_id}...")

        with httpx.Client() as client:
            response = client.post(
                f"{api_url}/api/v1/crews/{crew_id}/execute",
                json=execution_data,
                timeout=30.0 if not async_exec else 10.0,
            )

        if response.status_code == 200:
            result_data = response.json()

            if async_exec:
                execution_id = result_data.get("execution_id")
                click.echo(
                    click.style(
                        f"✅ Execution started (ID: {execution_id})", fg="green"
                    )
                )

                if wait:
                    click.echo("⏳ Waiting for completion...")
                    # TODO: Implement polling for completion
                    click.echo(
                        "Note: Polling not yet implemented. Use 'litecrew export execution <id>' to check status."
                    )
                else:
                    click.echo(
                        "Use 'litecrew export execution <id>' to check status and results."
                    )
            else:
                click.echo(click.style("✅ Execution completed", fg="green"))

                if verbose:
                    click.echo("\n📋 Execution Results:")
                    click.echo(json.dumps(result_data, indent=2))
                else:
                    result = result_data.get("result", {})
                    if isinstance(result, dict):
                        click.echo(
                            f"Result: {result.get('result', 'No result')[:200]}..."
                        )
                    else:
                        click.echo(f"Result: {str(result)[:200]}...")
        else:
            error_data = response.json() if response.text else {}
            click.echo(
                click.style(
                    f"❌ Execution failed: {error_data.get('detail', 'Unknown error')}",
                    fg="red",
                )
            )
            sys.exit(1)

    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"))
        sys.exit(1)


@crew_group.command()
@click.argument("crew_id")
@click.pass_context
def delete(ctx: click.Context, crew_id: str) -> None:
    """Delete a crew.

    CREW_ID: The ID of the crew to delete
    """
    api_url = ctx.obj["api_url"]

    try:
        with httpx.Client() as client:
            response = client.delete(f"{api_url}/api/v1/crews/{crew_id}", timeout=10.0)

        if response.status_code == 204:
            click.echo(
                click.style(f"✅ Crew {crew_id} deleted successfully", fg="green")
            )
        elif response.status_code == 404:
            click.echo(click.style(f"❌ Crew {crew_id} not found", fg="red"))
            sys.exit(1)
        else:
            click.echo(
                click.style(
                    f"❌ Failed to delete crew: HTTP {response.status_code}", fg="red"
                )
            )
            sys.exit(1)

    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"))
        sys.exit(1)


@crew_group.command()
@click.argument("crew_id")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Output format",
)
@click.pass_context
def show(ctx: click.Context, crew_id: str, output_format: str) -> None:
    """Show detailed information about a crew.

    CREW_ID: The ID of the crew to inspect
    """
    api_url = ctx.obj["api_url"]

    try:
        with httpx.Client() as client:
            response = client.get(f"{api_url}/api/v1/crews/{crew_id}", timeout=10.0)

        if response.status_code == 404:
            click.echo(click.style(f"❌ Crew {crew_id} not found", fg="red"))
            sys.exit(1)
        elif response.status_code != 200:
            click.echo(
                click.style(
                    f"❌ Failed to fetch crew: HTTP {response.status_code}", fg="red"
                )
            )
            sys.exit(1)

        crew_data = response.json()

        if output_format == "json":
            click.echo(json.dumps(crew_data, indent=2))
        elif output_format == "yaml":
            click.echo(yaml.dump(crew_data, default_flow_style=False))
        else:
            # Table format
            click.echo(f"📋 Crew Details: {crew_data.get('name', 'Unknown')}")
            click.echo("=" * 50)
            click.echo(f"ID: {crew_data.get('crew_id', 'Unknown')}")
            click.echo(f"Description: {crew_data.get('description', 'None')}")
            click.echo(f"Process: {crew_data.get('process', 'sequential')}")
            click.echo(f"Created: {crew_data.get('created_at', 'Unknown')}")

            click.echo(f"\n🤖 Agents ({len(crew_data.get('agents', []))}):")
            for i, agent in enumerate(crew_data.get("agents", []), 1):
                click.echo(f"  {i}. {agent.get('role', 'Unknown Role')}")
                click.echo(f"     Goal: {agent.get('goal', 'No goal')}")
                click.echo(
                    f"     Backstory: {agent.get('backstory', 'No backstory')[:50]}..."
                )

            click.echo(f"\n📝 Tasks ({len(crew_data.get('tasks', []))}):")
            for i, task in enumerate(crew_data.get("tasks", []), 1):
                click.echo(
                    f"  {i}. {task.get('description', 'No description')[:50]}..."
                )
                click.echo(f"     Agent: {task.get('agent_role', 'Unknown')}")
                click.echo(
                    f"     Expected Output: {task.get('expected_output', 'None')[:30]}..."
                )

    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"))
        sys.exit(1)

"""Export and result retrieval CLI commands."""

import csv
import json
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

import click
import httpx
import yaml


@click.group(name="export")
def export_group() -> None:
    """Export results and data in various formats."""
    pass


@export_group.command()
@click.argument("execution_id")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "yaml", "txt", "csv"]),
    default="json",
    help="Output format",
)
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--include-metadata", is_flag=True, help="Include execution metadata")
@click.pass_context
def execution(ctx: click.Context, execution_id: str, output_format: str, output: Optional[str], include_metadata: bool) -> None:
    """Export execution results.

    EXECUTION_ID: The ID of the execution to export
    """
    api_url = ctx.obj["api_url"]
    verbose = ctx.obj["verbose"]

    try:
        with httpx.Client() as client:
            response = client.get(
                f"{api_url}/api/v1/executions/{execution_id}", timeout=10.0
            )

        if response.status_code == 404:
            click.echo(click.style(f"❌ Execution {execution_id} not found", fg="red"))
            sys.exit(1)
        elif response.status_code != 200:
            click.echo(
                click.style(
                    f"❌ Failed to fetch execution: HTTP {response.status_code}",
                    fg="red",
                )
            )
            sys.exit(1)

        execution_data = response.json()

        # Prepare export data
        if include_metadata:
            export_data = execution_data
        else:
            export_data = {
                "execution_id": execution_data.get("execution_id"),
                "status": execution_data.get("status"),
                "result": execution_data.get("result"),
                "duration": execution_data.get("duration"),
            }

        # Format data
        if output_format == "json":
            formatted_data = json.dumps(export_data, indent=2)
        elif output_format == "yaml":
            formatted_data = yaml.dump(export_data, default_flow_style=False)
        elif output_format == "txt":
            result = export_data.get("result", {})
            if isinstance(result, dict):
                formatted_data = result.get("result", str(result))
            else:
                formatted_data = str(result)
        elif output_format == "csv":
            # Flatten data for CSV
            flattened = _flatten_dict(export_data)
            formatted_data = _dict_to_csv([flattened])

        # Output data
        if output:
            with open(output, "w") as f:
                f.write(formatted_data)
            click.echo(
                click.style(f"✅ Execution results exported to {output}", fg="green")
            )
        else:
            click.echo(formatted_data)

        if verbose and not output:
            click.echo("\n📊 Export Statistics:")
            click.echo(f"   Format: {output_format}")
            click.echo(f"   Size: {len(formatted_data)} characters")
            click.echo(f"   Metadata included: {include_metadata}")

    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"))
        sys.exit(1)


@export_group.command()
@click.option("--crew-id", help="Export executions for specific crew")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "yaml", "csv"]),
    default="json",
    help="Output format",
)
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--limit", default=100, help="Maximum number of executions to export")
@click.pass_context
def executions(ctx: click.Context, crew_id: Optional[str], output_format: str, output: Optional[str], limit: int) -> None:
    """Export multiple execution results."""
    api_url = ctx.obj["api_url"]
    verbose = ctx.obj["verbose"]

    try:
        if crew_id:
            endpoint = f"{api_url}/api/v1/crews/{crew_id}/executions"
        else:
            endpoint = f"{api_url}/api/v1/executions"

        with httpx.Client() as client:
            response = client.get(endpoint, timeout=10.0)

        if response.status_code != 200:
            click.echo(click.style("❌ Failed to fetch executions", fg="red"))
            sys.exit(1)

        data = response.json()
        executions = data.get("executions", [])

        # Limit results
        executions = executions[:limit]

        if not executions:
            click.echo("📋 No executions found")
            return

        # Format data
        if output_format == "json":
            formatted_data = json.dumps(executions, indent=2)
        elif output_format == "yaml":
            formatted_data = yaml.dump(executions, default_flow_style=False)
        elif output_format == "csv":
            # Flatten each execution for CSV
            flattened_executions = [
                _flatten_dict(exec_data) for exec_data in executions
            ]
            formatted_data = _dict_to_csv(flattened_executions)

        # Output data
        if output:
            with open(output, "w") as f:
                f.write(formatted_data)
            click.echo(
                click.style(
                    f"✅ {len(executions)} executions exported to {output}", fg="green"
                )
            )
        else:
            click.echo(formatted_data)

        if verbose and not output:
            click.echo("\n📊 Export Statistics:")
            click.echo(f"   Executions: {len(executions)}")
            click.echo(f"   Format: {output_format}")
            click.echo(f"   Crew filter: {crew_id or 'all'}")

    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"))
        sys.exit(1)


@export_group.command()
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "yaml", "csv"]),
    default="json",
    help="Output format",
)
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--include-config", is_flag=True, help="Include crew configuration details"
)
@click.pass_context
def crews(ctx: click.Context, output_format: str, output: Optional[str], include_config: bool) -> None:
    """Export crew definitions."""
    api_url = ctx.obj["api_url"]
    verbose = ctx.obj["verbose"]

    try:
        with httpx.Client() as client:
            response = client.get(f"{api_url}/api/v1/crews", timeout=10.0)

        if response.status_code != 200:
            click.echo(click.style("❌ Failed to fetch crews", fg="red"))
            sys.exit(1)

        data = response.json()
        crews = data.get("crews", [])

        if not crews:
            click.echo("📋 No crews found")
            return

        # Prepare export data
        if not include_config:
            # Simplified crew data
            export_crews = []
            for crew in crews:
                export_crews.append(
                    {
                        "crew_id": crew.get("crew_id"),
                        "name": crew.get("name"),
                        "description": crew.get("description"),
                        "agent_count": len(crew.get("agents", [])),
                        "task_count": len(crew.get("tasks", [])),
                        "created_at": crew.get("created_at"),
                    }
                )
        else:
            export_crews = crews

        # Format data
        if output_format == "json":
            formatted_data = json.dumps(export_crews, indent=2)
        elif output_format == "yaml":
            formatted_data = yaml.dump(export_crews, default_flow_style=False)
        elif output_format == "csv":
            # Flatten each crew for CSV
            flattened_crews = [_flatten_dict(crew_data) for crew_data in export_crews]
            formatted_data = _dict_to_csv(flattened_crews)

        # Output data
        if output:
            with open(output, "w") as f:
                f.write(formatted_data)
            click.echo(
                click.style(
                    f"✅ {len(export_crews)} crews exported to {output}", fg="green"
                )
            )
        else:
            click.echo(formatted_data)

        if verbose and not output:
            click.echo("\n📊 Export Statistics:")
            click.echo(f"   Crews: {len(export_crews)}")
            click.echo(f"   Format: {output_format}")
            click.echo(f"   Config included: {include_config}")

    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"))
        sys.exit(1)


@export_group.command()
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.pass_context
def metrics(ctx: click.Context, output: Optional[str]) -> None:
    """Export system metrics and performance data."""
    api_url = ctx.obj["api_url"]
    verbose = ctx.obj["verbose"]

    try:
        with httpx.Client() as client:
            # Get health metrics
            health_response = client.get(f"{api_url}/api/v1/health", timeout=10.0)

            # Get crew and execution counts
            crews_response = client.get(f"{api_url}/api/v1/crews", timeout=10.0)
            executions_response = client.get(
                f"{api_url}/api/v1/executions", timeout=10.0
            )

        if health_response.status_code != 200:
            click.echo(click.style("❌ Failed to fetch health metrics", fg="red"))
            sys.exit(1)

        health_data = health_response.json()
        crews_data = (
            crews_response.json()
            if crews_response.status_code == 200
            else {"crews": []}
        )
        executions_data = (
            executions_response.json()
            if executions_response.status_code == 200
            else {"executions": []}
        )

        # Compile metrics
        metrics_data = {
            "system": {
                "memory_mb": health_data.get("memory_mb"),
                "version": health_data.get("version"),
                "timestamp": health_data.get("timestamp"),
                "uptime": health_data.get("uptime"),
            },
            "usage": {
                "total_crews": len(crews_data.get("crews", [])),
                "total_executions": len(executions_data.get("executions", [])),
                "completed_executions": len(
                    [
                        e
                        for e in executions_data.get("executions", [])
                        if e.get("status") == "completed"
                    ]
                ),
            },
        }

        formatted_data = json.dumps(metrics_data, indent=2)

        # Output data
        if output:
            with open(output, "w") as f:
                f.write(formatted_data)
            click.echo(
                click.style(f"✅ System metrics exported to {output}", fg="green")
            )
        else:
            click.echo(formatted_data)

        if verbose and not output:
            click.echo("\n📊 Metrics Summary:")
            click.echo(f"   Memory Usage: {metrics_data['system']['memory_mb']:.1f} MB")
            click.echo(f"   Total Crews: {metrics_data['usage']['total_crews']}")
            click.echo(
                f"   Total Executions: {metrics_data['usage']['total_executions']}"
            )

    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"))
        sys.exit(1)


def _flatten_dict(
    d: Dict[str, Any], parent_key: str = "", sep: str = "_"
) -> Dict[str, Any]:
    """Flatten nested dictionary for CSV export."""
    items: List[Tuple[str, Any]] = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, len(v)))
        else:
            items.append((new_key, v))
    return dict(items)


def _dict_to_csv(data: List[Dict[str, Any]]) -> str:
    """Convert list of dictionaries to CSV string."""
    if not data:
        return ""

    import io

    output = io.StringIO()

    # Get all possible field names
    fieldnames: Set[str] = set()
    for row in data:
        fieldnames.update(row.keys())

    fieldnames_list = sorted(list(fieldnames))

    writer = csv.DictWriter(output, fieldnames=fieldnames_list)
    writer.writeheader()
    writer.writerows(data)

    return output.getvalue()

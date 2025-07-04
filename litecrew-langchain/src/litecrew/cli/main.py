"""Main CLI entry point for LiteCrew."""

import json
import sys
import time

import click

from .commands.config import config_group
from .commands.crew import crew_group
from .commands.debug import debug_group
from .commands.export import export_group
from .commands.task import task_group


@click.group()
@click.version_option(version="1.0.0", prog_name="litecrew")
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Configuration file path"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--api-url", default="http://localhost:8000", help="API server URL")
@click.pass_context
def cli(ctx, config, verbose, api_url):
    """🚀 LiteCrew - Lightweight AI Agent Orchestration CLI

    A fast, efficient alternative to CrewAI built on LangChain.

    Examples:
        litecrew crew create my-crew.yaml
        litecrew task run "Analyze market trends"
        litecrew export results --format json
        litecrew debug logs --tail 50
    """
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Store configuration in context
    ctx.obj["verbose"] = verbose
    ctx.obj["api_url"] = api_url
    ctx.obj["config_file"] = config
    ctx.obj["start_time"] = time.perf_counter()

    # Load configuration if provided
    if config:
        try:
            with open(config, "r") as f:
                if config.endswith(".json"):
                    ctx.obj["config"] = json.load(f)
                else:
                    # Assume YAML
                    import yaml

                    ctx.obj["config"] = yaml.safe_load(f)
        except Exception as e:
            if verbose:
                click.echo(f"Warning: Could not load config file: {e}", err=True)
            ctx.obj["config"] = {}
    else:
        ctx.obj["config"] = {}

    if verbose:
        click.echo(f"LiteCrew CLI starting with API URL: {api_url}")


# Add command groups
cli.add_command(crew_group)
cli.add_command(task_group)
cli.add_command(config_group)
cli.add_command(debug_group)
cli.add_command(export_group)


@cli.command()
@click.pass_context
def status(ctx):
    """Show LiteCrew system status."""
    import httpx

    api_url = ctx.obj["api_url"]
    verbose = ctx.obj["verbose"]

    try:
        start = time.perf_counter()

        with httpx.Client() as client:
            # Check API health
            health_response = client.get(f"{api_url}/api/v1/health", timeout=5.0)
            health_data = health_response.json()

            # Get crews
            crews_response = client.get(f"{api_url}/api/v1/crews", timeout=5.0)
            crews_data = crews_response.json()

        duration = (time.perf_counter() - start) * 1000

        # Display status
        click.echo("🚀 LiteCrew System Status")
        click.echo("=" * 25)

        if health_response.status_code == 200:
            click.echo(click.style("✅ API Server: Online", fg="green"))
            click.echo(f"   Memory Usage: {health_data.get('memory_mb', 0):.1f} MB")
            click.echo(f"   Version: {health_data.get('version', 'unknown')}")
        else:
            click.echo(click.style("❌ API Server: Offline", fg="red"))
            return

        if crews_response.status_code == 200:
            crew_count = len(crews_data.get("crews", []))
            click.echo(f"📋 Active Crews: {crew_count}")
        else:
            click.echo("❌ Could not fetch crews")

        click.echo(f"⚡ Response Time: {duration:.1f}ms")

        if verbose:
            click.echo("\n📊 Detailed Metrics:")
            click.echo(f"   API URL: {api_url}")
            click.echo(f"   Timestamp: {health_data.get('timestamp', 'unknown')}")
            click.echo(f"   Uptime: {health_data.get('uptime', 'unknown')}")

    except httpx.ConnectError:
        click.echo(click.style("❌ Cannot connect to API server", fg="red"))
        click.echo(f"   Check if server is running at {api_url}")
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"))
        sys.exit(1)


@cli.command()
@click.pass_context
def benchmark(ctx):
    """Run performance benchmarks."""
    import statistics

    import httpx

    api_url = ctx.obj["api_url"]

    click.echo("🏃 Running LiteCrew Benchmarks...")

    try:
        with httpx.Client() as client:
            # API latency test
            latencies = []
            with click.progressbar(range(10), label="Testing API latency") as bar:
                for _ in bar:
                    start = time.perf_counter()
                    response = client.get(f"{api_url}/api/v1/health", timeout=5.0)
                    latency = (time.perf_counter() - start) * 1000
                    latencies.append(latency)

                    if response.status_code != 200:
                        raise Exception(f"API returned status {response.status_code}")

            # Memory test
            health_response = client.get(f"{api_url}/api/v1/health")
            health_data = health_response.json()
            memory_mb = health_data.get("memory_mb", 0)

        # Results
        click.echo("\n📊 Benchmark Results:")
        click.echo("=" * 20)
        click.echo(f"   Avg Latency: {statistics.mean(latencies):.1f}ms")
        click.echo(f"   Min Latency: {min(latencies):.1f}ms")
        click.echo(f"   Max Latency: {max(latencies):.1f}ms")
        click.echo(f"   Memory Usage: {memory_mb:.1f}MB")

        # Performance assessment
        avg_latency = statistics.mean(latencies)
        if avg_latency < 50:
            click.echo(click.style("   Performance: Excellent ✨", fg="green"))
        elif avg_latency < 100:
            click.echo(click.style("   Performance: Good ✅", fg="yellow"))
        else:
            click.echo(click.style("   Performance: Needs attention ⚠️", fg="red"))

    except Exception as e:
        click.echo(click.style(f"❌ Benchmark failed: {str(e)}", fg="red"))
        sys.exit(1)


if __name__ == "__main__":
    cli()

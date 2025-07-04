"""Configuration management CLI commands."""

import click
import json
import yaml
import os
from pathlib import Path
from typing import Dict, Any


@click.group(name="config")
def config_group():
    """Manage LiteCrew configuration."""
    pass


@config_group.command()
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "yaml"]),
    default="yaml",
    help="Configuration format",
)
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--template",
    type=click.Choice(["basic", "advanced", "production"]),
    default="basic",
    help="Configuration template",
)
def init(output_format, output, template):
    """Initialize a new configuration file."""

    # Configuration templates
    templates = {
        "basic": {
            "api": {"url": "http://localhost:8000", "timeout": 30},
            "logging": {"level": "INFO", "format": "simple"},
            "defaults": {"crew_process": "sequential", "agent_verbose": False},
        },
        "advanced": {
            "api": {
                "url": "http://localhost:8000",
                "timeout": 30,
                "retry_attempts": 3,
                "retry_delay": 1.0,
            },
            "logging": {"level": "DEBUG", "format": "detailed", "file": "litecrew.log"},
            "defaults": {
                "crew_process": "sequential",
                "agent_verbose": True,
                "max_execution_time": 300,
                "memory_limit": "100MB",
            },
            "performance": {
                "cache_enabled": True,
                "parallel_tasks": True,
                "batch_size": 10,
            },
        },
        "production": {
            "api": {
                "url": "${LITECREW_API_URL:-http://localhost:8000}",
                "timeout": 60,
                "retry_attempts": 5,
                "retry_delay": 2.0,
                "auth_token": "${LITECREW_API_TOKEN}",
            },
            "logging": {
                "level": "${LOG_LEVEL:-INFO}",
                "format": "json",
                "file": "/var/log/litecrew/cli.log",
                "rotation": "daily",
            },
            "defaults": {
                "crew_process": "sequential",
                "agent_verbose": False,
                "max_execution_time": 600,
                "memory_limit": "500MB",
            },
            "performance": {
                "cache_enabled": True,
                "parallel_tasks": True,
                "batch_size": 50,
                "connection_pool_size": 20,
            },
            "monitoring": {
                "metrics_enabled": True,
                "health_check_interval": 30,
                "alert_thresholds": {
                    "memory_usage": "80%",
                    "api_latency": "1000ms",
                    "error_rate": "5%",
                },
            },
        },
    }

    config_data = templates[template]

    # Format output
    if output_format == "json":
        formatted_config = json.dumps(config_data, indent=2)
        default_filename = "litecrew.json"
    else:
        formatted_config = yaml.dump(
            config_data, default_flow_style=False, sort_keys=False
        )
        default_filename = "litecrew.yaml"

    # Determine output path
    if output:
        output_path = Path(output)
    else:
        output_path = Path.cwd() / default_filename

    # Check if file exists
    if output_path.exists():
        if not click.confirm(
            f"Configuration file {output_path} already exists. Overwrite?"
        ):
            click.echo("Configuration initialization cancelled.")
            return

    # Write configuration
    try:
        with open(output_path, "w") as f:
            f.write(formatted_config)

        click.echo(
            click.style(f"✅ Configuration initialized: {output_path}", fg="green")
        )
        click.echo(f"   Template: {template}")
        click.echo(f"   Format: {output_format}")

        # Usage hint
        click.echo("\n💡 Usage:")
        click.echo(f"   litecrew --config {output_path} status")

    except Exception as e:
        click.echo(
            click.style(f"❌ Failed to create configuration: {str(e)}", fg="red")
        )


@config_group.command()
@click.argument("config_file", type=click.Path(exists=True))
def validate(config_file):
    """Validate configuration file.

    CONFIG_FILE: Path to configuration file to validate
    """
    try:
        # Load configuration
        with open(config_file, "r") as f:
            if config_file.endswith(".json"):
                config_data = json.load(f)
            else:
                config_data = yaml.safe_load(f)

        click.echo(f"🔍 Validating configuration: {config_file}")
        click.echo("=" * 40)

        # Validation checks
        issues = []
        warnings = []

        # Check required sections
        required_sections = ["api"]
        for section in required_sections:
            if section not in config_data:
                issues.append(f"Missing required section: {section}")

        # Validate API section
        if "api" in config_data:
            api_config = config_data["api"]

            if "url" not in api_config:
                issues.append("Missing API URL in 'api' section")
            else:
                url = api_config["url"]
                if not (url.startswith("http://") or url.startswith("https://")):
                    issues.append(f"Invalid API URL format: {url}")

            if "timeout" in api_config:
                timeout = api_config["timeout"]
                if not isinstance(timeout, (int, float)) or timeout <= 0:
                    issues.append(f"Invalid timeout value: {timeout}")
                elif timeout > 300:
                    warnings.append(f"High timeout value: {timeout}s")

        # Validate logging section
        if "logging" in config_data:
            logging_config = config_data["logging"]

            if "level" in logging_config:
                level = logging_config["level"]
                valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                if level not in valid_levels:
                    issues.append(
                        f"Invalid log level: {level}. Valid levels: {valid_levels}"
                    )

            if "file" in logging_config:
                log_file = Path(logging_config["file"])
                if not log_file.parent.exists():
                    warnings.append(f"Log directory does not exist: {log_file.parent}")

        # Validate defaults section
        if "defaults" in config_data:
            defaults = config_data["defaults"]

            if "crew_process" in defaults:
                process = defaults["crew_process"]
                valid_processes = ["sequential", "hierarchical", "parallel"]
                if process not in valid_processes:
                    issues.append(
                        f"Invalid crew process: {process}. Valid: {valid_processes}"
                    )

            if "memory_limit" in defaults:
                memory = defaults["memory_limit"]
                if isinstance(memory, str) and memory.endswith("MB"):
                    try:
                        value = int(memory[:-2])
                        if value < 10:
                            warnings.append(f"Very low memory limit: {memory}")
                        elif value > 1000:
                            warnings.append(f"Very high memory limit: {memory}")
                    except ValueError:
                        issues.append(f"Invalid memory limit format: {memory}")

        # Display results
        if issues:
            click.echo(
                click.style(f"❌ Validation failed ({len(issues)} error(s)):", fg="red")
            )
            for issue in issues:
                click.echo(f"   • {issue}")
        else:
            click.echo(click.style("✅ Configuration is valid", fg="green"))

        if warnings:
            click.echo(click.style(f"\n⚠️  {len(warnings)} warning(s):", fg="yellow"))
            for warning in warnings:
                click.echo(f"   • {warning}")

        # Configuration summary
        click.echo("\n📋 Configuration Summary:")
        if "api" in config_data:
            click.echo(f"   API URL: {config_data['api'].get('url', 'Not set')}")
            click.echo(f"   Timeout: {config_data['api'].get('timeout', 'Default')}s")

        if "logging" in config_data:
            click.echo(
                f"   Log Level: {config_data['logging'].get('level', 'Default')}"
            )

        if "defaults" in config_data:
            click.echo(
                f"   Default Process: {config_data['defaults'].get('crew_process', 'sequential')}"
            )

        # Exit with error code if validation failed
        if issues:
            exit(1)

    except json.JSONDecodeError as e:
        click.echo(click.style(f"❌ JSON parsing error: {e}", fg="red"))
        exit(1)
    except yaml.YAMLError as e:
        click.echo(click.style(f"❌ YAML parsing error: {e}", fg="red"))
        exit(1)
    except Exception as e:
        click.echo(click.style(f"❌ Validation error: {str(e)}", fg="red"))
        exit(1)


@config_group.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.argument("key")
@click.argument("value", required=False)
def set(config_file, key, value):
    """Set or view configuration value.

    CONFIG_FILE: Path to configuration file
    KEY: Configuration key (use dot notation for nested keys)
    VALUE: New value (omit to view current value)

    Examples:
        litecrew config set config.yaml api.url http://localhost:8080
        litecrew config set config.yaml logging.level DEBUG
        litecrew config set config.yaml api.url  # View current value
    """
    try:
        # Load configuration
        with open(config_file, "r") as f:
            if config_file.endswith(".json"):
                config_data = json.load(f)
            else:
                config_data = yaml.safe_load(f)

        # Parse key path
        key_parts = key.split(".")

        if value is None:
            # View current value
            current = config_data
            try:
                for part in key_parts:
                    current = current[part]
                click.echo(f"{key}: {current}")
            except (KeyError, TypeError):
                click.echo(click.style(f"❌ Key '{key}' not found", fg="red"))
                exit(1)
        else:
            # Set new value
            current = config_data
            for part in key_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Try to parse value as appropriate type
            parsed_value = value
            if value.lower() in ("true", "false"):
                parsed_value = value.lower() == "true"
            elif value.isdigit():
                parsed_value = int(value)
            elif value.replace(".", "").isdigit():
                parsed_value = float(value)

            current[key_parts[-1]] = parsed_value

            # Write back to file
            with open(config_file, "w") as f:
                if config_file.endswith(".json"):
                    json.dump(config_data, f, indent=2)
                else:
                    yaml.dump(config_data, f, default_flow_style=False)

            click.echo(click.style(f"✅ Set {key} = {parsed_value}", fg="green"))

    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"))
        exit(1)


@config_group.command()
@click.option("--system", is_flag=True, help="Show system configuration paths")
def show(system):
    """Show configuration information."""
    if system:
        click.echo("🔧 LiteCrew Configuration Paths:")
        click.echo("=" * 35)

        # Standard configuration paths
        home_dir = Path.home()
        paths = [
            ("User config", home_dir / ".litecrew" / "config.yaml"),
            ("User config (JSON)", home_dir / ".litecrew" / "config.json"),
            ("System config", Path("/etc/litecrew/config.yaml")),
            ("Local config", Path.cwd() / "litecrew.yaml"),
            ("Local config (JSON)", Path.cwd() / "litecrew.json"),
        ]

        for name, path in paths:
            exists = "✅" if path.exists() else "❌"
            click.echo(f"{exists} {name:<20} {path}")

        click.echo("\n💡 Configuration loading order:")
        click.echo("   1. Command line --config option")
        click.echo("   2. Local directory (litecrew.yaml/json)")
        click.echo("   3. User directory (~/.litecrew/config.yaml)")
        click.echo("   4. System directory (/etc/litecrew/config.yaml)")

    else:
        # Show current configuration from environment
        click.echo("🔧 Current LiteCrew Configuration:")
        click.echo("=" * 35)

        # Environment variables
        env_vars = [
            ("LITECREW_API_URL", "API server URL"),
            ("LITECREW_API_TOKEN", "API authentication token"),
            ("LITECREW_CONFIG", "Configuration file path"),
            ("LOG_LEVEL", "Logging level"),
        ]

        click.echo("Environment variables:")
        for var, description in env_vars:
            value = os.environ.get(var, "(not set)")
            if "TOKEN" in var and value != "(not set)":
                value = "***" + value[-4:] if len(value) > 4 else "***"
            click.echo(f"   {var:<20} {value}")

        # Default values
        click.echo("\nDefault values:")
        defaults = [
            ("API URL", "http://localhost:8000"),
            ("Timeout", "30 seconds"),
            ("Log Level", "INFO"),
            ("Crew Process", "sequential"),
        ]

        for setting, default in defaults:
            click.echo(f"   {setting:<20} {default}")


@config_group.command()
@click.argument("source_file", type=click.Path(exists=True))
@click.argument("target_format", type=click.Choice(["json", "yaml"]))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def convert(source_file, target_format, output):
    """Convert configuration between formats.

    SOURCE_FILE: Path to source configuration file
    TARGET_FORMAT: Target format (json or yaml)
    """
    try:
        # Load source configuration
        with open(source_file, "r") as f:
            if source_file.endswith(".json"):
                config_data = json.load(f)
                source_format = "json"
            else:
                config_data = yaml.safe_load(f)
                source_format = "yaml"

        # Convert to target format
        if target_format == "json":
            converted_data = json.dumps(config_data, indent=2)
            default_ext = ".json"
        else:
            converted_data = yaml.dump(config_data, default_flow_style=False)
            default_ext = ".yaml"

        # Determine output path
        if output:
            output_path = Path(output)
        else:
            source_path = Path(source_file)
            output_path = source_path.with_suffix(default_ext)

        # Write converted configuration
        with open(output_path, "w") as f:
            f.write(converted_data)

        click.echo(
            click.style(
                f"✅ Converted {source_format} → {target_format}: {output_path}",
                fg="green",
            )
        )

    except Exception as e:
        click.echo(click.style(f"❌ Conversion failed: {str(e)}", fg="red"))
        exit(1)

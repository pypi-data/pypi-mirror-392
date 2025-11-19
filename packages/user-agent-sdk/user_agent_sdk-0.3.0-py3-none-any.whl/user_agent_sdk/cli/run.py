"""FastMCP run command implementation with enhanced type hints."""

import asyncio
import json
import sys
import threading
from user_agent_sdk.utils.logger import get_logger

logger = get_logger(__name__)

def run_command(
        agent_spec: str,
        config_file: str | None = None,
        debug: bool = False,
        abort_signal: threading.Event = None,
        workers: int | None = None,
        record_logs: bool = False,
) -> None:
    """
    Run a user agent based on the provided configuration.

    Args:
        agent_spec: Path to the agent Python file to run
        config_file: Path to the configuration file where all the settings are stored, use either config_file or the other parameters
        debug: Enable debug logging useful for troubleshooting
        abort_signal: Optional threading event to signal abortion of the agent run
        workers: Number of worker threads to spawn for the agent
        record_logs: Enable recording of execution logs for each task
    """

    try:
        from user_agent_sdk.decorators import clear_user_agent_registry
        clear_user_agent_registry()

        # Load the agent module dynamically
        import importlib.util
        from pathlib import Path

        path = Path(agent_spec).resolve()
        module_name = path.stem  # module name from filename
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Run the user agent worker
        from user_agent_sdk.user_agent_runner import UserAgentRunner

        runner = UserAgentRunner(
            config_file=config_file,
            debug=debug,
            abort_signal=abort_signal,
            workers=workers,
            record_logs=record_logs,
        )
        runner.run()
    except Exception as e:
        logger.error(f"Failed to run user agent: {e}", exc_info=e)
        sys.exit(1)

def run_cua_command(
        config_file: str | None = None,
        attach: bool = False,
        ui: bool = False,
        chrome_executable_path: str | None = None,
        debug: bool = False,
        abort_signal: threading.Event = None,
        record_logs: bool = False,
) -> None:
    try:
        from user_agent_sdk.decorators import clear_user_agent_registry, register_user_agent
        from logging import Logger
        from rich.console import Console
        from conductor.client.http.models.task import Task
        from user_agent_sdk.chrome_bridge import BridgeConfig, run_bridge
        
        clear_user_agent_registry()
        
        config_path = config_file or "credentials.json"
        console = Console()
        
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
        except FileNotFoundError:
            console.print(f"[red]Error: Configuration file not found: {config_path}[/red]")
            console.print("[yellow]Please create a credentials.json file with your API credentials[/yellow]")
            sys.exit(1)
        except json.JSONDecodeError as e:
            console.print(f"[red]Error: Invalid JSON in configuration file: {e}[/red]")
            sys.exit(1)
            
        # Extract required fields
        client_id = config_data.get('clientId')
        client_secret = config_data.get('clientSecret')
        base_url = config_data.get('baseUrl')
        # Support backward compatibility
        service_url = config_data.get('serviceUrl')
        auth_url = config_data.get('authUrl')

        if not client_id or not client_secret:
            console.print("[red]Error: clientId and clientSecret are required in configuration file[/red]")
            sys.exit(1)

        # Show warning if using deprecated fields
        if service_url or auth_url:
            console.print("[yellow]Warning: serviceUrl and authUrl are deprecated. Please use baseUrl instead.[/yellow]")

        console.print("[bold green]Starting Computer Use Agent[/bold green]")
        console.print(f"[cyan]Config file:[/cyan] {config_path}")

        if base_url:
            console.print(f"[cyan]Base URL:[/cyan] {base_url}")
        elif service_url:
            console.print(f"[cyan]Service URL:[/cyan] {service_url}")

        console.print(f"[cyan]Mode:[/cyan] {'Attach to existing' if attach else 'Launch new instance'}")
        if ui:
            console.print(f"[cyan]UI:[/cyan] Enabled")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")
        
        async def cua_agent(input_data: dict, logger: Logger, task: Task):
            cua_task = input_data.get("task")
            if not cua_task:
                logger.error("No task provided in input data")
                return None
            
            logger.info(f"Starting CUA agent for task: {cua_task}")
            
            config = BridgeConfig(
                base_url=base_url or "https://next.akabot.io",
                client_id=client_id,
                client_secret=client_secret,
                service_url=service_url,
                auth_url=auth_url,
                session_id=task.task_id,
                task=task.task_id,
                chrome_executable_path=chrome_executable_path,
                attach_mode=attach,
                ui=ui,
                ping_interval=10,
                ping_timeout=30,
                reconnect_delay=5,
            )
            
            try:
                return await run_bridge(config)
            except KeyboardInterrupt:
                console.print("\n[yellow]Computer Use Agent stopped[/yellow]")
            except Exception as e:
                logger.error(f"Computer Use Agent error: {e}", exc_info=e)
                sys.exit(1)
            
        register_user_agent(cua_agent)

        # Run the user agent worker
        from user_agent_sdk.user_agent_runner import UserAgentRunner

        runner = UserAgentRunner(
            config_file=config_file,
            debug=debug,
            abort_signal=abort_signal,
            record_logs=record_logs,
        )
        runner.run()
    except Exception as e:
        logger.error(f"Failed to run user agent: {e}", exc_info=e)
        sys.exit(1)

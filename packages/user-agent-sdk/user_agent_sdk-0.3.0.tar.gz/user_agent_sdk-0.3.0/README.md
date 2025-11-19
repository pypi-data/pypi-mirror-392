# User Agent SDK

A secure SDK for building custom user agents (workers) that run in your environment and connect safely with the akaBot
2.0 platform.

## Overview

The `User Agent SDK` empowers developers to build secure, customizable worker agents that operate within their own
environment while integrating seamlessly with the akaBot 2.0 platform. Each user agent extends workflow capabilities by
executing custom node logic locally, ensuring sensitive operations and data remain under the user’s control while
maintaining trusted communication and coordination with the central platform.

## Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager installed
- An akaBot 2.0 account with access to the Workflow Builder

## Installation

```bash
uv add user-agent-sdk
```

## Quick Start

### 1. Create a `credentials.json` file

This file contains the authentication details for your user agent.
You can download this file from the akaBot 2.0 Workflow Builder when creating a new user agent.

Place this file in the same directory as your user agent code.

```json
{
  "clientId": "your-client-id",
  "clientSecret": "your-client-secret",
  "agentId": "00000000-0000-0000-0000-000000000000#user-agent"
}
```

### 2. Create your user agent

The user agent code defines the logic that will be executed when the agent receives a task
such as processing data or performing actions.

```python
from logging import Logger
from user_agent_sdk import user_agent


@user_agent()
def sum_agent(input_data: dict, logger: Logger):
    # These logs will be visible in the akaBot 2.0 platform for monitoring
    logger.info("Processing task input")

    # Do some work with the input data
    num1 = input_data.get("num1", 0)
    num2 = input_data.get("num2", 0)
    total = num1 + num2

    return total

```

### 3. Run your user agent

Use built-in CLI to run your user agent locally:

```bash
useragent run your_agent.py
```

Alternatively, you can run it without installing the package using `uvx`:

```bash
uvx --from user-agent-sdk useragent run your_agent.py
```

### Folder structure:

```
your_project/
├── .venv/
├── credentials.json
├── pyproject.toml
└── your_agent.py
```

## Advanced Usage

### Custom Error Handling

The SDK automatically handles exceptions during task execution:

- Agent can be retried (max attempts are 3) on failure by regular exceptions
- `NonRetryableException` indicates that the task should not be retried

```python
from user_agent_sdk import user_agent
from user_agent_sdk.utils.exception import NonRetryableException


@user_agent()
def my_agent(input_data):
    user_name = input_data.get("user_name")
    if not user_name:
        raise NonRetryableException("'user_name' is required")

    # Regular processing...
```

### Async Support

The SDK supports asynchronous user agents using `async` functions.

```python
from user_agent_sdk import user_agent


@user_agent()
async def sum_agent():
    # async processing logic here
    pass
```

### High workload Handling

The SDK can handle high workloads by processing multiple tasks concurrently (vertical scaling),
or by running multiple instances of the user agent (horizontal scaling) in different machines.

To increase concurrency workers, use the `--workers` or `-w` flag when running the user agent:

```bash
# Spawn 4 concurrent workers for handling tasks for a single user agent
useragent run your_agent.py --workers 4
```

Alternatively, set the `workers` parameter in the `user_agent` decorator:

```python
from user_agent_sdk import user_agent


@user_agent(workers=4)
def sum_agent():
    # processing logic here
    pass
```

> If both workers flag and parameter are set, the flag takes precedence.

### Multiple User Agents

You can define multiple user agents in a single script by using the `user_agent` decorator multiple times with different
`agent_id`s.

```python
from user_agent_sdk import user_agent


@user_agent(agent_id="sum agent id")
def sum_agent():
    # processing logic here
    pass


@user_agent(agent_id="minus agent id")
def minus_agent():
    # processing logic here
    pass
```

> Run multiple user agents in one script/project is possible but not recommended.
> You should keep one user agent per script/project for better maintainability.

### Execution History

The SDK automatically records execution history for each task when enabled, allowing you to monitor and debug agent
executions.

#### Enable Execution History Recording

Use the `--record-execution-logs` or `-r` flag when running your agent:

```bash
useragent run your_agent.py -r
```

This will create a local SQLite database (`execution_history.db`) that stores:

- Task ID
- Agent ID and User Agent ID
- Start and end timestamps
- Execution status (success/error)
- Input and output data
- Error messages (if any)

#### View Execution History

Display a summary of recent executions:

```bash
# Show last 50 executions
useragent history

# Filter by agent ID
useragent history --agent-id "your-agent-id"

# Filter by user agent ID
useragent history --user-agent-id "user123"

# Limit number of records
useragent history --limit 100

# Use custom database path
useragent history --db-path /path/to/custom.db
```

#### View Detailed Execution Information

To see detailed information about a specific execution, including formatted input/output JSON:

```bash
# Show details for execution ID 1
useragent history-detail 1

# Or use the short alias
useragent hd 1

# With custom database path
useragent hd 5 --db-path /path/to/custom.db
```

The detail view displays:

- Complete execution metadata (Task ID, Agent ID, timestamps, status)
- Error messages (if any)
- **Input data** - Pretty-printed JSON with syntax highlighting
- **Output data** - Pretty-printed JSON with syntax highlighting

This is particularly useful for:

- Debugging failed executions
- Analyzing task inputs and outputs
- Monitoring agent performance
- Auditing agent activities

### Computer Use Agent (CUA)

The `cua` command (Computer Use Agent) lets you connect a local Chrome instance to the akaBot 2.0 platform so the platform can send control events to the browser running in your environment. Use this when your agent needs to automate browser actions locally while keeping credentials and sensitive data on your side.

Overview:

- Connects or launches a Chrome instance and bridges communication with the platform.
- Can attach to an existing Chrome process or launch a new one (auto-detects the Chrome executable if not provided).
- Optionally shows a small UI popup to display control events and connection status.
- Can record execution logs for each control task when enabled.

Usage:

```bash
# Basic: use default credentials.json in the current directory
useragent cua

# Specify a credentials file
useragent cua --config-file ./credentials.json

# Provide Chrome executable path (auto-detected if omitted)
useragent cua --chrome-executable-path "C:\Program Files\Google\Chrome\Application\chrome.exe"

# Attach to existing Chrome instead of launching a new one
useragent cua --attach

# Show the control UI popup
useragent cua --ui

# Enable recording execution logs for tasks handled via CUA
useragent cua -r

# Combine useful options
useragent cua --config-file ./credentials.json --chrome-executable-path "C:\Program Files\Google\Chrome\Application\chrome.exe" --ui -r -l DEBUG -d
```

Options (summary):

- `--config-file, -c`: Path to your credentials file (defaults to `credentials.json` in the current working directory).
- `--chrome-executable-path`: Explicit path to the Chrome binary to use. If omitted, the SDK will try to auto-detect a suitable Chrome/Chromium executable.
- `--attach, -a`: Attempt to attach to an existing Chrome instance instead of launching a new one.
- `--ui, -u`: Show a small UI popup to display control events coming from the platform (helpful for development and debugging).
- `--record-execution-logs, -r`: Record task execution logs into the local execution history database.
- `--log-level, -l`: Set logging verbosity (for example `INFO`, `DEBUG`).
- `--debug, -d`: Enable debug logging for more verbose troubleshooting output.

Troubleshooting & tips:

- Ensure the `credentials.json` file contains valid client credentials and an `agentId` with the correct format. Place it in your working directory or pass its path via `--config-file`.
- If `--attach` fails, verify a compatible Chrome instance is running and that it is started in a mode the SDK can connect to.
- Important: when attaching to an existing browser instance you must start Chrome with remote debugging enabled and ensure the remote-debugging port is available to the SDK. By convention the SDK connects to port 9222, so start Chrome with `--remote-debugging-port=9222`.

  On Windows you can start Chrome with remote debugging from PowerShell:

  ```powershell
  "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%TEMP%\\chrome-remote-profile"
  ```

  Note: if you use a custom port, start Chrome with that port and ensure any local firewall or network policy allows connections to that port (so the SDK can reach the browser). The SDK expects the browser's remote debugging endpoint to be reachable on the configured port.
- If Chrome isn't found automatically, provide the path with `--chrome-executable-path`.
- Use `--log-level DEBUG` and `--debug` when troubleshooting connection or control event problems.
- If you see permission errors on Windows, run the shell with appropriate rights or check that Chrome is allowed to be controlled by automation software.

Examples:

- Start a fresh Chrome instance and show the UI:

```bash
useragent cua --ui
```

- Attach to an already-running Chrome and enable execution logging:

```bash
useragent cua --attach -r
```

- Start CUA with a custom credentials file and an explicit Chrome binary:

```bash
useragent cua --config-file ./credentials.json --chrome-executable-path "C:\Program Files\Google\Chrome\Application\chrome.exe"
```

## License

Apache License 2.0
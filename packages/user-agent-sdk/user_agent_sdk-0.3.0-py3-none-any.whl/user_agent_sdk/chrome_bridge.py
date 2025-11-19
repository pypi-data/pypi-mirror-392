"""Chrome Bridge for connecting Chrome debugger to platform server."""

import asyncio
import base64
import subprocess
import platform
import shutil
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
import threading
from urllib.parse import quote

import requests
import httpx
import websockets
from websockets.asyncio.client import connect

from user_agent_sdk.utils.logger import get_logger
from user_agent_sdk.utils.url_generator import generate_service_url, generate_auth_url
from user_agent_sdk.cua_ui import AgentEventPopup

logger = get_logger(__name__)


class TokenManager:
    """Manages authentication tokens with automatic refresh."""

    def __init__(self, client_id: str, client_secret: str, auth_url: str, ttl_minutes: int | float = 45):
        """
        Initialize token manager.

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            auth_url: Authentication URL for token issuance
            ttl_minutes: Token time-to-live in minutes (default: 45)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = auth_url
        self.ttl_msec = int(ttl_minutes * 60 * 1000)
        self._token: Optional[str] = None
        self._token_update_time: int = 0

    def get_token(self) -> Optional[str]:
        """
        Get valid authentication token, refreshing if necessary.

        Returns:
            Valid authentication token or None if failed
        """
        now = round(time.time() * 1000)
        time_since_last_update = now - self._token_update_time

        # Check if token needs refresh
        if self._token is None or time_since_last_update > self.ttl_msec:
            logger.debug("Refreshing authentication token")
            self._refresh_token()

        return self._token

    def _refresh_token(self) -> None:
        """Refresh the authentication token."""
        try:
            if not self.client_id or not self.client_secret:
                logger.error("Client ID or Client Secret not set. Failed to get auth token")
                return

            logger.debug(f"Requesting token from {self.auth_url}")
            
            response = requests.post(
                self.auth_url,
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                timeout=10
            )
            response.raise_for_status()
            
            jwt = response.json()
            expires_in = jwt.get('expires_in')
            
            if expires_in:
                # Subtract 30 seconds for safety
                good_expires_in = int(expires_in) - 30
                self.ttl_msec = good_expires_in * 1000
                logger.debug(f"Token TTL set to {good_expires_in} seconds")

            self._token = jwt.get("access_token")
            self._token_update_time = round(time.time() * 1000)
            
            logger.info("✅ Authentication token obtained successfully")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get authentication token: {e}")
            self._token = None
        except Exception as e:
            logger.error(f"Unexpected error getting token: {e}")
            self._token = None

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers with Bearer token.

        Returns:
            Dictionary with Authorization header
        """
        token = self.get_token()
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}


@dataclass
class BridgeConfig:
    """Configuration for Chrome bridge."""
    client_id: str
    client_secret: str
    base_url: str = "https://next.akabot.io"
    session_id: Optional[str] = None
    task: Optional[str] = None
    chrome_host: str = "localhost"
    chrome_port: int = 9222
    chrome_executable_path: Optional[str] = None
    attach_mode: bool = False
    ui: bool = False
    ping_interval: int = 10
    ping_timeout: int = 30
    reconnect_delay: int = 5
    # Deprecated - kept for backward compatibility
    service_url: Optional[str] = None
    auth_url: Optional[str] = None

    def __post_init__(self):
        """Generate service_url and auth_url from base_url if not provided."""
        # Handle backward compatibility
        if self.service_url is None:
            self.service_url = generate_service_url(self.base_url)
            # Remove the /api suffix for service_url
            if self.service_url.endswith('/api'):
                self.service_url = self.service_url[:-4]
        if self.auth_url is None:
            self.auth_url = generate_auth_url(self.base_url)



class ChromeBridge:
    """Bridge between Chrome WebSocket debugger and platform control service."""

    def __init__(self, config: BridgeConfig):
        """
        Initialize Chrome bridge.

        Args:
            config: Bridge configuration
        """
        self.config = config
        self.chrome_process: Optional[subprocess.Popen] = None
        self._running = False
        self.popup: Optional[AgentEventPopup] = None
        self.popup_closed = False
        self._result: Optional[Any] = None
        
        # Ensure URLs are generated (should be done in __post_init__)
        if not config.service_url or not config.auth_url:
            raise ValueError("service_url and auth_url must be set in BridgeConfig")
        
        # Initialize token manager
        self.token_manager = TokenManager(
            client_id=config.client_id,
            client_secret=config.client_secret,
            auth_url=config.auth_url
        )
        
        # Build control WebSocket URL
        self.control_url = self._build_control_url()
        
        # Initialize UI if enabled
        if self.config.ui:
            self._init_ui()

    def _build_control_url(self) -> str:
        """
        Build control WebSocket URL from service URL.

        Returns:
            WebSocket URL for control service
        """
        # Convert HTTP(S) to WS(S)
        service_url = self.config.service_url.rstrip('/')  # type: ignore
        
        if service_url.startswith('https://'):
            ws_url = service_url.replace('https://', 'wss://')
        elif service_url.startswith('http://'):
            ws_url = service_url.replace('http://', 'ws://')
        else:
            ws_url = f"ws://{service_url}"
        
        ws_url = f"{ws_url}/cua/connect"
        
        logger.debug(f"Control WebSocket URL: {ws_url}")
        return ws_url

    def _init_ui(self) -> None:
        """Initialize the UI popup in a separate thread."""
        def on_popup_close():
            """Callback when popup is closed."""
            logger.info("UI popup closed by user")
            self.popup_closed = True
            self._running = False
            
            # Close browser if in non-attach mode
            if not self.config.attach_mode and self.chrome_process:
                logger.info("Closing browser (non-attach mode)")
                self._close_chrome_process()
        
        def run_ui():
            """Run UI in separate thread."""
            self.popup = AgentEventPopup(on_close_callback=on_popup_close)
            self.popup.set_event_name("Waiting for events...")
            self.popup.show()
        
        ui_thread = threading.Thread(target=run_ui, daemon=True)
        ui_thread.start()
        logger.info("UI popup initialized")

    def _find_chrome_executable(self) -> Optional[str]:
        """Find Chrome executable path based on platform."""
        # If executable path is explicitly provided, use it
        if self.config.chrome_executable_path:
            path_obj = Path(self.config.chrome_executable_path)
            if path_obj.exists():
                return str(path_obj)
            else:
                logger.warning(f"Specified Chrome executable path does not exist: {self.config.chrome_executable_path}")
                return None
        
        system = platform.system()
        
        possible_paths = []
        if system == "Windows":
            possible_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe",
            ]
        elif system == "Darwin":  # macOS
            possible_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            ]
        else:  # Linux
            possible_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
            ]

        # Try to find chrome using which/where command
        chrome_cmd = "chrome" if system != "Windows" else "chrome.exe"
        chrome_path = shutil.which(chrome_cmd) or shutil.which("google-chrome")
        
        if chrome_path:
            return chrome_path

        # Check known paths
        for path in possible_paths:
            path_obj = Path(path)
            if path_obj.exists():
                return str(path_obj)

        return None

    async def _start_chrome(self) -> bool:
        """
        Start Chrome in debug mode.

        Returns:
            True if Chrome started successfully, False otherwise
        """
        if self.config.attach_mode:
            logger.info("Attach mode enabled, skipping Chrome launch")
            return True

        chrome_path = self._find_chrome_executable()
        if not chrome_path:
            logger.error("Chrome executable not found. Please install Chrome or specify --attach mode.")
            return False

        logger.info(f"Starting Chrome from: {chrome_path}")
        
        try:
            # Chrome arguments for remote debugging
            chrome_args = [
                chrome_path,
                f"--remote-debugging-port={self.config.chrome_port}",
                "--remote-debugging-address=0.0.0.0",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "--disable-background-networking",
            ]

            # Start Chrome process
            self.chrome_process = subprocess.Popen(
                chrome_args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            
            logger.info(f"Chrome started with PID: {self.chrome_process.pid}")
            
            # Wait a bit for Chrome to start
            await asyncio.sleep(2)
            
            return True

        except Exception as e:
            logger.error(f"Failed to start Chrome: {e}")
            return False

    async def _get_chrome_debugger_url(self) -> Optional[str]:
        """
        Get Chrome WebSocket debugger URL.

        Returns:
            WebSocket debugger URL or None if failed
        """
        url = f"http://{self.config.chrome_host}:{self.config.chrome_port}/json/version"
        
        # Retry logic for getting debugger URL
        max_retries = 5
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    debug_info = response.json()
                    ws_url = debug_info.get("webSocketDebuggerUrl")
                
                if ws_url:
                    logger.info(f"Chrome debugger URL: {ws_url}")
                    return ws_url
                else:
                    logger.warning("No webSocketDebuggerUrl in response")
                    
            except (httpx.RequestError, json.JSONDecodeError, Exception) as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
        
        return None

    async def _bridge_messages(
        self,
        chrome_ws: websockets.ClientConnection,
        control_ws: websockets.ClientConnection
    ) -> None:
        """
        Bridge messages between Chrome and control service.

        Args:
            chrome_ws: Chrome WebSocket connection
            control_ws: Control service WebSocket connection
        """
        async def chrome_to_remote():
            """Forward messages from Chrome to remote control."""
            try:
                async for msg in chrome_ws:
                    if not self._running:
                        break
                    
                    # Convert message to string for logging
                    msg_str = msg if isinstance(msg, str) else (
                        bytes(msg).decode(errors='ignore') 
                        if isinstance(msg, (bytes, bytearray, memoryview)) 
                        else str(msg)
                    )
                    logger.debug(f"Chrome → Remote: {msg_str[:100]}...")
                    
                    await control_ws.send(msg)
            except websockets.exceptions.ConnectionClosed:
                logger.warning("Remote platform connection closed")
                self._running = False
            except Exception as e:
                logger.error(f"Error in chrome_to_remote: {e}")
                self._running = False

        async def remote_to_chrome():
            """Forward messages from remote control to Chrome."""
            try:
                async for msg in control_ws:
                    if not self._running:
                        break
                    
                    # Convert message to string for logging
                    msg_str = msg if isinstance(msg, str) else (
                        bytes(msg).decode(errors='ignore') 
                        if isinstance(msg, (bytes, bytearray, memoryview)) 
                        else str(msg)
                    )
                    logger.debug(f"Remote → Chrome: {msg_str[:100]}...")
                    
                    # Check if this is a control message
                    should_forward = True
                    if isinstance(msg, str):
                        try:
                            msg_data = json.loads(msg)
                            if isinstance(msg_data, dict) and msg_data.get("__control__") is True:
                                # This is a control message, don't forward to Chrome
                                should_forward = False
                                logger.debug(f"Control message received: {msg_data}")
                                
                                control_type = msg_data.get("__type__")
                                
                                if control_type == "result":
                                    # Store the result and stop the bridge
                                    result = msg_data.get("result")
                                    llm_usage = msg_data.get("llm_usage")
                                    self._result = {
                                        "content": result,
                                        "llm_usage": llm_usage
                                    }
                                    logger.info(f"Final result received: {self._result}")
                                    self._running = False
                                    break
                                elif control_type == "event":
                                    # Update UI if enabled
                                    if self.config.ui and self.popup:
                                        event_type = msg_data.get("event_type", "Unknown event")
                                        self.popup.set_event_name(event_type)
                                        logger.info(f"UI updated with event: {event_type}")
                                    else:
                                        logger.debug(f"Event received: {msg_data.get('event_type', 'Unknown')}")
                                else:
                                    # Unknown control message type
                                    logger.warning(f"Unknown control message type: {control_type}. Message: {msg_data}")
                        except json.JSONDecodeError:
                            # Not JSON, forward as normal
                            pass
                    
                    if should_forward:
                        await chrome_ws.send(msg)
                    
                    # If popup was closed, send notification to platform
                    if self.popup_closed:
                        logger.info("Sending popup closed notification to platform")
                        close_msg = json.dumps({"__control__": True, "closed": True})
                        await control_ws.send(close_msg)
                        self.popup_closed = False  # Reset flag
                        
            except websockets.exceptions.ConnectionClosed | websockets.exceptions.ConnectionClosedError:
                logger.warning("Remote platform connection closed")
                self._running = False
            except Exception as e:
                logger.error(f"Error in remote_to_chrome: {e}")
                self._running = False
            finally:
                await chrome_ws.close()
                await control_ws.close()

        # Run both direction bridges concurrently
        await asyncio.gather(chrome_to_remote(), remote_to_chrome())

    async def run(self) -> Optional[Any]:
        """Run the Chrome bridge.
        
        Returns:
            The final result if a control message with __type__='result' is received, otherwise None.
        """
        self._running = True
        self._result = None
        
        # Get initial token to verify credentials
        logger.info("Obtaining authentication token...")
        token = self.token_manager.get_token()
        if not token:
            logger.error("Failed to obtain authentication token. Check your credentials.")
            return
        
        # Start Chrome if not in attach mode
        if not await self._start_chrome():
            logger.error("Failed to start Chrome")
            return

        # Get Chrome debugger URL
        ws_debug_url = await self._get_chrome_debugger_url()
        if not ws_debug_url:
            logger.error("Failed to get Chrome debugger URL")
            if self.chrome_process:
                self.chrome_process.terminate()
            return

        logger.info("Starting bridge between Chrome and control service...")
        logger.info(f"Chrome: {self.config.chrome_host}:{self.config.chrome_port}")
        logger.info(f"Control: {self.control_url}")

        # Main bridge loop with reconnection
        while self._running:
            try:
                async with connect(
                    ws_debug_url,
                    ping_interval=self.config.ping_interval,
                    ping_timeout=self.config.ping_timeout,
                    max_size=None,
                ) as chrome_ws:
                    logger.info("✅ Connected to Chrome debugger")
                    
                    # Get fresh token and auth headers for control connection
                    auth_headers = self.token_manager.get_auth_headers()
                    
                    # Add agent ID to headers if provided
                    if self.config.session_id:
                        auth_headers["X-Session-ID"] = quote(self.config.session_id)
                        logger.debug(f"Using Agent ID: {self.config.session_id}")
                    
                    # Add task to headers if provided
                    if self.config.task:
                        auth_headers["X-TASK"] = self.config.task
                        logger.debug(f"Using Task: {self.config.task}")
                    
                    async with connect(
                        self.control_url,
                        additional_headers=auth_headers,
                        ping_interval=self.config.ping_interval,
                        ping_timeout=self.config.ping_timeout,
                        max_size=None,
                    ) as control_ws:
                        logger.info("✅ Connected to control service")
                        
                        await self._bridge_messages(chrome_ws, control_ws)
                        
                        # If popup was closed or connection lost, exit the loop
                        if self.popup_closed or not self._running:
                            logger.info("Exiting bridge due to popup closure or connection loss")
                            self._running = False
                            break
                        
            except KeyboardInterrupt:
                logger.info("Shutting down bridge...")
                self._running = False
                break
            except websockets.exceptions.ConnectionClosed:
                logger.warning("⚠️  Platform connection closed, exiting bridge...")
                self._running = False
                break
            except Exception as e:
                logger.warning(f"⚠️  Connection error: {e}")
                if self._running and not self.popup_closed:
                    logger.info(f"Retrying in {self.config.reconnect_delay}s...")
                    await asyncio.sleep(self.config.reconnect_delay)
                else:
                    logger.info("Exiting bridge...")
                    self._running = False
                    break
        
        return self._result

    def stop(self) -> None:
        """Stop the bridge and cleanup."""
        self._running = False
        
        if self.chrome_process:
            logger.info("Terminating Chrome process...")
            self.chrome_process.terminate()
            try:
                self.chrome_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Chrome did not terminate gracefully, killing...")
                self.chrome_process.kill()
            self.chrome_process = None

    def _close_chrome_process(self) -> None:
        """Close Chrome process if it exists."""
        if self.chrome_process:
            try:
                logger.info("Terminating Chrome process...")
                self.chrome_process.terminate()
                self.chrome_process.wait(timeout=5)
                logger.info("Chrome process terminated successfully")
            except subprocess.TimeoutExpired:
                logger.warning("Chrome did not terminate gracefully, killing...")
                self.chrome_process.kill()
            except Exception as e:
                logger.error(f"Error closing Chrome process: {e}")
            finally:
                self.chrome_process = None


async def run_bridge(config: BridgeConfig) -> Optional[Any]:
    """
    Run Chrome bridge with the given configuration.

    Args:
        config: Bridge configuration
    
    Returns:
        The final result if a control message with __type__='result' is received, otherwise None.
    """
    bridge = ChromeBridge(config)
    try:
        return await bridge.run()
    finally:
        bridge.stop()

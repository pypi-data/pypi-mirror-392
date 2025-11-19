import inspect
from functools import wraps
from typing import Callable, Any, List, Dict, Optional

# Registry to hold decorated methods and their config
user_agent_registry: List[Dict[str, Any]] = []


def user_agent(
        agent_id: Optional[str] = None,
        worker_id: Optional[str] = None,
        domain: Optional[str] = None,
        poll_interval: int = 1000,
        workers: int = 1,
):
    def decorator(func: Callable):
        # Check if the function is async
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            # Store the function and config in the registry
            user_agent_config = {
                "func": async_wrapper,
                "config": {
                    "agent_id": agent_id,
                    "worker_id": worker_id,
                    "domain": domain,
                    "poll_interval": poll_interval,
                    "workers": workers,
                }
            }
            effective_wrapper = async_wrapper
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            # Store the function and config in the registry
            user_agent_config = {
                "func": func,
                "config": {
                    "agent_id": agent_id,
                    "worker_id": worker_id,
                    "domain": domain,
                    "poll_interval": poll_interval,
                    "workers": workers,
                }
            }
            effective_wrapper = wrapper

        user_agent_registry.append(user_agent_config)

        return effective_wrapper

    return decorator


def register_user_agent(
        func: Callable,
        agent_id: Optional[str] = None,
        worker_id: Optional[str] = None,
        domain: Optional[str] = None,
        poll_interval: int = 1000,
        workers: int = 1,
):
    """
    Manually register a user agent function without using the decorator.
    
    Args:
        func: The function to register (can be sync or async)
        agent_id: The agent ID for this user agent
        worker_id: The worker ID for this user agent
        domain: The domain for this user agent
        poll_interval: Polling interval in milliseconds (default: 1000)
        workers: Number of worker instances (default: 1)
    
    Returns:
        The registered function (unchanged)
    """
    # Store the function and config in the registry
    user_agent_config = {
        "func": func,
        "config": {
            "agent_id": agent_id,
            "worker_id": worker_id,
            "domain": domain,
            "poll_interval": poll_interval,
            "workers": workers,
        }
    }
    user_agent_registry.append(user_agent_config)
    return func


def clear_user_agent_registry():
    """Utility function to clear the user agent registry."""
    user_agent_registry.clear()

import functools
import time
import requests
import asyncio
from typing import Callable, Optional

API_URL = "http://localhost:5001/track"  # hardcoded for now


def _post_event(payload: dict):
    """Fire-and-forget POST to local API; errors ignored."""
    try:
        requests.post(API_URL, json=payload, timeout=0.5)
    except Exception:
        pass


def track_action(agent_name: Optional[str] = None, action_name: Optional[str] = None):
    """Simple decorator: captures timestamp before & after calling a function,
    reports to localhost via POST.

    - No storage
    - No models
    - No async orchestration
    - Minimal logic
    """

    def decorator(func: Callable):
        is_coro = asyncio.iscoroutinefunction(func)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()

            _post_event({
                "event": "start",
                "agent": agent_name or "unknown-agent",
                "action": action_name or func.__name__,
                "timestamp": start,
            })

            try:
                result = func(*args, **kwargs)
                success = True
            except Exception as e:
                success = False
                raise
            finally:
                end = time.time()
                _post_event({
                    "event": "end",
                    "agent": agent_name or "unknown-agent",
                    "action": action_name or func.__name__,
                    "timestamp": end,
                    "success": success,
                })
            return result

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()

            _post_event({
                "event": "start",
                "agent": agent_name or "unknown-agent",
                "action": action_name or func.__name__,
                "timestamp": start,
            })

            try:
                result = await func(*args, **kwargs)
                success = True
            except Exception:
                success = False
                raise
            finally:
                end = time.time()
                _post_event({
                    "event": "end",
                    "agent": agent_name or "unknown-agent",
                    "action": action_name or func.__name__,
                    "timestamp": end,
                    "success": success,
                })
            return result

        return async_wrapper if is_coro else sync_wrapper

    return decorator

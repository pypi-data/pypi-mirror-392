"""
Global state management for Playgent SDK

This module maintains all global state that was previously managed by PlaygentClient instances.
"""

import contextvars
import threading
from dataclasses import dataclass
from queue import Queue
from typing import Optional, List, Any

# Configuration (initialized from environment or explicit init)
api_key: Optional[str] = None
server_url: str = "https://run.blaxel.ai/pharmie-agents/agents/playgent"  # Default, can be overridden
batch_size: int = 10

# Trace state
trace_id: Optional[str] = None  # Current trace ID
person_id: Optional[str] = None


@dataclass
class TraceContextData:
    """Container for trace context data"""
    trace_id: str
    session_id: Optional[str] = None  # User-provided session/conversation ID
    person_id: Optional[str] = None


# Thread-safe context variable for trace management
_trace_context: contextvars.ContextVar[Optional[TraceContextData]] = contextvars.ContextVar('playgent_trace', default=None)

# Runtime state
is_running: bool = False

# Event tracking
events: List[Any] = []
event_queue: Queue = Queue()
sender_thread: Optional[threading.Thread] = None
stop_sender: threading.Event = threading.Event()
endpoint: Optional[str] = None

# Lock for thread-safe state modifications
_state_lock = threading.Lock()
"""
Holos SDK - A Python SDK for A2A (Agent-to-Agent) communication with automatic tracing.

This SDK provides:
- HolosA2AClientFactory: A client factory that creates clients with automatic tracing
- HolosTracingA2AClient: A client wrapper that handles response tracing
- HolosRequestHandler: A server-side request handler with tracing functionality
- PlantTracer: A tracing utility for submitting object tracing data
- Plan and Assignment types for planning agents
- HolosEventQueue: A re-enterable event queue that allows consuming from any event_id
- HolosQueueManager: A queue manager that creates re-enterable event queues
"""

from .holos_a2a_client_factory import HolosA2AClientFactory
from .holos_a2a_client import HolosTracingA2AClient
from .holos_request_handler import HolosRequestHandler
from .plant_tracer import PlantTracer, no_op_tracer
from .types import Plan, Assignment
from .logging_config import setup_logging
from .holos_event_queue import HolosEventQueue
from .holos_queue_manager import HolosQueueManager

# Set up default logging
setup_logging()

__version__ = "0.1.0"
__all__ = [
    "HolosA2AClientFactory",
    "HolosTracingA2AClient",
    "HolosRequestHandler",
    "PlantTracer",
    "no_op_tracer",
    "Plan",
    "Assignment",
    "HolosEventQueue",
    "HolosQueueManager",
]
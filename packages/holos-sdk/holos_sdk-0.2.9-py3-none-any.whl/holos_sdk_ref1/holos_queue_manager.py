"""
Re-enterable Queue Manager that creates and manages re-enterable event queues.

This module provides a custom QueueManager implementation that creates
re-enterable EventQueue instances (with event_id tracking) instead of the default a2a event queues.
The key feature is the ability to re-enter and consume events from any event_id.
"""

import asyncio
import logging
from typing import Optional
from a2a.server.events import QueueManager, EventQueue, TaskQueueExists, NoTaskQueue

from .holos_event_queue import HolosEventQueue

logger = logging.getLogger(__name__)


class HolosQueueManager(QueueManager):
    """
    A QueueManager that creates re-enterable EventQueue instances.
    
    This manager replaces the default a2a QueueManager and ensures all
    event queues are re-enterable (can consume from any event_id).
    Events are persisted for a configurable duration (default 24 hours) to enable re-entering from past events.
    """
    
    def __init__(self, retention_seconds: int = 86400, cleanup_interval_seconds: int = 3600):
        """
        Initialize the Holos queue manager.
        
        Args:
            retention_seconds: How long to keep events in queues in seconds (default: 86400 = 24 hours)
            cleanup_interval_seconds: How often to run cleanup in seconds (default: 3600 = 1 hour)
        """
        self._queues: dict[str, HolosEventQueue] = {}
        self._retention_seconds = retention_seconds
        self._cleanup_interval = cleanup_interval_seconds
        self._lock = asyncio.Lock()
        retention_hours = retention_seconds / 3600.0
        logger.info(f"Initialized HolosQueueManager (re-enterable queues with {retention_seconds}s / {retention_hours:.1f}h retention)")
    
    async def add(self, task_id: str, queue: EventQueue) -> None:
        """Adds a new event queue for a task ID.
        
        Args:
            task_id: The task ID to associate with the queue
            queue: The EventQueue instance to add
            
        Raises:
            TaskQueueExists: If a queue for the given `task_id` already exists.
        """
        async with self._lock:
            if task_id in self._queues:
                raise TaskQueueExists
            if not isinstance(queue, HolosEventQueue):
                # Convert to HolosEventQueue if needed
                holos_queue = HolosEventQueue(
                    retention_seconds=self._retention_seconds,
                    cleanup_interval_seconds=self._cleanup_interval,
                )
                self._queues[task_id] = holos_queue
            else:
                self._queues[task_id] = queue
            logger.debug(f"Added HolosEventQueue for task_id: {task_id} with queue: {queue}")
    
    async def get(self, task_id: str) -> EventQueue | None:
        """Retrieves the event queue for a task ID.
        
        Args:
            task_id: The task ID to look up
            
        Returns:
            The `EventQueue` instance for the `task_id`, or `None` if not found.
        """
        async with self._lock:
            return self._queues.get(task_id)
    
    async def tap(self, task_id: str) -> EventQueue | None:
        """Taps the event queue for a task ID to create a child queue.
        
        Args:
            task_id: The task ID to tap
            
        Returns:
            A new child `EventQueue` instance, or `None` if the task ID is not found.
        """
        async with self._lock:
            if task_id not in self._queues:
                return None
            return self._queues[task_id].tap()
    
    async def close(self, task_id: str) -> None:
        """Closes and removes the event queue for a task ID.
        
        Args:
            task_id: The task ID to close
            
        Raises:
            NoTaskQueue: If no queue exists for the given `task_id`.
        """
        async with self._lock:
            if task_id not in self._queues:
                raise NoTaskQueue
            queue = self._queues.pop(task_id)
            await queue.close()
            logger.debug(f"Closed and removed HolosEventQueue for task_id: {task_id}")
    
    async def create_or_tap(self, task_id: str) -> EventQueue:
        """Creates a new event queue for a task ID if one doesn't exist, otherwise taps the existing one.
        
        Args:
            task_id: The task ID to create or tap
            
        Returns:
            A new or child `EventQueue` instance for the `task_id`.
        """
        async with self._lock:
            if task_id not in self._queues:
                queue = HolosEventQueue(
                    retention_seconds=self._retention_seconds,
                    cleanup_interval_seconds=self._cleanup_interval
                )
                self._queues[task_id] = queue
                logger.debug(f"Created new HolosEventQueue for task_id: {task_id}")
                return queue
            logger.debug(f"Tapping existing HolosEventQueue for task_id: {task_id}")
            return self._queues[task_id].tap()
    
    def get_holos_queue(self, task_id: str) -> Optional[HolosEventQueue]:
        """
        Get a HolosEventQueue instance directly (for advanced usage).
        
        Args:
            task_id: Unique identifier for the queue
            
        Returns:
            The HolosEventQueue instance, or None if not found
        """
        return self._queues.get(task_id)


"""
Re-enterable Event Queue with event_id tracking.

This module provides a custom EventQueue implementation that:
1. Auto-adds 'event_id' to Event's metadata dict
2. Supports re-entering and consuming events from a given event_id (key feature)
3. Persists events for 24 hours to enable re-entering from past events
"""

import asyncio
import copy
import json
import logging
import sys
import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List, Any
from a2a.server.events import Event, EventQueue

logger = logging.getLogger(__name__)

DEFAULT_MAX_QUEUE_SIZE = 1024


class StoredEvent:
    """Internal representation of a stored event with metadata."""
    
    def __init__(self, event: Event, event_id: str, timestamp: datetime):
        # Store a snapshot of the event instead of the reference
        # This ensures the stored event won't be affected by later modifications
        self.event = self._create_event_snapshot(event)
        self.event_id = event_id
        self.timestamp = timestamp
    
    @staticmethod
    def _create_event_snapshot(event: Event) -> Event:
        """
        Create a snapshot (deep copy) of an event to prevent reference issues.
        
        Handles different event types:
        - Pydantic models: Uses model_copy() or model_validate()
        - Regular objects: Uses copy.deepcopy()
        
        Args:
            event: The event to snapshot
            
        Returns:
            A snapshot copy of the event
        """
        # Try Pydantic model_copy for immutable models (most efficient)
        if hasattr(event, 'model_copy'):
            try:
                return event.model_copy()
            except (AttributeError, TypeError) as e:
                logger.debug(f"model_copy failed for {type(event)}: {e}, trying alternative methods")
        
        # Try model_validate for Pydantic v2 (reconstruct from dict)
        if hasattr(event, 'model_dump'):
            try:
                event_dict = event.model_dump()
                return event.__class__.model_validate(event_dict)
            except (AttributeError, TypeError, ValueError) as e:
                logger.debug(f"model_validate failed for {type(event)}: {e}, trying deepcopy")
        
        # Fallback to deepcopy for regular objects
        try:
            return copy.deepcopy(event)
        except (TypeError, AttributeError) as e:
            logger.warning(f"Could not create snapshot of event {type(event)}: {e}, storing reference (may be mutable)")
            return event


class HolosEventQueue(EventQueue):
    """
    A re-enterable EventQueue that allows consuming events from any event_id.
    
    Key Features:
    - Re-enterable: Consume events from any given event_id (primary feature)
    - Auto-generates unique event_id for each event and adds to metadata
    - Persists events for a configurable duration (default 24 hours) to enable re-entering from past events
    - Automatic cleanup of expired events
    
    Usage:
    - Standard interface: Use `dequeue_event()` for standard queue consumption (inherited from EventQueue)
    - Re-enterable interface: Use `consume_events(from_event_id=...)` for re-enterable consumption from any event_id
    """
    
    def __init__(self, retention_seconds: int = 86400, cleanup_interval_seconds: int = 3600, max_queue_size: int = DEFAULT_MAX_QUEUE_SIZE):
        """
        Initialize the persistent event queue.
        
        Args:
            retention_seconds: How long to keep events in seconds (default: 86400 = 24 hours)
            cleanup_interval_seconds: How often to run cleanup in seconds (default: 3600 = 1 hour)
            max_queue_size: Maximum size for the asyncio.Queue (default: 1024)
        """
        # Call parent __init__ to set up asyncio.Queue for compatibility
        super().__init__(max_queue_size=max_queue_size)
        
        self._events: List[StoredEvent] = []
        self._event_id_index: Dict[str, int] = {}  # event_id -> index in _events
        self._retention_seconds = retention_seconds
        self._cleanup_interval = cleanup_interval_seconds
        self._cleanup_task: Optional[asyncio.Task] = None
        self._consumers: Dict[str, int] = {}  # consumer_id -> last consumed index
        self._storage_lock = asyncio.Lock()  # Lock for storage operations (separate from parent's _lock)
        # Don't start cleanup task in __init__ - start it lazily when needed
    
    async def _start_cleanup_task(self):
        """Start the background cleanup task (lazy initialization)."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Background task to periodically clean up expired events."""
        try:
            while True:
                await asyncio.sleep(self._cleanup_interval)
                await self._cleanup_expired_events()
        except asyncio.CancelledError:
            logger.debug("Cleanup task cancelled")
        except Exception as e:
            logger.error(f"Error in cleanup loop: {e}", exc_info=True)
    
    async def _cleanup_expired_events(self):
        """Remove events older than retention period."""
        async with self._storage_lock:
            cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=self._retention_seconds)
            
            # Find the first index that's not expired
            first_valid_index = 0
            for i, stored_event in enumerate(self._events):
                if stored_event.timestamp >= cutoff_time:
                    first_valid_index = i
                    break
                else:
                    # Remove from index
                    if stored_event.event_id in self._event_id_index:
                        del self._event_id_index[stored_event.event_id]
            
            # Remove expired events
            if first_valid_index > 0:
                removed_count = first_valid_index
                self._events = self._events[first_valid_index:]
                
                # Rebuild index
                self._event_id_index = {stored.event_id: i for i, stored in enumerate(self._events)}
                
                # Update consumer positions
                for consumer_id in list(self._consumers.keys()):
                    if self._consumers[consumer_id] < removed_count:
                        self._consumers[consumer_id] = 0
                    else:
                        self._consumers[consumer_id] -= removed_count
                
                logger.debug(f"Cleaned up {removed_count} expired events")
    
    def _format_event_details(self, event: Event) -> str:
        """
        Format event details for logging.
        
        Args:
            event: The event to format
            
        Returns:
            A formatted string with event details
        """
        details = []
        
        # Try to get event type/class name
        event_type = type(event).__name__
        details.append(f"type={event_type}")
        
        # Try to get event id
        if hasattr(event, 'id'):
            try:
                details.append(f"id={event.id}")
            except Exception:
                pass
        
        # Try to get metadata
        if hasattr(event, 'metadata'):
            try:
                metadata = getattr(event, 'metadata', None)
                if metadata:
                    if isinstance(metadata, dict):
                        # Include metadata keys and some values
                        metadata_str = ", ".join([f"{k}={v}" for k, v in list(metadata.items())[:5]])
                        if len(metadata) > 5:
                            metadata_str += f" ... ({len(metadata)} total)"
                        details.append(f"metadata=[{metadata_str}]")
                    else:
                        details.append(f"metadata={metadata}")
            except Exception:
                pass
        
        # Try to get other common attributes
        for attr in ['type', 'actor', 'content', 'timestamp']:
            if hasattr(event, attr):
                try:
                    value = getattr(event, attr)
                    # Truncate long content
                    if attr == 'content' and value:
                        value_str = str(value)
                        if len(value_str) > 200:
                            value_str = value_str[:200] + "... (truncated)"
                        details.append(f"{attr}={value_str}")
                    else:
                        details.append(f"{attr}={value}")
                except Exception:
                    pass
        
        # Try to get full representation if it's a Pydantic model
        if hasattr(event, 'model_dump'):
            try:
                event_dict = event.model_dump()
                # Convert to JSON-like string, but limit size
                event_json = json.dumps(event_dict, default=str, ensure_ascii=False)
                if len(event_json) > 1000:
                    event_json = event_json[:1000] + "... (truncated)"
                details.append(f"full={event_json}")
            except Exception:
                # Fallback to repr if model_dump fails
                try:
                    event_repr = repr(event)
                    if len(event_repr) > 500:
                        event_repr = event_repr[:500] + "... (truncated)"
                    details.append(f"repr={event_repr}")
                except Exception:
                    pass
        
        return ", ".join(details)
    
    async def _add_event_id_to_metadata(self, event: Event, event_id: str) -> Event:
        """
        Add event_id to event's metadata, handling both mutable and immutable events.
        
        For Pydantic models (immutable), creates a copy with updated metadata.
        For regular objects, modifies in place.
        
        Args:
            event: The event to modify
            event_id: The event_id to add
            
        Returns:
            The event with event_id in metadata (may be a new instance for immutable events)
        """
        # Check if event already has event_id in metadata
        if hasattr(event, 'metadata') and isinstance(event.metadata, dict):
            if 'event_id' in event.metadata:
                # Already has event_id, return as-is
                return event
        
        # Try to modify metadata in place first (for mutable objects)
        if hasattr(event, 'metadata'):
            try:
                if event.metadata is None:
                    event.metadata = {}
                elif not isinstance(event.metadata, dict):
                    # If metadata exists but isn't a dict, wrap it
                    event.metadata = {'original': event.metadata}
                
                # Try to set metadata directly
                event.metadata['event_id'] = event_id
                return event
            except (AttributeError, TypeError):
                # If direct modification fails, try Pydantic model_copy
                pass
        
        # Try Pydantic model_copy for immutable models
        if hasattr(event, 'model_copy'):
            try:
                current_metadata = getattr(event, 'metadata', None) or {}
                if not isinstance(current_metadata, dict):
                    current_metadata = {'original': current_metadata}
                
                new_metadata = {**current_metadata, 'event_id': event_id}
                return event.model_copy(update={'metadata': new_metadata})
            except (AttributeError, TypeError) as e:
                logger.warning(f"Could not add event_id to event {type(event)}: {e}")
                return event
        
        # Try model_validate for Pydantic v2
        if hasattr(event, 'model_dump'):
            try:
                event_dict = event.model_dump()
                if 'metadata' not in event_dict or event_dict['metadata'] is None:
                    event_dict['metadata'] = {}
                elif not isinstance(event_dict['metadata'], dict):
                    event_dict['metadata'] = {'original': event_dict['metadata']}
                
                event_dict['metadata']['event_id'] = event_id
                return event.__class__.model_validate(event_dict)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Could not add event_id to event {type(event)} using model_validate: {e}")
                return event
        
        # Last resort: try to set attribute directly
        try:
            if not hasattr(event, 'metadata'):
                setattr(event, 'metadata', {})
            elif event.metadata is None:
                event.metadata = {}
            elif not isinstance(event.metadata, dict):
                event.metadata = {'original': event.metadata}
            
            event.metadata['event_id'] = event_id
            return event
        except (AttributeError, TypeError) as e:
            logger.warning(f"Could not add event_id to event {type(event)}: {e}")
            return event
    
    async def enqueue_event(self, event: Event) -> None:
        """
        Enqueue an event with auto-generated event_id.
        
        This overrides the parent method to add event_id tracking while maintaining
        compatibility with the standard EventQueue interface.
        
        Args:
            event: The event to enqueue
        """
        # Start cleanup task if not already started (lazy initialization)
        await self._start_cleanup_task()
        
        async with self._storage_lock:
            # Generate unique event_id
            event_id = str(uuid.uuid4())
            
            # Add event_id to metadata (may return a new event instance for immutable models)
            event_with_id = await self._add_event_id_to_metadata(event, event_id)
            
            # Store event with timestamp for re-enterability
            # StoredEvent will create a snapshot internally to prevent reference issues
            stored_event = StoredEvent(
                event=event_with_id,
                event_id=event_id,
                timestamp=datetime.now(timezone.utc)
            )
            
            self._events.append(stored_event)
            self._event_id_index[event_id] = len(self._events) - 1
            
            logger.debug(f"Enqueued event with event_id: {event_id}")
        
        # Call parent enqueue_event to maintain compatibility with asyncio.Queue
        # This puts the actual event (event_with_id) into the parent's asyncio.Queue,
        # so dequeue_event() will return the actual event, not a StoredEvent.
        # This will also handle child queues (taps)
        await super().enqueue_event(event_with_id)
    
    async def consume_events(
        self, 
        from_event_id: Optional[str] = None,
        consumer_id: Optional[str] = None
    ) -> AsyncIterator[Event]:
        """
        Re-enterable event consumption: consume events from the queue, optionally starting from a specific event_id.
        
        This is the key feature that allows re-entering the event stream from any point.
        
        Args:
            from_event_id: If provided, re-enter and start consuming from this event_id (exclusive).
                          Special value "HEAD" means start from the beginning of the event queue.
                          This allows resuming consumption from any point in the event history.
            consumer_id: Optional consumer identifier for tracking position across multiple calls
        
        Yields:
            Events from the queue, starting from the specified event_id or from the beginning
        """
        # Start cleanup task if not already started (lazy initialization)
        await self._start_cleanup_task()
        
        async with self._storage_lock:
            start_index = len(self._events)
            is_reconsuming = False
            
            if from_event_id:
                # Special event_id "head" means start from the beginning
                if from_event_id == "HEAD":
                    start_index = 0
                    is_reconsuming = len(self._events) > 0
                    if is_reconsuming:
                        logger.info(f"Reconsuming events from HEAD (beginning), total events: {len(self._events)}, consumer_id: {consumer_id}")
                # Find the index of the event with this event_id
                elif from_event_id in self._event_id_index:
                    # Start from the next event after the one with this event_id
                    start_index = self._event_id_index[from_event_id] + 1
                    is_reconsuming = start_index < len(self._events)
                    if is_reconsuming:
                        logger.info(f"Reconsuming events from event_id: {from_event_id}, starting at index: {start_index}, remaining events: {len(self._events) - start_index}, consumer_id: {consumer_id}")
                else:
                    logger.warning(f"Event with event_id {from_event_id} not found, starting from beginning")
                    start_index = 0
                    is_reconsuming = len(self._events) > 0
                    if is_reconsuming:
                        logger.info(f"Reconsuming events from beginning (event_id not found), total events: {len(self._events)}, consumer_id: {consumer_id}")
            elif consumer_id and consumer_id in self._consumers:
                # Resume from last consumed position
                start_index = self._consumers[consumer_id]
                is_reconsuming = start_index < len(self._events)
                if is_reconsuming:
                    logger.info(f"Reconsuming events for consumer_id: {consumer_id}, resuming from index: {start_index}, remaining events: {len(self._events) - start_index}")
            
            # Create a snapshot of events to yield (release lock before yielding)
            events_to_yield = [(i, self._events[i]) for i in range(start_index, len(self._events))]
        
        # Yield events outside the lock to avoid blocking
        for i, stored_event in events_to_yield:
            # Update consumer position (need lock for this)
            if consumer_id:
                async with self._storage_lock:
                    self._consumers[consumer_id] = i + 1
            
            # Log reconsumed events with details
            if is_reconsuming:
                event_details = self._format_event_details(stored_event.event)
                logger.info(
                    f"Reconsumed event - event_id: {stored_event.event_id}, "
                    f"index: {i}, consumer_id: {consumer_id}, "
                    f"stored_timestamp: {stored_event.timestamp.isoformat()}, "
                    f"event_details: [{event_details}]"
                )
            
            yield stored_event.event
    
    async def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """
        Get an event by its event_id.
        
        Args:
            event_id: The event_id to look up
            
        Returns:
            The event if found, None otherwise
        """
        # Start cleanup task if not already started (lazy initialization)
        await self._start_cleanup_task()
        
        async with self._storage_lock:
            if event_id in self._event_id_index:
                index = self._event_id_index[event_id]
                return self._events[index].event
            return None
    
    async def get_all_event_ids(self) -> List[str]:
        """
        Get all event_ids currently stored in the queue.
        
        Returns:
            List of event_ids
        """
        # Start cleanup task if not already started (lazy initialization)
        await self._start_cleanup_task()
        
        async with self._storage_lock:
            return [stored.event_id for stored in self._events]
    
    async def close(self, immediate: bool = False) -> None:
        """Close the queue and clean up resources.
        
        Args:
            immediate: If True, immediately closes and clears events. If False, waits for queue to drain.
        """
        # Cancel cleanup task
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Clear stored events
        async with self._storage_lock:
            self._events.clear()
            self._event_id_index.clear()
            self._consumers.clear()
        
        # Call parent close to handle asyncio.Queue and child queues
        await super().close(immediate=immediate)
    
    def tap(self) -> 'HolosEventQueue':
        """Taps the event queue to create a new child queue that receives all future events.
        
        Overrides parent method to return a HolosEventQueue instead of regular EventQueue,
        ensuring child queues also have re-enterability features.
        
        Returns:
            A new `HolosEventQueue` instance that will receive all events enqueued
            to this parent queue from this point forward.
        """
        logger.debug('Tapping HolosEventQueue to create a child queue.')
        # Create a new HolosEventQueue with same retention settings
        queue = HolosEventQueue(
            retention_seconds=self._retention_seconds,
            cleanup_interval_seconds=self._cleanup_interval,
            max_queue_size=self.queue.maxsize
        )
        # Add to parent's children list (inherited from EventQueue)
        self._children.append(queue)
        return queue
    
    async def clear_events(self, clear_child_queues: bool = True) -> None:
        """Clears all events from the current queue and optionally all child queues.
        
        Overrides parent method to also clear stored events for re-enterability.
        
        Args:
            clear_child_queues: If True (default), clear all child queues as well.
                              If False, only clear the current queue, leaving child queues untouched.
        """
        # Clear stored events for re-enterability
        async with self._storage_lock:
            self._events.clear()
            self._event_id_index.clear()
            self._consumers.clear()
        
        # Call parent to clear asyncio.Queue and child queues
        await super().clear_events(clear_child_queues)
    
    def __aiter__(self) -> AsyncIterator[Event]:
        """
        Make the queue iterable, consuming all events from the beginning.
        
        Note: This creates a new consumer for each iteration.
        Use consume_events() for more control over consumption.
        """
        # Create a unique consumer_id for this iteration
        consumer_id = f"__aiter___{uuid.uuid4()}"
        return self.consume_events(consumer_id=consumer_id)


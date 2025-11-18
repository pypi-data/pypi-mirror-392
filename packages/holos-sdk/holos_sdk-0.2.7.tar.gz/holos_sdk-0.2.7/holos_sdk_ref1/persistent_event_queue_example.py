"""
Example usage of PersistentEventQueue and PersistentQueueManager.

This file demonstrates how to use the re-enterable event queue to replace
the default a2a event queue. The key feature is the ability to re-enter
and consume events from any event_id, enabling resumable event processing.
"""

import asyncio
from a2a.types import Message, Part, TextPart, Role
from holos_sdk import PersistentEventQueue, PersistentQueueManager, HolosRequestHandler
from holos_sdk.types import Plan


async def example_persistent_event_queue():
    """Example of using PersistentEventQueue with re-enterability (key feature)."""
    # Create a re-enterable event queue (24 hours = 86400 seconds)
    queue = PersistentEventQueue(retention_seconds=86400)
    
    # Create some events
    message1 = Message(
        message_id="msg-1",
        role=Role.user,
        parts=[Part(root=TextPart(text="Hello"))]
    )
    
    plan1 = Plan(goal="Complete task")
    
    # Enqueue events (event_id will be auto-added to metadata)
    await queue.enqueue_event(message1)
    await queue.enqueue_event(plan1)
    
    # Get the event_id from the first event's metadata
    first_event_id = None
    async for event in queue.consume_events():
        if isinstance(event, Message):
            first_event_id = event.metadata.get('event_id')
            print(f"First event_id: {first_event_id}")
            break
    
    # KEY FEATURE: Re-enter and consume events from a specific event_id
    # This allows resuming event processing from any point in the history
    print("\nRe-entering from event_id (key feature):")
    async for event in queue.consume_events(from_event_id=first_event_id):
        print(f"Event type: {type(event).__name__}")
        if hasattr(event, 'metadata') and event.metadata:
            print(f"  event_id: {event.metadata.get('event_id')}")
    
    # Get event by event_id
    if first_event_id:
        event = await queue.get_event_by_id(first_event_id)
        if event:
            print(f"\nRetrieved event by ID: {type(event).__name__}")
    
    # Clean up
    await queue.close()


async def example_persistent_queue_manager():
    """Example of using PersistentQueueManager with HolosRequestHandler."""
    # Create a persistent queue manager (24 hours = 86400 seconds)
    queue_manager = PersistentQueueManager(retention_seconds=86400)
    
    # Get a queue (this will be used by the request handler)
    queue = queue_manager.get_queue("task-queue-1")
    
    # The queue is a PersistentEventQueue instance
    assert isinstance(queue, PersistentEventQueue)
    
    # Use it with HolosRequestHandler
    # (In real usage, you would pass this to HolosRequestHandler)
    # handler = HolosRequestHandler(
    #     agent_executor=your_executor,
    #     task_store=your_task_store,
    #     queue_manager=queue_manager,  # Use persistent queue manager
    #     tracer=your_tracer
    # )
    
    # Clean up
    await queue_manager.close()


async def example_consume_from_event_id():
    """Example demonstrating the key re-enterability feature: consuming from a specific event_id."""
    queue = PersistentEventQueue()
    
    # Enqueue multiple events
    for i in range(5):
        message = Message(
            message_id=f"msg-{i}",
            role=Role.user,
            parts=[Part(root=TextPart(text=f"Message {i}"))]
        )
        await queue.enqueue_event(message)
    
    # Get all event_ids
    event_ids = await queue.get_all_event_ids()
    print(f"Total events: {len(event_ids)}")
    
    # KEY FEATURE: Re-enter from the 3rd event_id (skip first 2)
    # This demonstrates resumable event processing - you can jump to any point
    if len(event_ids) >= 3:
        start_event_id = event_ids[2]
        print(f"\nRe-entering from event_id: {start_event_id} (skipping first 2 events)")
        
        count = 0
        async for event in queue.consume_events(from_event_id=start_event_id):
            count += 1
            print(f"  Event {count}: {type(event).__name__}")
        
        print(f"Consumed {count} events starting from event_id")
    
    await queue.close()


if __name__ == "__main__":
    print("=== Example 1: Direct PersistentEventQueue usage ===")
    asyncio.run(example_persistent_event_queue())
    
    print("\n=== Example 2: PersistentQueueManager usage ===")
    asyncio.run(example_persistent_queue_manager())
    
    print("\n=== Example 3: Consume from event_id ===")
    asyncio.run(example_consume_from_event_id())


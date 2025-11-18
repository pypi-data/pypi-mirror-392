import logging
from collections.abc import AsyncGenerator
from a2a.utils import artifact
from a2a.utils.artifact import new_artifact
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.agent_execution import AgentExecutor, RequestContextBuilder
from a2a.server.context import ServerCallContext
from a2a.server.events import Event, EventConsumer, QueueManager
from a2a.server.tasks import (
    PushNotificationConfigStore,
    PushNotificationSender,
    ResultAggregator,
    TaskManager,
    TaskStore,
)
from a2a.types import (
    Message,
    MessageSendParams,
    Task,
    TaskIdParams,
    TaskState,
    TaskStatusUpdateEvent,
    TaskArtifactUpdateEvent,
    TaskNotFoundError,
    InvalidParamsError,
)
from a2a.utils.errors import ServerError

from holos_sdk.utils import plan_to_message, try_convert_to_plan
from .plant_tracer import PlantTracer, no_op_tracer
from .types import Plan, Assignment, TaskArtifact
from .holos_queue_manager import HolosQueueManager
from .holos_event_queue import HolosEventQueue

logger = logging.getLogger(__name__)


class HolosRequestHandler(DefaultRequestHandler):
    """
    Holos request handler that extends DefaultRequestHandler with tracing functionality.
    
    This handler adds tracing to:
    1. on_message_send - consumes incoming objects and traces results
    2. on_message_send_stream - consumes incoming objects, tries to convert to Plan, and traces all events
    """
    
    def __init__(
        self,
        agent_executor: AgentExecutor,
        task_store: TaskStore,
        queue_manager: QueueManager | None = None,
        push_config_store: PushNotificationConfigStore | None = None,
        push_sender: PushNotificationSender | None = None,
        request_context_builder: RequestContextBuilder | None = None,
        tracer: PlantTracer = no_op_tracer,
    ) -> None:
        """
        Initialize the Holos request handler.
        
        Args:
            agent_executor: The AgentExecutor instance to run agent logic
            task_store: The TaskStore instance to manage task persistence
            queue_manager: The QueueManager instance to manage event queues. 
                          If None, defaults to HolosQueueManager for re-enterable event queues.
            push_config_store: The PushNotificationConfigStore instance for managing push notification configurations
            push_sender: The PushNotificationSender instance for sending push notifications
            request_context_builder: The RequestContextBuilder instance used to build request contexts
            tracer: PlantTracer instance for submitting tracing data
        """
        # Use HolosQueueManager by default if no queue_manager is provided
        if queue_manager is None:
            queue_manager = HolosQueueManager()
        
        super().__init__(
            agent_executor=agent_executor,
            task_store=task_store,
            queue_manager=queue_manager,
            push_config_store=push_config_store,
            push_sender=push_sender,
            request_context_builder=request_context_builder,
        )
        self._tracer = tracer

    def _ensure_tracer_in_context(self, context: ServerCallContext | None = None) -> ServerCallContext:
        """
        Ensure the tracer is available in the context.
        
        Creates a request-scoped copy of the tracer to prevent race conditions
        when handling multiple concurrent requests. Each request gets its own
        tracer instance with isolated state (consumed_objects, produced_objects).
        
        If context is provided, add the request-scoped tracer to its state.
        If context is None, create a new ServerCallContext with the request-scoped tracer.
        
        Args:
            context: The server call context (can be None)
            
        Returns:
            ServerCallContext with request-scoped tracer in state
        """
        # Create a request-scoped copy to prevent race conditions
        request_tracer = self._tracer.create_request_scoped_copy()
        
        if context is not None:
            context.state['tracer'] = request_tracer
            return context
        else:
            return ServerCallContext(state={'tracer': request_tracer})

    async def _trace_event(self, event: Event, tracer: PlantTracer) -> None:
        """
        Trace an event using the provided tracer.
        
        Args:
            event: The event to trace
            tracer: The request-scoped tracer to use for tracing
        """
        try:
            if isinstance(event, (Message, Task)):
                await tracer.submit_object_produced(event)
            elif isinstance(event, Assignment):
                await tracer.submit_object_produced_consumed(event)
            elif isinstance(event, TaskStatusUpdateEvent):
                await tracer.submit_object_updated(event)
            elif isinstance(event, TaskArtifactUpdateEvent):
                task = await self.task_store.get(event.task_id)
                if (event.last_chunk is None or event.last_chunk == True) and task.artifacts:
                    for artifact in task.artifacts:
                        if artifact.artifact_id == event.artifact.artifact_id:
                            task_artifact = TaskArtifact(
                                artifact=artifact,
                                context_id=event.context_id,
                                task_id=event.task_id,
                            )
                            await tracer.submit_object_produced(task_artifact)
                            break
            #No need to submit plan, the client will submit it
            # elif isinstance(event, Plan):
            #     tracer.submit_object_produced(event)
        
        except Exception as e:
            logger.error(f"Error in _trace_event: {e}", exc_info=True)
    
    async def on_message_send(
        self,
        params: MessageSendParams,
        context: ServerCallContext | None = None,
    ) -> Message | Task:
        """
        Handle message send with tracing.
        
        This follows the server-side pattern where we consume the incoming request
        object before processing (opposite of client-side which produces before sending).
        """
        context = self._ensure_tracer_in_context(context)
        request_tracer = context.state['tracer']
        await request_tracer.submit_object_consumed(params.message)
        
        result = await super().on_message_send(params, context)
        await self._trace_event(result, request_tracer)
        
        return result
    
    async def on_message_send_stream(
        self,
        params: MessageSendParams,
        context: ServerCallContext | None = None,
    ) -> AsyncGenerator[Event]:
        """
        Handle message send stream with tracing.
        
        This follows the server-side pattern:
        1. Consume the incoming request object (server-side receives)
        2. Try to convert to Plan and resubmit if successful (following client-side pattern)
        """

        context = self._ensure_tracer_in_context(context)
        request_tracer = context.state['tracer']
        await request_tracer.submit_object_consumed(params.message)
        plan = try_convert_to_plan(params.message)
        if plan:
            plans_to_submit = [plan]
            submitted_plans = set()
            while plans_to_submit:
                cur_plan = plans_to_submit.pop(0)
                if cur_plan.id in submitted_plans:
                    continue
                await request_tracer.submit_object_consumed(cur_plan)
                submitted_plans.add(cur_plan.id)
                plans_to_submit.extend(cur_plan.depend_plans)

        responsed_context_id = None
        responsed_task_id = None
        async for event in super().on_message_send_stream(params, context):
            await self._trace_event(event, request_tracer)

            if isinstance(event, Task):
                responsed_task_id = event.id
                responsed_context_id = event.context_id

            #just yielding a2a.types
            if isinstance(event, Event):
                yield event
            elif isinstance(event, Plan):
                plan_message = plan_to_message(event)
                task_artifact_update_event = TaskArtifactUpdateEvent(
                    artifact=new_artifact(plan_message.parts, name="plan_message"),
                    context_id=responsed_context_id,
                    task_id=responsed_task_id,
                )
                task_artifact = TaskArtifact(
                    artifact=task_artifact_update_event.artifact,
                    context_id=task_artifact_update_event.context_id,
                    task_id=task_artifact_update_event.task_id
                )
                await request_tracer.submit_object_produced(task_artifact)
                yield task_artifact_update_event
    
    async def on_resubscribe_to_task(
        self,
        params: TaskIdParams,
        context: ServerCallContext | None = None,
    ) -> AsyncGenerator[Event]:
        """
        Handle resubscribe with support for re-entering from event_id.
        
        If task.metadata contains a 'from_event_id', and the queue_manager is a HolosQueueManager,
        this will use the re-enterable consume_events() to start from that event_id, but still
        processes events through ResultAggregator and EventConsumer to maintain task state updates
        and proper error handling.
        Otherwise, falls back to the standard implementation.
        """
        logger.info(f"on_resubscribe_to_task called for task_id: {params.id}")
        
        task: Task | None = await self.task_store.get(params.id, context)
        if not task:
            logger.error(f"Task {params.id} not found in task_store")
            raise ServerError(error=TaskNotFoundError())
        
        task_state = task.status.state if task.status else None
        logger.info(f"Task {params.id} found, state: {task_state}")
        
        # Check if task is in a terminal state
        terminal_states = {TaskState.completed, TaskState.canceled, TaskState.failed, TaskState.rejected}
        is_terminal = task_state in terminal_states if task_state else False
        if is_terminal:
            logger.info(f"Task {params.id} is in terminal state {task_state}")
        
        # Create TaskManager and ResultAggregator (same as default implementation)
        task_manager = TaskManager(
            task_id=task.id,
            context_id=task.context_id,
            task_store=self.task_store,
            initial_message=None,
            context=context,
        )
        result_aggregator = ResultAggregator(task_manager)
        
        # Check if we should use re-enterable consumption
        # from_event_id should come from the request params first, then fall back to task metadata
        from_event_id = None
        if params.metadata and isinstance(params.metadata, dict):
            from_event_id = params.metadata.get('from_event_id')
            logger.info(f"Request params metadata contains from_event_id: {from_event_id} for task {params.id}")
        elif task.metadata and isinstance(task.metadata, dict):
            from_event_id = task.metadata.get('from_event_id')
            logger.info(f"Task {params.id} metadata contains from_event_id: {from_event_id} (from stored task)")
        else:
            logger.info(f"No from_event_id found in params.metadata or task.metadata for task {params.id}")
        
        # If we have an event_id and HolosQueueManager, use re-enterable consumption
        # This works even for terminal tasks to replay events
        logger.info(f"Checking conditions for re-enterable consumption for task {params.id}: from_event_id={from_event_id}, queue_manager_type={type(self._queue_manager).__name__}")
        
        if from_event_id and isinstance(self._queue_manager, HolosQueueManager):
            logger.info(f"✓ Conditions met: from_event_id exists and queue_manager is HolosQueueManager for task {params.id}")
            logger.info(f"Attempting re-enterable consumption for task {params.id} with from_event_id: {from_event_id}")
            holos_queue = self._queue_manager.get_holos_queue(params.id)
            logger.info(f"Retrieved queue for task {params.id}: queue={holos_queue}, queue_type={type(holos_queue).__name__ if holos_queue else None}")
            
            if holos_queue and isinstance(holos_queue, HolosEventQueue):
                logger.info(f"✓ Queue is HolosEventQueue for task {params.id}")
                event = None
                if from_event_id == "HEAD":
                    logger.info(f"Re-entering task {params.id} from beginning (HEAD)")
                else:
                    logger.info(f"Re-entering task {params.id} from event_id: {from_event_id}")
                    # Check if event_id exists first
                    event = await holos_queue.get_event_by_id(from_event_id)
                    logger.info(f"Event lookup result for event_id {from_event_id}: event={'found' if event else 'not found'}")
                    if event is None:
                        logger.warning(f"Event with event_id {from_event_id} not found in queue for task {params.id}, falling back to standard resubscribe")
                    else:
                        logger.info(f"Event with event_id {from_event_id} found, starting re-enterable consumption")
                
                if from_event_id == "HEAD" or (from_event_id != "HEAD" and event is not None):
                    logger.info(f"✓ Starting re-enterable consumption for task {params.id} with from_event_id={from_event_id}")
                    event_count = 0
                    async for event in holos_queue.consume_events(from_event_id=from_event_id):
                        event_count += 1
                        if not is_terminal:
                            await task_manager.process(event)
                        yield event
                    logger.info(f"Re-enterable consumption completed for task {params.id}, processed {event_count} events")
                    return
                logger.warning(f"✗ Cannot start re-enterable consumption: from_event_id={from_event_id}, event={'found' if event else 'not found'}, falling back to standard resubscribe")
            else:
                logger.warning(f"✗ Queue check failed for task {params.id}: holos_queue={'exists' if holos_queue else 'None'}, is_HolosEventQueue={isinstance(holos_queue, HolosEventQueue) if holos_queue else False}, falling back to standard resubscribe")
        else:
            if not from_event_id:
                logger.info(f"✗ No from_event_id provided for task {params.id} (from_event_id={from_event_id}), using standard resubscribe")
            elif not isinstance(self._queue_manager, HolosQueueManager):
                logger.info(f"✗ Queue manager is not HolosQueueManager for task {params.id} (type={type(self._queue_manager).__name__}), using standard resubscribe")

        # For terminal tasks without from_event_id, try to get events from queue if available
        if is_terminal:
            logger.info(f"Task {params.id} is in terminal state {task_state}, attempting to get events from queue")
            logger.info(f"Checking queue for terminal task {params.id}: queue_manager_type={type(self._queue_manager).__name__}")
            if isinstance(self._queue_manager, HolosQueueManager):
                logger.info(f"✓ Queue manager is HolosQueueManager for terminal task {params.id}")
                holos_queue = self._queue_manager.get_holos_queue(params.id)
                logger.info(f"Retrieved queue for terminal task {params.id}: queue={holos_queue}, queue_type={type(holos_queue).__name__ if holos_queue else None}")
                if holos_queue and isinstance(holos_queue, HolosEventQueue):
                    logger.info(f"✓ Queue is HolosEventQueue for terminal task {params.id}, replaying events from HEAD")
                    event_count = 0
                    async for event in holos_queue.consume_events(from_event_id="HEAD"):
                        event_count += 1
                        yield event
                    logger.info(f"Replayed {event_count} events for terminal task {params.id}")
                    return
                else:
                    logger.info(f"✗ Queue check failed for terminal task {params.id}: holos_queue={'exists' if holos_queue else 'None'}, is_HolosEventQueue={isinstance(holos_queue, HolosEventQueue) if holos_queue else False}")
            else:
                logger.info(f"✗ Queue manager is not HolosQueueManager for terminal task {params.id} (type={type(self._queue_manager).__name__})")
            # If no queue available, just yield the task
            logger.info(f"No queue available for terminal task {params.id}, yielding task only")
            yield task
            return

        logger.info(f"Using standard resubscribe for task {params.id} (reached end of decision tree)")
        queue = await self._queue_manager.tap(task.id)
        if not queue:
            logger.error(f"Failed to tap queue for task {params.id}")
            raise ServerError(error=TaskNotFoundError())

        consumer = EventConsumer(queue)
        event_count = 0
        async for event in result_aggregator.consume_and_emit(consumer):
            event_count += 1
            yield event
        logger.info(f"Standard resubscribe completed for task {params.id}, processed {event_count} events")

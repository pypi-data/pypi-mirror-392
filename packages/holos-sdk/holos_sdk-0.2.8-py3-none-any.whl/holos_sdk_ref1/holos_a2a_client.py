"""
HolosTracingA2AClient - A client wrapper that adds response tracing to A2A clients.
"""

import asyncio
import logging
from collections.abc import AsyncIterator
from typing import Optional
from a2a.client.base_client import BaseClient
from a2a.client.client import Client, ClientCallContext, ClientEvent
from a2a.client.errors import A2AClientHTTPError
from a2a.types import Message, Task, TaskQueryParams, TaskIdParams, TaskPushNotificationConfig, GetTaskPushNotificationConfigParams, AgentCard, TaskArtifactUpdateEvent
from .plant_tracer import PlantTracer
from .types import Plan, TaskArtifact, Assignment
from .utils import plan_to_message

logger = logging.getLogger(__name__)


class HolosTracingA2AClient(Client):
    """
    A client wrapper that adds request and response tracing to A2A clients.
    
    This client handles both request and response tracing for:
    1. send_message - submits produced object before sending, consumed object after receiving response
    2. resubscribe - submits consumed object for message/task objects, ignores A2A events
    3. send_plan_streaming - submits plan as produced, converts to message and calls send_message
    """

    def __init__(self, base_client: BaseClient, tracer: PlantTracer):
        """
        Initialize the tracing client.
        
        Args:
            base_client: The underlying BaseClient instance
            tracer: PlantTracer instance for submitting tracing data, may be the no_op_tracer
        """
        super().__init__(base_client._consumers, base_client._middleware)
        self._base_client = base_client
        self._tracer = tracer
        self._card = base_client._card
        self._config = base_client._config
        self._transport = base_client._transport

    async def _handle_response_iterator( self, 
        response_iterator: AsyncIterator[ClientEvent | Message], 
        enable_retry: bool = True, 
        max_retries: int = 3,
        context: ClientCallContext | None = None,
    ) -> AsyncIterator[ClientEvent | Message]:
        """
        Helper method to handle response iterator and trace responses.
        
        This extracts the duplicated response tracing logic from send_message and resubscribe.
        Optionally handles retry logic for A2AClientHTTPError.
        
        Args:
            response_iterator: The async iterator of responses to process
            enable_retry: Whether to enable retry logic (default: True)
            max_retries: Maximum number of retries (default: 3)
            context: Client call context
        Yields:
            The same responses after tracing them
        """
        retry_count = 0
        task_id = None
        last_event_id = None  # Initialize to None in case server doesn't return event_id
        
        while retry_count <= max_retries:
            try:
                async for response in response_iterator:
                    last_event_id = self._extract_event_id(response)
                    #trace response
                    if isinstance(response, Message):
                        await self._tracer.submit_object_consumed(response)
                    elif isinstance(response, tuple):
                        response_task, response_event = response
                        task_id = response_task.id

                        if response_event is None:
                            await self._tracer.submit_object_consumed(response_task)
                        elif isinstance(response_event, TaskArtifactUpdateEvent):
                            if response_event.last_chunk is None or response_event.last_chunk == True:
                                for artifact in response_task.artifacts:
                                    if artifact.artifact_id == response_event.artifact.artifact_id:
                                        task_artifact = TaskArtifact(
                                            artifact=artifact,
                                            context_id=response_event.context_id,
                                            task_id=response_event.task_id,
                                        )
                                        await self._tracer.submit_object_consumed(task_artifact)
                                        break
                    yield response
                break
                
            except A2AClientHTTPError as e:
                if not enable_retry:
                    raise
                
                # If no last_event_id, don't reconnect (server doesn't support event_id tracking)
                if last_event_id is None:
                    logger.warning(
                        f"Request failed with HTTP error {e.status_code}: {e.message}. "
                        f"No event_id available, skipping retry (normal a2a-sdk behavior)."
                    )
                    raise
                
                retry_count += 1
                if retry_count > max_retries:
                    logger.error(f"Request failed after {max_retries} retries: {e}")
                    raise
                
                logger.warning(
                    f"Request failed with HTTP error {e.status_code}: {e.message}. "
                    f"Retrying ({retry_count}/{max_retries})..."
                )

                await asyncio.sleep(1)
                # Build metadata for retry with event_id
                request = TaskIdParams(id=task_id, metadata={'from_event_id': last_event_id})
                response_iterator = self._base_client.resubscribe(request, context=context)


    def _extract_event_id(self, response: ClientEvent | Message) -> Optional[str]:
        if isinstance(response, Message):
            if hasattr(response, 'metadata') and isinstance(response.metadata, dict):
                return response.metadata.get('event_id', None)
        elif isinstance(response, tuple):
            response_task, response_event = response
            if response_event is not None:
                if hasattr(response_event, 'metadata') and isinstance(response_event.metadata, dict):
                    return response_event.metadata.get('event_id', None)
            else:
                if hasattr(response_task, 'metadata') and response_task.metadata is not None and isinstance(response_task.metadata, dict):
                    return response_task.metadata.get('event_id', None)
        return None


    async def send_message(self, request: Message, *, context: ClientCallContext | None = None, from_objects = None) -> AsyncIterator[ClientEvent | Message]:
        await self._tracer.submit_object_produced(request, from_objects)

        assignment = Assignment(
            object_id=request.message_id,
            assignee_id=self._card.url,
            assignee_name=self._card.name,
        )
        await self._tracer.submit_object_produced_consumed(assignment)

        response_iterator = self._base_client.send_message(request, context=context)
        async for response in self._handle_response_iterator(response_iterator, context=context):
            yield response

    async def resubscribe(self, request: TaskIdParams, *, context: ClientCallContext | None = None,) -> AsyncIterator[ClientEvent]:
        """
        Resubscribe to a task's event stream with retry logic and re-enterable event support.
        """
        # Get the response iterator from base client
        response_iterator = self._base_client.resubscribe(request, context=context)
        
        # Process responses with retry logic enabled (enabled by default)
        async for response in self._handle_response_iterator(response_iterator, context=context):
            yield response

    async def send_plan_streaming( self, plan: Plan, context: Optional[ClientCallContext] = None, from_objects = None) -> AsyncIterator[ClientEvent | Message]:
        """
        Send a plan using streaming and submit tracing data.
        
        This function is specifically for planning agents:
        1. Submits the plan as produced
        2. Converts plan to message and calls send_message
        3. send_message will handle its own tracing for the converted message
        
        Args:
            plan: The Plan object to send
            context: Optional client call context
            
        Returns:
            The result from send_message (which will be streaming)
        """
        try:
            plans_to_submit = [plan]
            submitted_plans = set()
            while plans_to_submit:
                cur_plan = plans_to_submit.pop(0)
                if cur_plan.id in submitted_plans:
                    continue
                await self._tracer.submit_object_produced(cur_plan, from_objects)
                submitted_plans.add(cur_plan.id)
                plans_to_submit.extend(cur_plan.depend_plans)

            message = plan_to_message(plan)
            message_from_objects = [plan.id]
            async for response in self.send_message(message, context=context, from_objects=message_from_objects):
                yield response
        except Exception as e:
            logger.error(f"Error in send_plan_streaming: {e}")
            raise
    

    #--- just call base client

    async def get_task( self, request: TaskQueryParams, *, context: ClientCallContext | None = None,) -> Task:
        return await self._base_client.get_task(request, context=context)
    
    async def cancel_task( self, request: TaskIdParams, *, context: ClientCallContext | None = None,) -> Task:
        return await self._base_client.cancel_task(request, context=context)
    
    async def set_task_callback( self, request: TaskPushNotificationConfig, *, context: ClientCallContext | None = None,) -> TaskPushNotificationConfig:
        return await self._base_client.set_task_callback(request, context=context)
    
    async def get_task_callback( self, request: GetTaskPushNotificationConfigParams, *, context: ClientCallContext | None = None,) -> TaskPushNotificationConfig:
        return await self._base_client.get_task_callback(request, context=context)
    
    async def get_card( self, *, context: ClientCallContext | None = None) -> AgentCard:
        return await self._base_client.get_card(context=context)
    
    async def close(self) -> None:
        await self._base_client.close()

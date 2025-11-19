# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from typing import Iterable, Tuple
import time

from google.protobuf.any_pb2 import Any

from cegalprizm.hub import TaskContext

from .. import logger
from ..hub_helper import _get_hub_user_identity
from ..workflow_library import get_workflow_info
from ..value_parameters import get_value_from_payload
from ..pycoderunner_pb2 import RunWellKnownWorkflowRequest, StringValuePayload
from .run_workflow_mp_queue import RunWorkflowMpQueue
from .run_workflow_process_pool import RunWorkflowProcessPool

def RunWorkflow(ctx: TaskContext, payload: Any) -> Iterable[Tuple[bool, bool, Any, str]]:
    identity = _get_hub_user_identity(ctx.metadata)
    start_time = time.time()
    logger.info(f"Run workflow request: Identity: '{identity}'")
    request = RunWellKnownWorkflowRequest()
    payload.Unpack(request)

    parameters = None
    context_id = None
    session_id = None
    workflow_target_connector_id = None
    if request.parameters is not None:
        params = {}
        for item in request.parameters.dict.items():
            input = get_value_from_payload(item[1])
            if input[0]:
                if input[1] is not None:
                    params[item[0]] = input[1]
            else:
                parameter = item[1]
                if parameter.content_type == "__contextId":
                    context_id_payload = StringValuePayload()
                    parameter.content.Unpack(context_id_payload)
                    context_id = context_id_payload.value
                elif parameter.content_type == "__sessionId":
                    session_id_payload = StringValuePayload()
                    parameter.content.Unpack(session_id_payload)
                    session_id = session_id_payload.value
                elif parameter.content_type == "__workflowTargetConnectorId":
                    workflow_target_connector_id = StringValuePayload()
                    parameter.content.Unpack(workflow_target_connector_id)
                    workflow_target_connector_id = workflow_target_connector_id.value

        parameters = {}
        parameters['parameters'] = params

    metadata = {}
    for key in ctx.metadata.keys():
        metadata[key] = ctx.metadata[key]

    logger.info(f"Parameters : {parameters}")

    info = get_workflow_info(request.workflow_id)
    if info is None:
        yield (False, True, None, f"Workflow with id {request.workflow_id} not found")
        return
    live_output = request.live_output if hasattr(request, 'live_output') else True
    logger.info(f"Running workflow: WorkflowName: '{info.name}' WorkflowId: '{request.workflow_id}' Identity: '{identity}' LiveOutput: '{live_output}'")

    if live_output:
        yield from RunWorkflowMpQueue(
            ctx,
            info,
            parameters,
            metadata,
            context_id,
            session_id,
            workflow_target_connector_id,
        )
    else:
        yield from RunWorkflowProcessPool(
            ctx,
            info,
            parameters,
            metadata,
            context_id,
            session_id,
            workflow_target_connector_id,
        )

    end_time = time.time()
    logger.info(f"Run workflow completed: WorkflowName: '{info.name}' WorkflowId: '{request.workflow_id}' Duration: {end_time - start_time:.2f} seconds")

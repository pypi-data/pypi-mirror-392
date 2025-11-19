# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from typing import Iterable, Tuple
import multiprocessing as mp
import time
import os

from google.protobuf.any_pb2 import Any
from cegalprizm.hub import TaskContext

from .. import logger
from ..hub_helper import _set_hub_user_access
from ..workflow_library import run_workflow

def _run_mp_queue(input_q: mp.Queue, output_q: mp.Queue, done_event: mp.Event):
    (info, parameters, metadata, context_id, session_id, workflow_target_connector_id) = input_q.get()
    _set_hub_user_access(metadata)
    if context_id is not None:
        os.environ['workflow_context_id'] = context_id
    if session_id is not None:
        os.environ['session_id'] = session_id
    if workflow_target_connector_id is not None:
        os.environ['workflow_target_connector_id'] = workflow_target_connector_id
    for r in run_workflow(info, parameters):
        output_q.put(r)
    done_event.set()


def RunWorkflowMpQueue(
    ctx: TaskContext, 
    info, 
    parameters, 
    metadata, 
    context_id, 
    session_id, 
    workflow_target_connector_id,
) -> Iterable[Tuple[bool, bool, Any, str]]:
    """Execute workflow using multiprocessing queues."""
    mp_ctx = mp.get_context('spawn')
    input_q = mp_ctx.Queue()
    output_q = mp_ctx.Queue()
    done_event = mp_ctx.Event()

    p = mp_ctx.Process(target=_run_mp_queue, args=(input_q, output_q, done_event))
    try:
        p.start()
        input_q.put((info, parameters, metadata, context_id, session_id, workflow_target_connector_id))
        while not done_event.is_set() or not output_q.empty():
            if ctx.cancellation_token.is_cancelled():
                p.terminate()
                time.sleep(0.5)
                if p.is_alive():
                    p.kill()
                yield (False, True, None, "Run script cancelled")
                break
            while not output_q.empty():
                yield output_q.get()
            time.sleep(0.25)
            if not p.is_alive() and p.exitcode != 0:
                logger.warning(f"Workflow terminated for unknown reason: exitcode {p.exitcode}")
                yield (False, True, None, f"Workflow terminated for unknown reason: exitcode {p.exitcode}")
                break
        p.join()
    except Exception as error:
        logger.error(f"Run workflow request: {error} {error.args}")
        yield (False, True, None, f"Workflow terminated for unknown reason: exitcode {p.exitcode}")
    finally:
        p.close()

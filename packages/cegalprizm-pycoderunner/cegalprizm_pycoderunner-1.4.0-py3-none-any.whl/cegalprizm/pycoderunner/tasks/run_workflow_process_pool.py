# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

import atexit
import concurrent.futures
import multiprocessing as mp
from typing import Iterable, Tuple
import time
import threading
import os

from google.protobuf.any_pb2 import Any

from cegalprizm.hub import TaskContext
from .. import globals
from .. import logger
from ..hub_helper import _set_hub_user_access
from ..workflow_library import run_workflow

# Global process pool (Shared between all run workflow requests)
_process_pool = None
_pool_lock = threading.Lock()
_shutdown_timer = None
_last_activity_time = None
_IDLE_TIMEOUT_SECONDS = 30.0

def _schedule_shutdown():
    """Schedule shutdown of process pool after idle timeout."""
    global _shutdown_timer, _last_activity_time

    def _check_and_shutdown():
        global _process_pool, _shutdown_timer, _last_activity_time
        
        with _pool_lock:
            current_time = time.time()
            
            # Check if enough time has passed since last activity
            if _last_activity_time and (current_time - _last_activity_time) >= _IDLE_TIMEOUT_SECONDS:
                shutdown_process_pool()
                
                _shutdown_timer = None
                _last_activity_time = None
            else:
                # Reschedule if there's still time left
                remaining_time = _IDLE_TIMEOUT_SECONDS - (current_time - (_last_activity_time or current_time))
                if remaining_time > 0:
                    _shutdown_timer = threading.Timer(remaining_time, _check_and_shutdown)
                    _shutdown_timer.daemon = True
                    _shutdown_timer.start()
    
    # Cancel existing timer
    if _shutdown_timer:
        _shutdown_timer.cancel()
    
    # Start new timer
    _shutdown_timer = threading.Timer(_IDLE_TIMEOUT_SECONDS, _check_and_shutdown)
    _shutdown_timer.daemon = True
    _shutdown_timer.start()

def shutdown_process_pool():
    global _process_pool
    if _process_pool is not None:
        logger.info("Shutting down idle process pool...")
        try:
            _process_pool.shutdown(wait=True)
            _process_pool = None
            logger.info("Idle process pool shut down successfully")
        except KeyboardInterrupt:
            logger.info("Process pool shutdown interrupted by keyboard interrupt")
        except Exception as e:
            logger.error(f"Error shutting down process pool: {str(e)}")
            try:
                _process_pool.shutdown(wait=True)
                _process_pool = None
            except Exception as e2:
                logger.error(f"Error forcefully shutting down process pool: {str(e2)}")
                pass

def get_process_pool():
    global _process_pool, _last_activity_time
    
    with _pool_lock:
        # Update activity time
        _last_activity_time = time.time()
        
        if _process_pool is None:
            # Create a pool with limited workers to prevent resource exhaustion
            NUM_OF_CONCURRENT_TASKS = globals.get_num_of_concurrent_tasks()
            max_workers = min(NUM_OF_CONCURRENT_TASKS, mp.cpu_count())
            _process_pool = concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)
            # Register cleanup function to run at exit
            atexit.register(cleanup_process_pool)
            logger.info(f"Process pool initialized with {max_workers} workers")
        
        return _process_pool

def reset_pool_timer():
    """Reset the idle timeout timer after workflow completion."""
    global _last_activity_time
    
    with _pool_lock:
        # Update activity time to current time
        _last_activity_time = time.time()
        
        # Schedule shutdown timer
        _schedule_shutdown()

def cleanup_process_pool():
    """Clean up the global process pool."""
    global _process_pool, _shutdown_timer
    
    with _pool_lock:
        # Cancel shutdown timer
        if _shutdown_timer:
            _shutdown_timer.cancel()
            _shutdown_timer = None
        
        shutdown_process_pool()

def _run_workflow_in_process_pool(info, parameters, metadata, context_id, session_id, workflow_target_connector_id):
    """Run workflow in a separate process and return all results."""
    _set_hub_user_access(metadata)
    if context_id is not None:
        os.environ['workflow_context_id'] = context_id
    if session_id is not None:
        os.environ['session_id'] = session_id
    if workflow_target_connector_id is not None:
        os.environ['workflow_target_connector_id'] = workflow_target_connector_id
    
    results = []
    try:
        for r in run_workflow(info, parameters, live_output=False):
            results.append(r)
    except Exception as e:
        results.append((False, True, None, f"Workflow error: {str(e)}"))
    return results

def RunWorkflowProcessPool(
    ctx: TaskContext,
    info, 
    parameters, 
    metadata, 
    context_id, 
    session_id, 
    workflow_target_connector_id,
) -> Iterable[Tuple[bool, bool, Any, str]]:
    
    try:
        pool = get_process_pool()
        future = pool.submit(_run_workflow_in_process_pool, info, parameters, metadata, context_id, session_id, workflow_target_connector_id)
        
        # Poll for results with adaptive timing
        sleep_duration = 0.01
        max_sleep = 0.1
        
        while not future.done():
            if ctx.cancellation_token.is_cancelled():
                future.cancel()  # Try to cancel
                yield (False, True, None, "Run script cancelled")
                return
            
            time.sleep(sleep_duration)
            sleep_duration = min(sleep_duration * 1.2, max_sleep)
        
        ## Get results
        results = future.result(timeout=1.0)
        for result in results:
            yield result
            
    except concurrent.futures.TimeoutError:
        yield (False, True, None, "Workflow execution timed out")
    except Exception as error:
        logger.error(f"Run workflow request: {error}")
        yield (False, True, None, f"Workflow execution failed: {str(error)}")
    finally:
        reset_pool_timer()

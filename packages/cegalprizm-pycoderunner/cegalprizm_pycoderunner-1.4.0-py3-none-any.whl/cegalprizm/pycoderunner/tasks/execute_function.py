# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from typing import Iterable, Tuple

from google.protobuf.any_pb2 import Any


from .. import logger
from ..script_library import get_script
from ..value_parameters import get_value_from_payload, get_payload
from ..pycoderunner_pb2 import ExecutionRequest, ExecutionResponse


def _create_return_payload(output_payload_type: str, output_values: Any):
    try:
        logger.debug(f"Output Type  : {output_payload_type}")
        logger.debug(f"Output Values: {output_values}")

        output = get_payload(output_payload_type, output_values)
        if not output[0]:
            logger.info("output_payload_type")
            return None  # [(False, True, None, f"output_payload_type {output_payload_type} not recognised")]
    except Exception as error:
        logger.error(error)
        return None  # [(False, True, None, f"function results invalid: expected type {output_payload_type}, was type {type(output_values)}")]

    result = ExecutionResponse()
    result.output_payload.content_type = output_payload_type
    result.output_payload.content.Pack(output[1])
    return result


def ExecuteFunctionUnary(payload) -> Tuple[bool, Any, str]:
    logger.info("Execute function request")
    request = ExecutionRequest()
    payload.Unpack(request)

    script = get_script(request.function_id)
    if not script:
        logger.info("Function has not been created")
        return (False, None, "Function has not been created")

    fn = script.find_first_function(request.function_names_to_ignore)
    if fn is None:
        logger.info("ExecuteFunctionUnary: No runnable function found")
        return (False, None, "ExecuteFunctionUnary: No runnable function found")

    try:
        input = get_value_from_payload(request.parameter)
        if input[0]:
            if input[1] is None:
                return (False, None, f"input_payload_type {request.input_payload_type} not recognised")
            else:
                input_values = input[1]
    except Exception:
        return (False, None, f"Exception parsing parameter {request.parameter}")

    return script.run_function(fn, input_values, request.output_payload_type, _create_return_payload)


def ExecuteFunction(payload) -> Iterable[Tuple[bool, bool, Any, str]]:
    logger.info("Execute function request")
    request = ExecutionRequest()
    payload.Unpack(request)

    script = get_script(request.function_id)
    if not script:
        logger.info("Function has not been created")
        return [(False, True, None, "Function has not been created")]

    fn = script.find_first_function(request.function_names_to_ignore)
    if fn is None:
        logger.info("ExecuteFunction: No runnable function found")
        return [(False, True, None, "ExecuteFunction: No runnable function found")]

    try:
        input = get_value_from_payload(request.parameter)
        if input[0]:
            if input[1] is None:
                logger.info("input_payload_type")
                return [(False, True, None, f"input_payload_type {request.input_payload_type} not recognised")]
            else:
                input_values = input[1]
    except Exception:
        logger.info("Exception parsing input_payload_type")
        return [(False, True, None, f"Exception parsing parameter {request.parameter}")]

    if input_values is not None:
        logger.debug(f"Input Type  : {request.parameter.content_type}")
        logger.debug(f"Input Values: {input_values}")

        return script.run_function_async(fn, input_values, request.output_payload_type, _create_return_payload)

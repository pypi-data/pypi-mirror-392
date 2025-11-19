# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from typing import Tuple

from google.protobuf.any_pb2 import Any

from .. import logger
from ..script_library import add_script
from ..pycoderunner_pb2 import CreateFunctionRequest, CreateFunctionResponse


def CreateFunction(payload) -> Tuple[bool, Any, str]:
    logger.info("Create function request")
    request = CreateFunctionRequest()
    payload.Unpack(request)

    if len(request.script) > 0:
        logger.debug("Using script")
        script = request.script
    elif len(request.pickled_object) > 0:
        logger.debug("Using pickled_object")
        script = f"""
import cloudpickle
import base64
pyFunc = cloudpickle.loads(base64.b64decode('{request.pickled_object}'))
        """
    else:
        return (False, None, "Cannot create function")

    result = add_script(script)
    logger.debug(result)
    if not result[0]:
        return (False, None, result[1])

    function_id = result[1]
    logger.info(f"Function cached with id {function_id}")
    response = CreateFunctionResponse()
    response.function_id = function_id

    return (True, response, None)

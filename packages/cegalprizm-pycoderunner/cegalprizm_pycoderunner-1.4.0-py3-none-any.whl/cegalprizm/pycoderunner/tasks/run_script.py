# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from typing import Iterable, Tuple

from google.protobuf.any_pb2 import Any

from cegalprizm.hub import TaskContext

from .. import logger
from ..script import Script
from ..value_parameters import get_value_from_payload
from ..pycoderunner_pb2 import RunScriptRequest


def RunScript(ctx: TaskContext, payload: Any) -> Iterable[Tuple[bool, bool, Any, str]]:
    logger.info("Run script request")
    logger.info(f"metadata: {ctx.metadata}")

    request = RunScriptRequest()
    payload.Unpack(request)

    injected_vars = None
    if request.injected_vars is not None:
        injected_vars = {}
        for item in request.injected_vars.dict.items():
            input = get_value_from_payload(item[1])
            if input[0]:
                if input[1] is not None:
                    injected_vars[item[0]] = input[1]
        if len(injected_vars) == 0:
            injected_vars = None
        logger.debug(f"Injected : {injected_vars}")

    script = Script("temp", request.script)
    if not script.is_valid:
        return [(False, True, None, script.error_message)]

    return script.run_capture_outputs(injected_vars)

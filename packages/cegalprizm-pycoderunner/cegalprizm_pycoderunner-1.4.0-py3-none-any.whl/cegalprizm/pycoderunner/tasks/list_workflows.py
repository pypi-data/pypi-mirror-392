# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from typing import Tuple

from google.protobuf.any_pb2 import Any

from .. import logger
from ..constants import _PWR_IDENTIFIER, _PWR_CLASS_NAME
from ..pycoderunner_pb2 import WellKnownWorkflow, ListWellKnownWorkflowsRequest, ListWellKnownWorkflowsResponse
from ..value_parameters import get_payload
from ..workflow_library import get_environment_name, list_available_workflows, refresh_library


def ListWorkflows(payload: Any) -> Tuple[bool, Any, str]:
    logger.info("List workflows request")
    request = ListWellKnownWorkflowsRequest()
    payload.Unpack(request)

    identifier: str = request.identifier if request.identifier else _PWR_IDENTIFIER
    class_name: str = request.class_name if request.class_name else _PWR_CLASS_NAME

    refresh_library(True, identifier, class_name)

    result = ListWellKnownWorkflowsResponse()
    for workflow_tuple in list_available_workflows():
        try:
            item = WellKnownWorkflow()
            item.environment_name = get_environment_name()
            item.workflow_id = workflow_tuple[0]
            item.name = workflow_tuple[1]._get_name()
            item.category = workflow_tuple[1]._get_category()
            item.description = workflow_tuple[1]._get_description()
            item.authors = workflow_tuple[1]._get_authors()
            item.version = workflow_tuple[1]._get_version()
            item.filepath = workflow_tuple[1]._get_filepath()
            item.is_valid = workflow_tuple[1]._is_valid
            item.is_unlicensed = workflow_tuple[1]._is_unlicensed()
            if item.is_valid:
                for parameter in workflow_tuple[1]._get_parameters():
                    item.inputs.append(parameter.get_wellknown_workflow_input())
                config = get_payload("DictionaryPayload", workflow_tuple[1]._get_configurations())
                if config[0]:
                    item.configurations.CopyFrom(config[1])
            else:
                item.error_message = workflow_tuple[1]._get_error_message()
            for deprecated in workflow_tuple[1]._get_deprecated_imports_used():
                item.deprecated_imports_used.append(deprecated)
            result.workflows.append(item)
        except Exception as e:
            logger.warning(f'{e}')
            logger.warning(f"Exception listing workflow {workflow_tuple[1]._get_filepath()}")

    logger.info("List workflows successful")
    return (True, result, None)

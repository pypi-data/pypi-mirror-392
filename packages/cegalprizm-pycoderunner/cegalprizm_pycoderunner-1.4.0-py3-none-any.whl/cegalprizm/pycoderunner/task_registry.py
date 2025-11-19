# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from cegalprizm.hub import HubTaskRegistry

from .tasks.run_script import RunScript
from .tasks.create_function import CreateFunction
from .tasks.execute_function import ExecuteFunctionUnary, ExecuteFunction
from .tasks.list_workflows import ListWorkflows
from .tasks.run_workflow import RunWorkflow


def get_task_registry() -> HubTaskRegistry:

    registry = HubTaskRegistry()

    registry.register_server_streaming_task(wellknown_payload_identifier="cegal.pycoderunner.run_script",
                                            task=RunScript,
                                            friendly_name="Run script",
                                            description="Runs a script",
                                            payload_auth=None)

    registry.register_unary_task(wellknown_payload_identifier="cegal.pycoderunner.create_function",
                                 task=CreateFunction,
                                 friendly_name="Create function",
                                 description="Compiles the supplied script so that it can be executed as a function",
                                 payload_auth=None)

    registry.register_unary_task(wellknown_payload_identifier="cegal.pycoderunner.execute_function",
                                 task=ExecuteFunctionUnary,
                                 friendly_name="Execute function",
                                 description="Executes a function with the supplied parameters and returns the result",
                                 payload_auth=None)

    registry.register_server_streaming_task(wellknown_payload_identifier="cegal.pycoderunner.execute_function_async",
                                            task=ExecuteFunction,
                                            friendly_name="Execute function",
                                            description="Executes a function with the supplied parameters and returns the result",
                                            payload_auth=None)

    registry.register_unary_task(wellknown_payload_identifier="cegal.pycoderunner.list_workflows",
                                 task=ListWorkflows,
                                 friendly_name="List workflows",
                                 description="Returns a list of all available workflows",
                                 payload_auth=None)

    registry.register_server_streaming_task(wellknown_payload_identifier="cegal.pycoderunner.run_workflow",
                                            task=RunWorkflow,
                                            friendly_name="Run workflow",
                                            description="Run a workflow",
                                            payload_auth=None)

    return registry

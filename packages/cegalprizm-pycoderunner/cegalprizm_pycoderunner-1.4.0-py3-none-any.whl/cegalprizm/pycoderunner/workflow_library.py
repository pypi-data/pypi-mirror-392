# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from typing import Iterable, List, Tuple

import hashlib
import os
import sys
import nbformat as nbf
from google.protobuf.any_pb2 import Any

from . import logger
from .constants import _PWR_IDENTIFIER, _PWR_CLASS_NAME
from .python_code_parser import _DescriptionCode, _ParsedDescription, _PythonCodeParser
from .notebook import Notebook
from .script import Script
from .workflow_description import ScriptTypeEnum, WorkflowDescription, WorkflowInfo


this = sys.modules[__name__]

this.environment_name: str = None
this.working_path: str = None
this.workflow_library_paths: List[str] = None
this.workflow_dict = {}

def get_environment_name():
    return this.environment_name


def initialise_workflow_library(environment_name: str, workflow_library_path: str, working_path: str):
    if environment_name is None or len(environment_name) == 0 or str.isspace(environment_name):
        raise ValueError("environment_name must not be None, empty or whitespace")

    if workflow_library_path is None or len(workflow_library_path) == 0 or str.isspace(workflow_library_path):
        raise ValueError("workflow_library_path must not be None, empty or whitespace")

    if working_path is None or len(working_path) == 0 or str.isspace(working_path):
        raise ValueError("working_path must not be None, empty or whitespace")

    workflow_library_paths_input = list(workflow_library_path.split(";"))
    verified_workflow_library_paths = []
    for path in workflow_library_paths_input:
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            logger.warning(f'Specified library path not valid: {abs_path}')
        elif len(path) == 0 or str.isspace(path): ## Empty input is invalid even if the abs_path is not empty
            logger.warning(f'Specified library path not valid: {path}')
        else:
            verified_workflow_library_paths.append(abs_path)

    if len(verified_workflow_library_paths) == 0:
        raise ValueError("No valid workflow library paths specified, see log for details")

    abs_working_path = os.path.abspath(working_path)
    if not os.path.exists(abs_working_path):
        raise ValueError(f"Specified working path does not exist: {abs_working_path}")

    this.environment_name = environment_name
    this.working_path = abs_working_path
    this.workflow_library_paths = verified_workflow_library_paths

    logger.info(f"working_path: {this.working_path}")
    os.environ['CEGAL_PWR_TASK_WORKING_PATH'] = this.working_path

    refresh_library(True)


def refresh_library(reset_library: bool, identifier: str = _PWR_IDENTIFIER, class_name: str = _PWR_CLASS_NAME):
    if this.workflow_library_paths is None:
        return

    if reset_library:
        this.workflow_dict.clear()

    for workflow_library_path in this.workflow_library_paths:
        logger.info(f'Refreshing library: {workflow_library_path}')

        for path, subdirs, files in os.walk(workflow_library_path):
            if path.endswith(".ipynb_checkpoints"):
                continue

            files.sort()
            
            for name in files:
                if name.endswith("-checkpoint.ipynb"):
                    continue
                if not (name.endswith(".py") or name.endswith(".ipynb")):
                    continue

                filepath = os.path.join(path, name)
                error_message = None

                logger.info(f'Parsing file: {filepath}')

                if os.path.getsize(filepath) == 0:
                    info = WorkflowDescription(name, "Invalid", "", "", "")
                    error_message = f"{filepath} is an empty file"
                    info._set_error_message(error_message)
                    logger.warning(error_message)
                    this.workflow_dict[filepath] = info
                    continue

                hash_md5 = hashlib.md5()
                with open(filepath, mode='rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
                workflow_id = hash_md5.hexdigest()

                if workflow_id in this.workflow_dict.keys():
                    info = WorkflowDescription(name, "Invalid", "", "", "")
                    error_message = f"This workflow already exists in library {filepath}"
                    info._set_error_message(error_message)
                    logger.warning(error_message)
                    this.workflow_dict[filepath] = info
                    continue

                script_type = None
                description = None
                notebook_kernel_info = {}

                with open(filepath, "r") as f:
                    if name.endswith(".py"):
                        script_type = ScriptTypeEnum.PyScript
                        try:
                            description = _PythonCodeParser.parse_workflow_description(name, f.readlines(), identifier, class_name)
                        except UnicodeDecodeError:
                            description = _ParsedDescription(_DescriptionCode(False, error_message=f"Unable to decode all characters in {name}. This may be due to emojis or other special characters."))
                    elif name.endswith(".ipynb"):
                        script_type = ScriptTypeEnum.Notebook
                        try:
                            nb = nbf.read(f, as_version=nbf.NO_CONVERT)
                            notebook_kernel_info = nb.metadata.get("kernelspec", {})
                            for cell in nb.cells:
                                if cell["cell_type"] == "code":
                                    if not description:
                                        description = _PythonCodeParser.parse_workflow_description(name, cell["source"].split("\n"), identifier, class_name)
                                        break
                        except Exception as error:
                            description = _ParsedDescription(error_message=error.args[0])

                if description is None or description._description_code is None or script_type is None:
                    continue

                info = create_workflow_info(workflow_id, filepath, name, script_type, description)
                
                if script_type == ScriptTypeEnum.Notebook and not notebook_kernel_info:
                    info._category = "Invalid"
                    error_message = "Notebook kernel not defined. A notebook must have a kernel defined before it can be used as a workflow"
                    info._set_error_message(error_message)
                    logger.warning(f'{filepath}: {error_message}')

                duplicate_info = next((i for i in this.workflow_dict.values() if i._get_name() == info._get_name() and i._get_version() == info._get_version()), None)
                if duplicate_info is not None:
                    error_message = f"This workflow appears to be a duplicate of {duplicate_info._get_filepath()} which already exists in library"
                    info._set_error_message(error_message)
                    logger.warning(f'{filepath}: {error_message}')

                this.workflow_dict[workflow_id] = info
                logger.info(f'Add workflow: {info._get_name()}')


def run_workflow(info: WorkflowInfo, parameters, live_output: bool = True) -> Iterable[Tuple[bool, bool, Any, str]]:
    try:
        working_path = info.working_path
        logger.debug(f"working_path: {working_path}")

        if info.script_type == ScriptTypeEnum.Notebook:

            notebook = Notebook(info.filepath, working_path)

            if not notebook.is_valid:
                return [(False, True, None, notebook.error_message)]

            return notebook.run_capture_outputs(parameters, live_output=live_output)

        elif info.script_type == ScriptTypeEnum.PyScript:
            with open(info.filepath, 'r') as file:
                parameters["working_path"] = working_path
                path = os.path.normpath(os.path.dirname(info.filepath)).replace('\\', '/')
                os.chdir(path)
                code = f"import sys\nsys.path.append('{path}')\n"
                code += file.read()

                script = Script("temp", code)

                if not script.is_valid:
                    return [(False, True, None, script.error_message)]

                return script.run_capture_outputs(parameters, live_output=live_output)
        else:
            logger.warning(f'Unsupported script type: {info.script_type}')
            return [(False, True, None, f"Error running {info.name} due to unsupported script type: {info.script_type}")]

    except Exception as e:
        logger.warning(f'{e}')
        return [(False, True, None, f"Error running workflow {e}")]


def list_available_workflows() -> Iterable[Tuple[str, WorkflowDescription]]:
    for key in this.workflow_dict.keys():
        yield (key, this.workflow_dict[key])


def get_workflow_info(workflow_id: str) -> WorkflowInfo:
    if workflow_id not in this.workflow_dict.keys():
        return None
    return WorkflowInfo(this.workflow_dict[workflow_id])

def create_workflow_info(workflow_id: str, filepath: str, name: str, script_type: ScriptTypeEnum, 
                         description: _ParsedDescription) -> WorkflowDescription:
    info = WorkflowDescription(name, "Invalid", "", "", "")
    deprecateded_imports = []
    if description.is_valid():
        described_code = description.get_description_code()
        code = ""
        for line in description.get_pycoderunner_imports():
            if "from cegalprizm.pycoderunner" in line and "DomainObjectsEnum" in line:
                deprecateded_imports.append("DomainObjectsEnum")
            code += f"{line}\n"
        code += described_code.code()
        parameters_script = Script(workflow_id, code)
        parameters_script._run()
        if not parameters_script.is_valid:
            error_message = "WorkflowDescription does not compile"
            info._set_error_message(error_message)
            logger.warning(f'{filepath}: {error_message}')
        elif parameters_script.is_error:
            error_message = parameters_script.error_message
            info._set_error_message(error_message)
            logger.warning(f'{filepath}: {error_message}')
        elif described_code.variable_name() in parameters_script.variables.keys():
            info = parameters_script.variables[described_code.variable_name()]
            try:
                info.is_valid()
            except Exception as error:
                info._set_error_message(error.args[0])
                logger.warning(f'{filepath}: {error.args[0]}')
        else:
            error_message = "WorkflowDescription object incorrectly defined"
            info._set_error_message(error_message)
            logger.warning(f'{filepath}: {error_message}')
    else:
        info._set_error_message(description.error_message())
        logger.warning(description.error_message())

    info._set_filepath(filepath)
    info._set_script_type(script_type)
    info._set_unlicensed(description.unlicensed())
    info._set_deprecated_imports_used(deprecateded_imports)

    return info
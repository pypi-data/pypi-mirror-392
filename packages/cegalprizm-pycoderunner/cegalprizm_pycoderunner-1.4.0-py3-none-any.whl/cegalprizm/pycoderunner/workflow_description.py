# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

import os
from typing import Dict, Iterable, List, Tuple, Union
from enum import Enum

from .pycoderunner_pb2 import RenderNumberAsType, RenderEnumAsType
from .workflow_inputs import BaseWorkflowInput
from .workflow_inputs import WorkflowInputBoolean, WorkflowInputInteger, WorkflowInputDouble
from .workflow_inputs import WorkflowInputString, WorkflowInputFile, WorkflowInputFolder
from .workflow_inputs import WorkflowInputEnum, WorkflowInputObjectRef


class ScriptTypeEnum(Enum):
    PyScript = 1
    Notebook = 2

class VisualEnum(Enum):
    Enabled = 1
    Visible = 2

class ObjectRefStateEnum(Enum):
    Selected = 1
    NotSelected = 2

class ParameterRef():
    """A reference to a parameter in a workflow description.
    """
    def __init__(self, name: str, workflow_input: BaseWorkflowInput):
        self.name = name
        self.workflow_input = workflow_input

    def is_valid_state(self, state):
        if self.workflow_input.get_type() == "bool":
            if not isinstance(state, bool):
                return (False, "state must be a bool")
        elif self.workflow_input.get_type() == "enum":
            if not isinstance(state, int):
                return (False, "state must be an int")
            if state not in self.workflow_input._options.keys():
                return (False, "state must be a valid option")
        elif self.workflow_input.get_type() == "object_ref":
            if not isinstance(state, ObjectRefStateEnum):
                return (False, "state must be an ObjectRefStateEnum")
        return (True, "")
    
    def state_as_string(self, state):
        if self.workflow_input.get_type() == "bool":
            return str(state)
        elif self.workflow_input.get_type() == "enum":
            return str(state)
        elif self.workflow_input.get_type() == "object_ref":
            return str(state.name)

class ParameterState():
    """A class to define a desired parameter state.
    Used as the key in the linked_visual_parameters dictionary when add_*_parameter is called on the WorkflowDescription object. The ParameterState links the visual state of a parameter to the state of another parameter.

    **Example**: 

    Add an integer parameter that is only enabled in the UI when the linked boolean reference is True (Integer value can only be set when checkbox is checked):

    .. code-block:: python

        linked_bool_ref = pwr_description.add_boolean_parameter(name="linked_bool", label="linked_bool", description="linked_bool", default_value=False)
        linked_visual_parameters = {ParameterState(linked_bool_ref, True): VisualEnum.Enabled}
        pwr_description.add_integer_parameter(name="int", label="int", description="int", default_value=0, linked_visual_parameters=linked_visual_parameters)

    **Example**:

    Add an object reference parameter that is only visible in the UI when the linked enum reference is set to a specific value (Well selector only shows when the enum drop-down is set to Value3):

    .. code-block:: python

        linked_enum_ref = pwr_description.add_enum_parameter(name="enum1", label="enum1", description="enum1", options={1:"Value1", 2:"Value2", 3:"Value3"}, default_value=1)
        linked_visual_parameters = {ParameterState(linked_enum_ref, 3): VisualEnum.Visible}
        pwr_description.add_object_ref_parameter(name='well', label='well_selector', description='well_selector', object_type='well', select_multiple=False, linked_visual_parameters=linked_visual_parameters)

    **Example**:

    Add a float parameter that is only enabled in the UI when the linked object reference parameter has a selection (Float value can only be set when a well is selected):

    .. code-block:: python

        linked_object_ref = pwr_description.add_object_ref_parameter(name='well', label='well_selector', description='well_selector', object_type='well', select_multiple=False)
        linked_visual_parameters = {ParameterState(linked_object_ref, ObjectRefStateEnum.Selected): VisualEnum.Enabled}
        pwr_description.add_float_parameter(name="float", label="float", description="float", default_value=0.0, linked_visual_parameters=linked_visual_parameters)

    """
    def __init__(self, parameter_ref: ParameterRef, state):
        self.parameter_ref = parameter_ref
        self.state = state

    def is_valid(self):
        if self.parameter_ref is None:
            return (False, "parameter_ref must be defined")
        return self.parameter_ref.is_valid_state(self.state)
    
    def as_string(self):
        state_as_string = self.parameter_ref.state_as_string(self.state)
        return f"{self.parameter_ref.name}:{state_as_string}"

class WorkflowDescription():

    def __init__(self, name: str, category: str, description: str, authors: str, version: str):
        """
        Describes a PWR workflow

        Args:
            name (str): The name of the workflow.
            category (str): The category of the workflow (this is a free text string that can be used by the user to help filter and discover workflows)
            description (str): A free text field description of the workflow and what is does.
            authors (str): A free text field that can be used to list the names/email addresses of who should be contacted for support and/or additional information about this workflow.
            version (str): A free text field that can be used to describe the version of the workflow.
        """
        self._is_valid = True
        self._error_message = ""

        if not isinstance(name, str):
            self._is_valid = False
            raise ValueError("name must be a str")
        if not isinstance(category, str):
            self._is_valid = False
            raise ValueError("category must be a str")
        if not isinstance(description, str):
            self._is_valid = False
            raise ValueError("description must be a str")
        if not isinstance(authors, str):
            self._is_valid = False
            raise ValueError("authors must be a str")
        if not isinstance(version, str):
            self._is_valid = False
            raise ValueError("version must be a str")

        self._name = name
        self._category = category
        self._description = description
        self._authors = authors
        self._version = version
        self._filepath = ""
        self._unlicensed = False
        self._script_type = ScriptTypeEnum.PyScript
        self._parameters: List[BaseWorkflowInput] = []
        self._deprecated_imports_used = []
        self._configurations: Dict[str, object] = {}

    def _get_name(self) -> str:
        return self._name

    def _get_category(self) -> str:
        return self._category

    def _get_description(self) -> str:
        return self._description

    def _get_authors(self) -> str:
        return self._authors

    def _get_version(self) -> str:
        return self._version

    def _get_script_type(self) -> ScriptTypeEnum:
        return self._script_type

    def _set_script_type(self, script_type: ScriptTypeEnum):
        self._script_type = script_type

    def _get_filepath(self) -> str:
        return self._filepath

    def _set_filepath(self, filepath: str):
        self._filepath = filepath

    def _is_unlicensed(self) -> str:
        return self._unlicensed

    def _set_unlicensed(self, unlicensed: bool):
        self._unlicensed = unlicensed

    def _get_parameters(self) -> Iterable[BaseWorkflowInput]:
        return self._parameters

    def _get_configurations(self) -> Dict[str, object]:
        return self._configurations

    def _get_error_message(self) -> str:
        return self._error_message

    def _set_error_message(self, error_message: str):
        self._error_message = error_message
        self._is_valid = False

    def _set_deprecated_imports_used(self, deprecated_imports: List[str]):
        self._deprecated_imports_used = deprecated_imports
    
    def _get_deprecated_imports_used(self) -> List[str]:
        return self._deprecated_imports_used

    def add_boolean_parameter(self, name: str, label: str, description: str, default_value: bool,
                              linked_visual_parameters: Dict[ParameterState, VisualEnum] = None,
                              parameter_group: str = None):
        """
        Adds a boolean parameter to the workflow description.

        This will generate a checkbox in the workflow UI.

        **Example**:

        Add a boolean parameter:
        
        .. code-block:: python

            pwr_description.add_boolean_parameter(name='bool', label='bool_input', description='bool_input', default_value=False)

        **Example**:

        Add a boolean parameter that is only visible in the UI when the linked enum reference is set to a specific value (Checkbox only shows when the enum drop-down is set to Value3):

        .. code-block:: python

            linked_enum_ref = pwr_description.add_enum_parameter(name="enum1", label="enum1", description="enum1", options={1:"Value1", 2:"Value2", 3:"Value3"}, default_value=1)
            linked_visual_parameters = {ParameterState(linked_enum_ref, 3): VisualEnum.Visible}
            pwr_description.add_boolean_parameter(name='bool', label='bool_input', description='bool_input', default_value=False, linked_visual_parameters=linked_visual_parameters)

        Args:
            name (str): The name of the object created in the parameters dictionary. This name must be unique within the workflow.
            label (str): The label text that will be displayed next to the checkbox in the workflow UI.
            description (str): A description of what the parameter represents. This description will be shown in the tooltip next to the checkbox in the workflow UI.
            default_value (bool): The default value to be assigned to the parameter.
            linked_visual_parameters (Dict[ParameterState, VisualEnum], optional): Use this to specify a link between another boolean, enum or object_ref parameter state and this parameter's visual state.
                                                                                If the linked visual parameter have correct state the parameter will be enabled/visible accordingly.
                                                                                If adding multiple linked visual parameters, all must be true for the parameter to be enabled/visible.
                                                                                Defaults to None.
            parameter_group (str, optional): Use this to specify the parameter group this parameter belongs to. Defaults to None.

        Returns:
            ParameterRef: a reference to the parameter that was added
                                                                        
        Raises:
            ValueError: If the name is not a string, is not lowercase or contains spaces.
            ValueError: If the name is already used in the workflow.
            ValueError: If the label is not a string.
            ValueError: If the description is not a string.
            ValueError: If the linked_visual_parameters is not a dict where all keys are ParameterState and all values are VisualEnum.
            ValueError: If the default_value is not a bool.
        """

        valid = self._is_common_parameters_valid(name, label, description, linked_visual_parameters, parameter_group)
        if not valid[0]:
            self._is_valid = False
            self._error_message = valid[1]
            raise ValueError(self._error_message)

        if not isinstance(default_value, bool):
            self._is_valid = False
            self._error_message = f"Parameter {name}: default_value must be a bool"
            raise ValueError(self._error_message)
        
        workflow_input = WorkflowInputBoolean(name, label, description, default_value, linked_visual_parameters, parameter_group)
        self._parameters.append(workflow_input)
        return ParameterRef(name, workflow_input)

    def add_integer_parameter(self, name: str, label: str, description: str, default_value: int = 0,
                              minimum_value: int = None, maximum_value: int = None,
                              linked_visual_parameters: Dict[ParameterState, VisualEnum] = None,
                              parameter_group: str = None):
        """
        Adds an integer parameter to the workflow description.

        This will generate an integer number field in the workflow UI.

        **Example**:

        Add an integer parameter:

        .. code-block:: python

            pwr_description.add_integer_parameter(name='int', label='int_input', description='int_input', default_value=0)

        **Example**:

        Add an integer parameter that is only visible in the UI when the linked boolean reference is set to True:

        .. code-block:: python

            linked_bool_ref = pwr_description.add_boolean_parameter(name="linked_bool", label="linked_bool", description="linked_bool", default_value=False)
            linked_visual_parameters = {ParameterState(linked_bool_ref, True): VisualEnum.Visible}
            pwr_description.add_integer_parameter(name='int', label='int_input', description='int_input', default_value=0, linked_visual_parameters=linked_visual_parameters)

        Args:
            name (str): The name of the object created in the parameters dictionary. This name must be unique within the workflow.
            label (str): The label text that will be displayed next to the field in the workflow UI.
            description (str): A description of what the parameter represents. This description will be shown in the tooltip next to the field in the workflow UI.
            default_value (int, optional): If defined this specifies the default value to be assigned to the parameter. Defaults to 0.
            minimum_value (int, optional): If defined this specifies the lowest value the field can accept. Defaults to None.
            maximum_value (int, optional): If defined this specifies the highest value the field can accept. Defaults to None.
            linked_visual_parameters (Dict[ParameterState, VisualEnum], optional): Use this to specify a link between another boolean, enum or object_ref parameter state and this parameter's visual state.
                                                                                If the linked visual parameter have correct state the parameter will be enabled/visible accordingly.
                                                                                If adding multiple linked visual parameters, all must be true for the parameter to be enabled/visible.
                                                                                Defaults to None.
            parameter_group (str, optional): Use this to specify the parameter group this parameter belongs to. Defaults to None.

        Returns:
            ParameterRef: a reference to the parameter that was added

        Raises:
            ValueError: If the name is not a string, is not lowercase or contains spaces.
            ValueError: If the name is already used in the workflow.
            ValueError: If the label is not a string.
            ValueError: If the description is not a string.
            ValueError: If the linked_visual_parameters is not a dict where all keys are ParameterState and all values are VisualEnum.
            ValueError: If the default_value is not an int.
            ValueError: If the minimum_value or maximum value is not an int or None.
        """

        valid = self._is_common_parameters_valid(name, label, description, linked_visual_parameters, parameter_group)
        if not valid[0]:
            self._is_valid = False
            self._error_message = valid[1]
            raise ValueError(self._error_message)

        if not isinstance(default_value, int):
            self._is_valid = False
            self._error_message = f"Parameter {name}: default_value must be an int"
            raise ValueError(self._error_message)
        if minimum_value and not isinstance(minimum_value, int):
            self._is_valid = False
            self._error_message = f"Parameter {name}: default_value must be an int or None"
            raise ValueError(self._error_message)
        if maximum_value and not isinstance(maximum_value, int):
            self._is_valid = False
            self._error_message = f"Parameter {name}: maximum_value must be an int or None"
            raise ValueError(self._error_message)

        workflow_input = WorkflowInputInteger(name, label, description, 
                                              default_value, minimum_value, maximum_value, 
                                              linked_visual_parameters, 
                                              RenderNumberAsType.Text, 
                                              parameter_group)
        self._parameters.append(workflow_input)
        return ParameterRef(name, workflow_input)

    def add_integer_spinner_parameter(self, name: str, label: str, description: str, default_value: int,
                              minimum_value: int, maximum_value: int,
                              linked_visual_parameters: Dict[ParameterState, VisualEnum] = None, 
                              parameter_group: str = None):
        """
        Adds an integer spinner parameter to the workflow description.

        This will generate an integer spinner field in the workflow UI.

        **Example**:

        Add an integer spinner parameter:

        .. code-block:: python

            pwr_description.add_integer_spinner_parameter(name='int_spinner', label='int_spinner_input', description='int_spinner_input', default_value=0, minimum_value=0, maximum_value=10)

        **Example**:

        Add an integer spinner parameter that is only visible in the UI when the linked boolean reference is set to True:

        .. code-block:: python

            linked_bool_ref = pwr_description.add_boolean_parameter(name="linked_bool", label="linked_bool", description="linked_bool", default_value=False)
            linked_visual_parameters = {ParameterState(linked_bool_ref, True): VisualEnum.Visible}
            pwr_description.add_integer_spinner_parameter(name='i_s', label='i_s_input', description='i_s_input', default_value=0, minimum_value=0, maximum_value=10, linked_visual_parameters=linked_visual_parameters)

        Args:
            name (str): The name of the object created in the parameters dictionary. This name must be unique within the workflow.
            label (str): The label text that will be displayed next to the field in the workflow UI.
            description (str): A description of what the parameter represents. This description will be shown in the tooltip next to the field in the workflow UI.
            default_value (int): This specifies the default value to be assigned to the parameter.
            minimum_value (int): This specifies the lowest value the field can accept.
            maximum_value (int): This specifies the highest value the field can accept.
            linked_visual_parameters (Dict[ParameterState, VisualEnum], optional): Use this to specify a link between another boolean, enum or object_ref parameter state and this parameter's visual state.
                                                                                If the linked visual parameter have correct state the parameter will be enabled/visible accordingly.
                                                                                If adding multiple linked visual parameters, all must be true for the parameter to be enabled/visible.
                                                                                Defaults to None.
            parameter_group (str, optional): Use this to specify the parameter group this parameter belongs to. Defaults to None.

        Returns:
            ParameterRef: a reference to the parameter that was added

        Raises:
            ValueError: If the name is not a string, is not lowercase or contains spaces.
            ValueError: If the name is already used in the workflow.
            ValueError: If the label is not a string.
            ValueError: If the description is not a string.
            ValueError: If the linked_visual_parameters is not a dict where all keys are ParameterState and all values are VisualEnum.
            ValueError: If the default_value is not an int.
            ValueError: If the minimum_value or maximum value is not an int.
        """

        valid = self._is_common_parameters_valid(name, label, description, linked_visual_parameters, parameter_group)
        if not valid[0]:
            self._is_valid = False
            self._error_message = valid[1]
            raise ValueError(self._error_message)

        if not isinstance(default_value, int):
            self._is_valid = False
            self._error_message = f"Parameter {name}: default_value must be an int"
            raise ValueError(self._error_message)
        if minimum_value and not isinstance(minimum_value, int):
            self._is_valid = False
            self._error_message = f"Parameter {name}: minimum_value must be an int"
            raise ValueError(self._error_message)
        if maximum_value and not isinstance(maximum_value, int):
            self._is_valid = False
            self._error_message = f"Parameter {name}: maximum_value must be an int"
            raise ValueError(self._error_message)

        workflow_input = WorkflowInputInteger(name, label, description, 
                                              default_value, minimum_value, maximum_value, 
                                              linked_visual_parameters, 
                                              RenderNumberAsType.Spinner,
                                              parameter_group)
        self._parameters.append(workflow_input)
        return ParameterRef(name, workflow_input)
    
    def add_float_parameter(self, name: str, label: str, description: str, default_value: float = 0.0,
                            minimum_value: float = None, maximum_value: float = None,
                            measurement_type: Union[Enum, str] = None,
                            display_symbol: str = None,
                            linked_visual_parameters: Dict[ParameterState, VisualEnum] = None, 
                            parameter_group: str = None):
        """Adds a float parameter to the workflow description.

        This will generate an float number field in the workflow UI.

        **Example**:

        Add a float parameter:

        .. code-block:: python

            pwr_description.add_float_parameter(name='float', label='float_input', description='float_input', default_value=0.0)

        **Example**:

        Add a float parameter that is only visible in the UI when the linked boolean reference is set to True:

        .. code-block:: python

            linked_bool_ref = pwr_description.add_boolean_parameter(name="linked_bool", label="linked_bool", description="linked_bool", default_value=False)
            linked_visual_parameters = {ParameterState(linked_bool_ref, True): VisualEnum.Visible}
            pwr_description.add_float_parameter(name='float', label='float_input', description='float_input', default_value=0.0, linked_visual_parameters=linked_visual_parameters)

        Args:
            name (str): The name of the object created in the parameters dictionary. This name must be unique within the workflow.
            label (str): The label text that will be displayed next to the field in the workflow UI.
            description (str): A description of what the parameter represents. This text will be shown in the tooltip next to the field in the workflow UI.
            default_value (float, optional): If defined this specifies the default value to be assigned to the parameter. Defaults to 0.
            minimum_value (float, optional): If defined this specifies the lowest value the field can accept. Defaults to None.
            maximum_value (float, optional): If defined this specifies the highest value the field can accept. Defaults to None.
            measurement_type (Union[Enum(str), str], optional): If defined this specifies the measurement type of the parameter. Defaults to None.
            display_symbol (str, optional): If defined this specifies the units of the supplied parameter.
                                            This allows the workflow to ensure that the parameter will be in the given units irrespective of the display units in the Petrel project.
                                            Defaults to None.
            linked_visual_parameters (Dict[ParameterState, VisualEnum], optional): Use this to specify a link between another boolean, enum or object_ref parameter state and this parameter's visual state.
                                                                                If the linked visual parameter have correct state the parameter will be enabled/visible accordingly.
                                                                                If adding multiple linked visual parameters, all must be true for the parameter to be enabled/visible.
                                                                                Defaults to None.
            parameter_group (str, optional): Use this to specify the parameter group this parameter belongs to. Defaults to None.
                                                                    
        Returns:
            ParameterRef: a reference to the parameter that was added
                                                                        
        Raises:
            ValueError: If the name is not a string, is not lowercase or contains spaces.
            ValueError: If the name is already used in the workflow.
            ValueError: If the label is not a string.
            ValueError: If the description is not a string.
            ValueError: If the linked_visual_parameters is not a dict where all keys are ParameterState and all values are VisualEnum.
            ValueError: If the measurement_type is not Enum(str) or a str or None
            ValueError: If the display_symbol is not a str or None
            ValueError: If the display_symbol is defined while measurement_type is not defined, or the display_symbol is not defined while measeurement_type is defined
            ValueError: If the default_value is not a float or int
            ValueError: If the minimum_value or maximum_value is not a float or int or None
        """

        valid = self._is_common_parameters_valid(name, label, description, linked_visual_parameters, parameter_group)
        if not valid[0]:
            self._is_valid = False
            self._error_message = valid[1]
            raise ValueError(self._error_message)

        if not isinstance(default_value, float) and not isinstance(default_value, int):
            self._is_valid = False
            self._error_message = f"Parameter {name}: default_value must be a float"
            raise ValueError(self._error_message)
        if minimum_value and not isinstance(minimum_value, float) and not isinstance(minimum_value, int):
            self._is_valid = False
            self._error_message = f"Parameter {name}: minimum_value must be a float or None"
            raise ValueError(self._error_message)
        if maximum_value and not isinstance(maximum_value, float) and not isinstance(maximum_value, int):
            self._is_valid = False
            self._error_message = f"Parameter {name}: maximum_value must be a float or None"
            raise ValueError(self._error_message)

        measurement_name = None
        if measurement_type:
            if isinstance(measurement_type, Enum) and isinstance(measurement_type.value, str):
                measurement_name = measurement_type.value
            elif isinstance(measurement_type, str):
                measurement_name = measurement_type
            else:
                self._is_valid = False
                self._error_message = f"Parameter {name}: measurement_type invalid: must be Enum(str) or str or None"
                raise ValueError(self._error_message)

        if display_symbol:
            if not measurement_type:
                self._is_valid = False
                self._error_message = f"Parameter {name}: display_symbol should only be defined if measurement_type is defined"
                raise ValueError(self._error_message)
            if not isinstance(display_symbol, str):
                self._is_valid = False
                self._error_message = f"Parameter {name}: display_symbol must be a str"
                raise ValueError(self._error_message)

        if measurement_type:
            if not display_symbol:
                self._is_valid = False
                self._error_message = f"Parameter {name}: display_symbol must be defined if measurement_type is defined"
                raise ValueError(self._error_message)

        _default_value = None
        if default_value is not None:
            _default_value = float(default_value)

        _minimum_value = None
        if minimum_value is not None:
            _minimum_value = float(minimum_value)

        _maximum_value = None
        if maximum_value is not None:
            _maximum_value = float(maximum_value)

        workflow_input = WorkflowInputDouble(name, label, description, _default_value,
                                             _minimum_value, _maximum_value,
                                             measurement_name,
                                             display_symbol,
                                             linked_visual_parameters,
                                             False, 0.0, 
                                             -1,
                                             RenderNumberAsType.Text,
                                             parameter_group)
        self._parameters.append(workflow_input)
        return ParameterRef(name, workflow_input)

    def add_float_spinner_parameter(self, name: str, label: str, description: str, default_value: float,
                                    minimum_value: float, maximum_value: float, increment: float,
                                    measurement_type: Union[Enum, str] = None,
                                    display_symbol: str = None,
                                    linked_visual_parameters: Dict[ParameterState, VisualEnum] = None,
                                    show_increment: bool = False,
                                    decimal_places: int = -1, 
                                    parameter_group: str = None):
        """Adds a float spinner parameter to the workflow description.

        This will generate a float spinner in the workflow UI.

        **Example**:

        Add a float spinner parameter:

        .. code-block:: python

            pwr_description.add_float_spinner_parameter(name='float_spinner', label='float_spinner_input', description='float_spinner_input', default_value=0.0, minimum_value=-5.0, maximum_value=5.0, increment=0.2)

        **Example**:

        Add a float spinner parameter that is only visible in the UI when the linked boolean reference is set to True:

        .. code-block:: python

            linked_bool_ref = pwr_description.add_boolean_parameter(name="linked_bool", label="linked_bool", description="linked_bool", default_value=False)
            linked_visual_parameters = {ParameterState(linked_bool_ref, True): VisualEnum.Visible}
            pwr_description.add_float_spinner_parameter(name='f_s', label='f_s_input', description='f_s_input', default_value=2.5, minimum_value=0.0, maximum_value=5.0, increment=0.1, linked_visual_parameters=linked_visual_parameters)

        Args:
            name (str): The name of the object created in the parameters dictionary. This name must be unique within the workflow.
            label (str): The label text that will be displayed next to the field in the workflow UI.
            description (str): A description of what the parameter represents. This text will be shown in the tooltip next to the field in the workflow UI.
            default_value (float): The default value to be assigned to the parameter.
            minimum_value (float): The lowest value the field can accept.
            maximum_value (float): The highest value the field can accept.
            increment (float): The increment (step size) for the spinner control. Increment must be greater than zero.
            measurement_type (Union[Enum(str), str], optional): If defined this specifies the measurement type of the parameter. Defaults to None.
            display_symbol (str, optional): If defined this specifies the units of the supplied parameter.
                                            This allows the workflow to ensure that the parameter will be in the given units irrespective of the display units in the Petrel project.
                                            Defaults to None.
            linked_visual_parameters (Dict[ParameterState, VisualEnum], optional): Use this to specify a link between another boolean, enum or object_ref parameter state and this parameter's visual state.
                                                                                If the linked visual parameter have correct state the parameter will be enabled/visible accordingly.
                                                                                If adding multiple linked visual parameters, all must be true for the parameter to be enabled/visible.
                                                                                Defaults to None.
            show_increment (bool, optional): Use this to specify if the increment value should be shown in the UI. Defaults to False.
            decimal_places (int, optional): Use this to specify the number of decimal places to show in the UI.
            parameter_group (str, optional): Use this to specify the parameter group this parameter belongs to. Defaults to None.
                                                     
        Returns:
            ParameterRef: a reference to the parameter that was added
                                                                        
        Raises:
            ValueError: If the name is not a string, is not lowercase or contains spaces.
            ValueError: If the name is already used in the workflow.
            ValueError: If the label is not a string.
            ValueError: If the description is not a string.
            ValueError: If the linked_visual_parameters is not a dict where all keys are ParameterState and all values are VisualEnum.
            ValueError: If the measurement_type is not Enum(str) or a str or None
            ValueError: If the display_symbol is not a str or None
            ValueError: If the display_symbol is defined while measurement_type is not defined, or the display_symbol is not defined while measurement_type is defined
            ValueError: If the default_value is not a float or int
            ValueError: If the minimum_value or maximum_value is not a float or int
            ValueError: If the increment is not a float or int, or the increment is less than or equal to zero
            ValueError: If the decimal_places is not an int
        """

        valid = self._is_common_parameters_valid(name, label, description, linked_visual_parameters, parameter_group)
        if not valid[0]:
            self._is_valid = False
            self._error_message = valid[1]
            raise ValueError(self._error_message)

        if not isinstance(default_value, float) and not isinstance(default_value, int):
            self._is_valid = False
            self._error_message = f"Parameter {name}: default_value must be a float"
            raise ValueError(self._error_message)
        if minimum_value and not isinstance(minimum_value, float) and not isinstance(minimum_value, int):
            self._is_valid = False
            self._error_message = f"Parameter {name}: minimum_value must be a float"
            raise ValueError(self._error_message)
        if maximum_value and not isinstance(maximum_value, float) and not isinstance(maximum_value, int):
            self._is_valid = False
            self._error_message = f"Parameter {name}: maximum_value must be a float"
            raise ValueError(self._error_message)

        measurement_name = None
        if measurement_type:
            if isinstance(measurement_type, Enum) and isinstance(measurement_type.value, str):
                measurement_name = measurement_type.value
            elif isinstance(measurement_type, str):
                measurement_name = measurement_type
            else:
                self._is_valid = False
                self._error_message = f"Parameter {name}: measurement_type invalid: must be Enum(str) or str or None"
                raise ValueError(self._error_message)

        if display_symbol:
            if not measurement_type:
                self._is_valid = False
                self._error_message = f"Parameter {name}: display_symbol should only be defined if measurement_type is defined"
                raise ValueError(self._error_message)
            if not isinstance(display_symbol, str):
                self._is_valid = False
                self._error_message = f"Parameter {name}: display_symbol must be a str"
                raise ValueError(self._error_message)

        if measurement_type:
            if not display_symbol:
                self._is_valid = False
                self._error_message = f"Parameter {name}: display_symbol must be defined if measurement_type is defined"
                raise ValueError(self._error_message)
        
        if decimal_places and not isinstance(decimal_places, int):
            self._is_valid = False
            self._error_message = f"Parameter {name}: decimal_places must be an int"
            raise ValueError(self._error_message)

        _default_value = float(default_value)
        _minimum_value = float(minimum_value)
        _maximum_value = float(maximum_value)
        _increment = float(increment)
        if _increment <= 0.0:
            self._is_valid = False
            self._error_message = f"Parameter {name}: increment must be greater than zero"
            raise ValueError(self._error_message)

        _decimal_places = int(decimal_places) if decimal_places is not None else -1

        workflow_input = WorkflowInputDouble(name, label, description, _default_value,
                                             _minimum_value, _maximum_value,
                                             measurement_name,
                                             display_symbol,
                                             linked_visual_parameters,
                                             show_increment, _increment,
                                             _decimal_places,
                                             RenderNumberAsType.Spinner,
                                             parameter_group)
        self._parameters.append(workflow_input)
        return ParameterRef(name, workflow_input)

    def add_string_parameter(self, name: str, label: str, description: str, default_value: str = "", 
                             linked_visual_parameters: Dict[ParameterState, VisualEnum] = None, 
                             parameter_group: str = None):
        """
        Adds a string parameter to the workflow description.

        This will generate a text field in the workflow UI.

        **Example**:

        Add a string parameter to input a string:

        .. code-block:: python

            pwr_description.add_string_parameter(name='string', label='string_input', description='string_input', default_value='Please type someting here')

        **Example**:

        Add a string parameter that is only enabled in the UI when the linked boolean reference is set to True:

        .. code-block:: python

            linked_bool_ref = pwr_description.add_boolean_parameter(name="linked_bool", label="linked_bool", description="linked_bool", default_value=False)
            linked_visual_parameters = {ParameterState(linked_bool_ref, True): VisualEnum.Enabled}
            pwr_description.add_string_parameter(name='string', label='string_input', description='string_input', default_value='You can only type here after checking the checkbox', linked_visual_parameters=linked_visual_parameters)

        Args:
            name (str): The name of the object created in the parameters dictionary. This name must be unique within the workflow.
            label (str): The label text that will be displayed next to the text field in the workflow UI.
            description (str): A description of what the parameter is used for. This description will be shown in the tooltip next to the text field in the workflow UI.
            default_value (str, optional): The default value to be assigned to the parameter.
            linked_visual_parameters (Dict[ParameterState, VisualEnum], optional): Use this to specify a link between another boolean, enum or object_ref parameter state and this parameter's visual state.
                                                                                If the linked visual parameter have correct state the parameter will be enabled/visible accordingly.
                                                                                If adding multiple linked visual parameters, all must be true for the parameter to be enabled/visible.
                                                                                Defaults to None.
            parameter_group (str, optional): Use this to specify the parameter group this parameter belongs to. Defaults to None.

        Returns:
            ParameterRef: a reference to the parameter that was added

        Raises:
            ValueError: If the name is not a string, is not lowercase or contains spaces.
            ValueError: If the name is already used in the workflow.
            ValueError: If the label is not a string.
            ValueError: If the description is not a string.
            ValueError: If the linked_visual_parameters is not a dict where all keys are ParameterState and all values are VisualEnum.
            ValueError: If the default_value is not a str.
        """

        valid = self._is_common_parameters_valid(name, label, description, linked_visual_parameters, parameter_group)
        if not valid[0]:
            self._is_valid = False
            self._error_message = valid[1]
            raise ValueError(self._error_message)

        if not isinstance(default_value, str):
            self._is_valid = False
            self._error_message = f"Parameter {name}: default_value must be a str"
            raise ValueError(self._error_message)

        workflow_input = WorkflowInputString(name, label, description, default_value, linked_visual_parameters, parameter_group)
        self._parameters.append(workflow_input)
        return ParameterRef(name, workflow_input)

    def add_enum_parameter(self, name: str, label: str, description: str, 
                           options: Dict[int, str], default_value: int = None, 
                           linked_visual_parameters: Dict[ParameterState, VisualEnum] = None, 
                           parameter_group: str = None):
        """
        Adds an enum parameter to the workflow description.

        This will generate a combobox in the workflow UI.

        **Example**:

        Add an enum parameter to select between three options:

        .. code-block:: python

            pwr_description.add_enum_parameter(name='enum', label='enum_selector', description='enum_selector', options={1:"Option1", 2:"Option2", 3:"Option3"})

        **Example**:

        Add an enum parameter to select between three options that is only enabled in the UI when the linked boolean reference is set to True:

        .. code-block:: python

            linked_bool_ref = pwr_description.add_boolean_parameter(name="linked_bool", label="linked_bool", description="linked_bool", default_value=False)
            linked_visual_parameters = {ParameterState(linked_bool_ref, True): VisualEnum.Enabled}
            pwr_description.add_enum_parameter(name='enum', label='enum_selector', description='enum_selector', options={1:"Option1", 2:"Option2", 3:"Option3"}, linked_visual_parameters=linked_visual_parameters)

        Args:
            name (str): The name of the object created in the parameters dictionary. This name must be unique within the workflow.
            label (str): The label text that will be displayed next to the text field in the workflow UI.
            description (str): A description of what the parameter is used for. This description will be shown in the tooltip next to the combobox in the workflow UI.
            options (Dict[int, str]): A dictionary of options where each option is described by a value and the text to be shown for it.
            default_value (int, optional): The default value to be assigned to the parameter.
            linked_visual_parameters (Dict[ParameterState, VisualEnum], optional): Use this to specify a link between another boolean, enum or object_ref parameter state and this parameter's visual state.
                                                                                If the linked visual parameter have correct state the parameter will be enabled/visible accordingly.
                                                                                If adding multiple linked visual parameters, all must be true for the parameter to be enabled/visible.
                                                                                Defaults to None.
            parameter_group (str, optional): Use this to specify the parameter group this parameter belongs to. Defaults to None.

        Returns:
            ParameterRef: a reference to the parameter that was added
                                                                        
        Raises:
            ValueError: If the name is not a string, is not lowercase or contains spaces.
            ValueError: If the name is already used in the workflow.
            ValueError: If the label is not a string.
            ValueError: If the description is not a string.
            ValueError: If the linked_visual_parameters is not a dict where all keys are ParameterState and all values are VisualEnum.
            ValueError: If the options is not a dict, or if the options dictionary is empty.
            ValueError: If the options dictionary contains a key that is not an int or a value that is not a str.
            ValueError: If the options dictionary contains a value that is already defined as an option.
            ValueError: If the default_value is not an int, or if the default_value is not a defined option.
        """

        valid = self._is_common_parameters_valid(name, label, description, linked_visual_parameters, parameter_group)
        if not valid[0]:
            self._is_valid = False
            self._error_message = valid[1]
            raise ValueError(self._error_message)

        if not isinstance(options, dict):
            self._is_valid = False
            self._error_message = f"Parameter {name}: options must be a dict"
            raise ValueError(self._error_message)
        if len(options) == 0:
            self._is_valid = False
            self._error_message = f"Parameter {name}: options must not be empty"
            raise ValueError(self._error_message)

        valid_keys = []
        valid_options = {}
        for key in options.keys():
            if not isinstance(key, int):
                self._is_valid = False
                self._error_message = f"Parameter {name}: option {str(key)} key must be int"
                raise ValueError(self._error_message)
            if not isinstance(options[key], str):
                self._is_valid = False
                self._error_message = f"Parameter {name}: option {str(key)} value must be str"
                raise ValueError(self._error_message)
            if options[key] in valid_options.values():
                self._is_valid = False
                self._error_message = f"Parameter {name}: option {str(key)} value is already defined as an option"
                raise ValueError(self._error_message)
            valid_keys.append(key)
            valid_options[key] = options[key]

        if default_value is None:
            default_value = valid_keys[0]
        if not isinstance(default_value, int):
            self._is_valid = False
            self._error_message = f"Parameter {name}: default_value must be an int"
            raise ValueError(self._error_message)
        if default_value not in valid_options.keys():
            self._is_valid = False
            self._error_message = f"Parameter {name}: default_value must be a defined option"
            raise ValueError(self._error_message)

        workflow_input = WorkflowInputEnum(name, label, description, 
                                           valid_options, default_value, 
                                           linked_visual_parameters, 
                                           RenderEnumAsType.Combo, 
                                           parameter_group)
        self._parameters.append(workflow_input)
        return ParameterRef(name, workflow_input)

    def add_radio_parameter(self, name: str, label: str, description: str, 
                            options: Dict[int, str], default_value: int = None, 
                            linked_visual_parameters: Dict[ParameterState, VisualEnum] = None, 
                            parameter_group: str = None):
        """
        Adds a radio parameter to the workflow description.

        This will generate set of radio buttons in the workflow UI.

        **Example**:

        Add a radio parameter to select between three options:

        .. code-block:: python

            pwr_description.add_radio_parameter(name='radio', label='radio_selector', description='radio_selector', options={1:"Option1", 2:"Option2", 3:"Option3"})

        **Example**:

        Add a radio parameter to select between three options that is only enabled in the UI when the linked boolean reference is set to True:

        .. code-block:: python

            linked_bool_ref = pwr_description.add_boolean_parameter(name="linked_bool", label="linked_bool", description="linked_bool", default_value=False)
            linked_visual_parameters = {ParameterState(linked_bool_ref, True): VisualEnum.Enabled}
            pwr_description.add_radio_parameter(name='radio', label='radio_selector', description='radio_selector', options={1:"Option1", 2:"Option2", 3:"Option3"}, linked_visual_parameters=linked_visual_parameters)

        Args:
            name (str): The name of the object created in the parameters dictionary. This name must be unique within the workflow.
            label (str): The label text that will be displayed next to the text field in the workflow UI.
            description (str): A description of what the parameter is used for. This description will be shown in the tooltip next to the radio buttons in the workflow UI.
            options (Dict[int, str]): A dictionary of options where each option is described by a value and the text to be shown for it.
            default_value (int, optional): The default value to be assigned to the parameter.
            linked_visual_parameters (Dict[ParameterState, VisualEnum], optional): Use this to specify a link between another boolean, enum or object_ref parameter state and this parameter's visual state.
                                                                                If the linked visual parameter have correct state the parameter will be enabled/visible accordingly.
                                                                                If adding multiple linked visual parameters, all must be true for the parameter to be enabled/visible.
                                                                                Defaults to None.
            parameter_group (str, optional): Use this to specify the parameter group this parameter belongs to. Defaults to None.

        Returns:
            ParameterRef: a reference to the parameter that was added
                                                                        
        Raises:
            ValueError: If the name is not a string, is not lowercase or contains spaces.
            ValueError: If the name is already used in the workflow.
            ValueError: If the label is not a string.
            ValueError: If the description is not a string.
            ValueError: If the linked_visual_parameters is not a dict where all keys are ParameterState and all values are VisualEnum.
            ValueError: If the options is not a dict, or if the options dictionary is empty.
            ValueError: If the options dictionary contains a key that is not an int or a value that is not a str.
            ValueError: If the options dictionary contains a value that is already defined as an option.
            ValueError: If the default_value is not an int, or if the default_value is not a defined option.
        """

        valid = self._is_common_parameters_valid(name, label, description, linked_visual_parameters, parameter_group)
        if not valid[0]:
            self._is_valid = False
            self._error_message = valid[1]
            raise ValueError(self._error_message)

        if not isinstance(options, dict):
            self._is_valid = False
            self._error_message = f"Parameter {name}: options must be a dict"
            raise ValueError(self._error_message)
        if len(options) == 0:
            self._is_valid = False
            self._error_message = f"Parameter {name}: options must not be empty"
            raise ValueError(self._error_message)

        valid_keys = []
        valid_options = {}
        for key in options.keys():
            if not isinstance(key, int):
                self._is_valid = False
                self._error_message = f"Parameter {name}: option {str(key)} key must be int"
                raise ValueError(self._error_message)
            if not isinstance(options[key], str):
                self._is_valid = False
                self._error_message = f"Parameter {name}: option {str(key)} value must be str"
                raise ValueError(self._error_message)
            if options[key] in valid_options.values():
                self._is_valid = False
                self._error_message = f"Parameter {name}: option {str(key)} value is already defined as an option"
                raise ValueError(self._error_message)
            valid_keys.append(key)
            valid_options[key] = options[key]

        if default_value is None:
            default_value = valid_keys[0]
        if not isinstance(default_value, int):
            self._is_valid = False
            self._error_message = f"Parameter {name}: default_value must be an int"
            raise ValueError(self._error_message)
        if default_value not in valid_options.keys():
            self._is_valid = False
            self._error_message = f"Parameter {name}: default_value must be a defined option"
            raise ValueError(self._error_message)

        workflow_input = WorkflowInputEnum(name, label, description, 
                                           valid_options, default_value,
                                           linked_visual_parameters, 
                                           RenderEnumAsType.Radio, 
                                           parameter_group)
        self._parameters.append(workflow_input)
        return ParameterRef(name, workflow_input)

    def add_file_parameter(self, name: str, label: str, description: str, 
                           file_extensions: str, select_multiple: bool = False, 
                           linked_visual_parameters: Dict[ParameterState, VisualEnum] = None,
                           parameter_group: str = None):
        """
        Adds a file parameter to the workflow description.

        This will generate a file selection in the workflow UI.

        **Example**:

        Add a file parameter to select a file:

        .. code-block:: python

            pwr_description.add_file_parameter(name='file', label='file_selector', description='file_selector', file_extensions='*.txt')

        **Example**:

        Add a file parameter to select multiple files that is only enabled in the UI when the linked boolean reference is set to True:

        .. code-block:: python

            linked_bool_ref = pwr_description.add_boolean_parameter(name="linked_bool", label="linked_bool", description="linked_bool", default_value=False)
            linked_visual_parameters = {ParameterState(linked_bool_ref, True): VisualEnum.Enabled}
            pwr_description.add_file_parameter(name='file', label='file_selector', description='file_selector', file_extensions='*.txt', select_multiple=True, linked_visual_parameters=linked_visual_parameters)

        Args:
            name (str): The name of the object created in the parameters dictionary. This name must be unique within the workflow.
            label (str): The label text that will be displayed next to the text field in the workflow UI.
            description (str): A description of what the parameter is used for. This description will be shown in the tooltip next to the text field in the workflow UI.
            file_extensions (str): The file extensions supported.
            select_multiple (bool, optional): Specifies if the parameter can contain multiple values. Defaults to False.
            linked_visual_parameters (Dict[ParameterState, VisualEnum], optional): Use this to specify a link between another boolean, enum or object_ref parameter state and this parameter's visual state.
                                                                                If the linked visual parameter have correct state the parameter will be enabled/visible accordingly.
                                                                                If adding multiple linked visual parameters, all must be true for the parameter to be enabled/visible.
                                                                                Defaults to None.
            parameter_group (str, optional): Use this to specify the parameter group this parameter belongs to. Defaults to None.

        Returns:
            ParameterRef: a reference to the parameter that was added
                                                                                                                                                
        Raises:
            ValueError: If the name is not a string, is not lowercase or contains spaces.
            ValueError: If the name is already used in the workflow.
            ValueError: If the label is not a string.
            ValueError: If the description is not a string.
            ValueError: If the linked_visual_parameters is not a dict where all keys are ParameterState and all values are VisualEnum.
            ValueError: If the file_extensions is not a str.
            ValueError: If the select_multiple is not a bool.
        """

        valid = self._is_common_parameters_valid(name, label, description, linked_visual_parameters, parameter_group)
        if not valid[0]:
            self._is_valid = False
            self._error_message = valid[1]
            raise ValueError(self._error_message)

        if not isinstance(file_extensions, str):
            self._is_valid = False
            self._error_message = f"Parameter {name}: file_extensions must be a str"
            raise ValueError(self._error_message)

        if not isinstance(select_multiple, bool):
            self._is_valid = False
            self._error_message = f"Parameter {name}: select_multiple must be a bool"
            raise ValueError(self._error_message)

        workflow_input = WorkflowInputFile(name, label, description, 
                                           file_extensions, 
                                           linked_visual_parameters, 
                                           select_multiple, 
                                           parameter_group)
        self._parameters.append(workflow_input)
        return ParameterRef(name, workflow_input)

    def add_folder_parameter(self, name: str, label: str, description: str, 
                             linked_visual_parameters: Dict[ParameterState, VisualEnum] = None,
                             default_folder: Union[Enum, str] = None,
                             parameter_group: str = None):
        """
        Adds a folder parameter to the workflow description.

        This will generate a folder selection in the workflow UI.

        **Example**:

        Add a folder parameter to select a folder:

        .. code-block:: python

            pwr_description.add_folder_parameter(name='folder', label='folder_selector', description='folder_selector')

        **Example**:

        Add a folder parameter to select a folder that is only enabled in the UI when the linked enum reference is set to "Value3":

        .. code-block:: python

            linked_enum_ref = pwr_description.add_enum_parameter(name="enum1", label="enum1", description="enum1", options={1:"Value1", 2:"Value2", 3:"Value3"}, default_value=1)
            linked_visual_parameters = {ParameterState(linked_enum_ref, 3): VisualEnum.Enabled}
            pwr_description.add_folder_parameter(name='folder', label='folder_selector', description='folder_selector', linked_visual_parameters=linked_visual_parameters, default_folder=WellKnownFolderLocationsEnum.Documents)

        Args:
            name (str): The name of the object created in the parameters dictionary. This name must be unique within the workflow.
            label (str): The label text that will be displayed next to the text field in the workflow UI.
            description (str): A description of what the parameter is used for. This description will be shown in the tooltip next to the text field in the workflow UI.
            linked_visual_parameters (Dict[ParameterState, VisualEnum], optional): Use this to specify a link between another boolean, enum or object_ref parameter state and this parameter's visual state.
                                                                                If the linked visual parameter have correct state the parameter will be enabled/visible accordingly.
                                                                                If adding multiple linked visual parameters, all must be true for the parameter to be enabled/visible.
                                                                                Defaults to None.
            default_folder (Union[Enum, str], optional): If defined this specifies the initially selected folder. Defaults to None.
            parameter_group (str, optional): Use this to specify the parameter group this parameter belongs to. Defaults to None.

        Returns:
            ParameterRef: a reference to the parameter that was added

        Raises:
            ValueError: If the name is not a string, is not lowercase or contains spaces.
            ValueError: If the name is already used in the workflow.
            ValueError: If the label is not a string.
            ValueError: If the description is not a string.
            ValueError: If the linked_visual_parameters is not a dict where all keys are ParameterState and all values are VisualEnum.
            ValueError: If the default_folder is not Enum(str) or a str
        """

        valid = self._is_common_parameters_valid(name, label, description, linked_visual_parameters, parameter_group)
        if not valid[0]:
            self._is_valid = False
            self._error_message = valid[1]
            raise ValueError(self._error_message)

        default_value = None
        if default_folder:
            if isinstance(default_folder, Enum) and isinstance(default_folder.value, str):
                default_value = default_folder.value
            elif isinstance(default_folder, str):
                default_value = default_folder
            else:
                self._is_valid = False
                self._error_message = f"Parameter {name}: default_folder invalid: must be Enum(str) or str"
                raise ValueError(self._error_message)
        
        workflow_input = WorkflowInputFolder(name, label, description, default_value, linked_visual_parameters, parameter_group)
        self._parameters.append(workflow_input)
        return ParameterRef(name, workflow_input)

    def add_object_ref_parameter(self, name: str, label: str, description: str,
                                 object_type: Union[Enum, str],
                                 template_type: Union[Iterable[Union[Enum, str]], Enum, str] = None,
                                 measurement_type: Union[Enum, str] = None,
                                 select_multiple: bool = False,
                                 linked_input_name: Union[ParameterRef, str] = None,
                                 linked_visual_parameters: Dict[ParameterState, VisualEnum] = None, 
                                 parameter_group: str = None):
        """
        Adds an object_ref parameter to the workflow description.

        This will generate a domain object selector (blue arrow control) in the workflow UI.

        Note: If select_multiple is False then the parameter value will be set to the DROID of the selected domain object.
              If select_multiple is True then the parameter value will be a list of DROIDs for the selected domain objects.

        **Example**:

        Add a single object reference parameter to select a well object:

        .. code-block:: python

            pwr_description.add_object_ref_parameter(name='well', label='well_selector', description='well_selector', object_type='well')

        **Example**:

        Add two object reference parameters to select a well object and then select multiple well continuous log objects for the selected well. Both drop-downs are only set to be visible when the linked boolean parameter is set to True:

        .. code-block:: python

            linked_bool_ref = pwr_description.add_boolean_parameter(name="linked_bool", label="linked_bool", description="linked_bool", default_value=False)
            linked_visual_parameters = {ParameterState(linked_bool_ref, True): VisualEnum.Visible}
            well_ref = pwr_description.add_object_ref_parameter(name='well', label='well_selector', description='well_selector', object_type=DomainObjectsEnum.Well, select_multiple=False, linked_visual_parameters=linked_visual_parameters)
            well_log_ref = pwr_description.add_object_ref_parameter(name='well_log', label='well_log_selector', description='well_log_selector', object_type=DomainObjectsEnum.WellContinuousLog, select_multiple=True, linked_input_name=well_ref, linked_visual_parameters=linked_visual_parameters)

        Args:
            name (str): The name of the object created in the parameters dictionary. This name must be unique within the workflow.
            label (str): The label text that will be displayed next to the dropbox in the workflow UI.
            description (str): A description of what the parameter is used for. This description will be shown in the tooltip next to the text field in the workflow UI.
            object_type (Union[Enum(str), str]): The domain object type that must be supplied for this parameter.
                                                         The workflow UI will limit the user to selecting only domain objects for this type.
            template_type (Union[Iterable[Union[Enum(str), str]], Enum(str), str], optional): If defined this specifies the template types accepted for the parameter. Defaults to None.
            measurement_type (Union[Enum(str), str], optional): If defined this specifies the measurement type accepted for the parameter. Defaults to None.
            select_multiple (bool, optional): Specifies if the parameter can contain multiple values. Defaults to False.
            linked_input_name (Union[ParameterRef, str], optional): If defined this links to another parameter defined in the workflow which must be specified to enable this parameter in the workflow UI. Can be specified either using the ParameterRef of another parameter or the name of the parameter as a string. Defaults to None.
            linked_visual_parameters (Dict[ParameterState, VisualEnum], optional): Use this to specify a link between another boolean, enum or object_ref parameter state and this parameter's visual state.
                                                                                If the linked visual parameter have correct state the parameter will be enabled/visible accordingly.
                                                                                If adding multiple linked visual parameters, all must be true for the parameter to be enabled/visible.
                                                                                Defaults to None.
            parameter_group (str, optional): Use this to specify the parameter group this parameter belongs to. Defaults to None.

        Returns:
            ParameterRef: a reference to the parameter that was added

        Raises:
            ValueError: If the name is not a string, is not lowercase or contains spaces.
            ValueError: If the name is already used in the workflow.
            ValueError: If the label is not a string.
            ValueError: If the description is not a string.
            ValueError: If the linked_visual_parameters is not a dict where all keys are ParameterState and all values are VisualEnum.
            ValueError: If the object_type is not Enum(str) or a str
            ValueError: If the template_type is not Iterable[Enum(str)] or a Iterable[str] or Enum(str) or a str
            ValueError: If the measurement_type is not Enum(str) or a str
            ValueError: If the select_multiple is not a bool
            ValueError: If the linked_input_name is not a str or ParameterRef
        """

        valid = self._is_common_parameters_valid(name, label, description, linked_visual_parameters, parameter_group)
        if not valid[0]:
            self._is_valid = False
            self._error_message = valid[1]
            raise ValueError(self._error_message)

        object_name = None
        if isinstance(object_type, Enum) and isinstance(object_type.value, str):
            object_name = object_type.value
        elif isinstance(object_type, str):
            object_name = object_type
        else:
            self._is_valid = False
            self._error_message = f"Parameter {name}: object_type invalid: must be Enum(str) or str"
            raise ValueError(self._error_message)

        template_names = None
        if template_type:
            template_type_valid = False
            if isinstance(template_type, Enum) and isinstance(template_type.value, str):
                template_type_valid = True
                template_names = []
                template_names.append(template_type.value)
            elif isinstance(template_type, str):
                template_type_valid = True
                template_names = []
                template_names.append(template_type)
            else:
                try:
                    template_type_valid = True
                    template_names = []
                    for val in iter(template_type):
                        if isinstance(val, Enum) and isinstance(val.value, str):
                            template_names.append(val.value)
                        elif isinstance(val, str):
                            template_names.append(val)
                        else:
                            template_type_valid = False
                            break
                except TypeError:
                    # not iterable
                    template_type_valid = False

            if not template_type_valid:
                self._is_valid = False
                self._error_message = f"Parameter {name}: template_type invalid: must be an iterable or Enum(str) or str"
                raise ValueError(self._error_message)

        measurement_name = None
        if measurement_type:
            if isinstance(measurement_type, Enum) and isinstance(measurement_type.value, str):
                measurement_name = measurement_type.value
            elif isinstance(measurement_type, str):
                measurement_name = measurement_type
            else:
                self._is_valid = False
                self._error_message = f"Parameter {name}: measurement_type invalid: must be Enum(str) or str"
                raise ValueError(self._error_message)

        if not isinstance(select_multiple, bool):
            self._is_valid = False
            self._error_message = f"Parameter {name}: select_multiple must be a bool"
            raise ValueError(self._error_message)

        if linked_input_name:
            if isinstance(linked_input_name, ParameterRef):
                linked_input_name = linked_input_name.name
            elif isinstance(linked_input_name, str):
                linked_input_name = linked_input_name
            else:
                self._is_valid = False
                self._error_message = f"Parameter {name}: linked_input_name must be a str or ParameterRef"
                raise ValueError(self._error_message)

        workflow_input = WorkflowInputObjectRef(name, label, description, 
                                                object_name, template_names, measurement_name, select_multiple, 
                                                linked_input_name, 
                                                linked_visual_parameters, 
                                                parameter_group)
        self._parameters.append(workflow_input)
        return ParameterRef(name, workflow_input)

    def is_valid(self) -> bool:
        """Returns a bool indicating if the workflow is valid

        Returns:
            bool: Indicates the if the workflow is valid
        """
        if not self._is_valid:
            return False

        linked_names_valid = self._linked_names_valid()
        if not linked_names_valid[0]:
            raise ValueError(linked_names_valid[1])
        
        linked_visual_parameters_valid = self._linked_visual_parameters_valid()
        if not linked_visual_parameters_valid[0]:
            raise ValueError(linked_visual_parameters_valid[1])

        return True

    def get_default_parameters(self) -> Dict[str, object]:
        """
        Returns a dictionary of the default values for parameters required by the workflow.

        This is useful when testing the workflow outside of PWR.

        Returns:
            Dict[str, object]: _description_
        """
        try:
            if not self.is_valid():
                return None
        except Exception:
            return None

        default_parameters = {}
        for item in self._parameters:
            default_parameters[item.get_name()] = item.get_default_value()
        return default_parameters

    def get_label(self, name: str) -> str:
        if not isinstance(name, str):
            raise ValueError(f"Parameter {name}: name must be a str")
        item = next((x for x in self._parameters if x.get_name() == name), None)
        if item is None:
            raise ValueError(f"Parameter {name}: No parameter defined with '{name}'")
        return item.get_label()
    

    def _is_common_parameters_valid(self, name: str, label: str, description: str, linked_visual_parameters, parameter_group: str) -> Tuple[bool, str]:
        if not isinstance(name, str):
            return (False, f"Parameter {name}: name must be a str")
        item = next((x for x in self._parameters if x.get_name() == name), None)
        if item is not None:
            return (False, f"Parameter {name}: Parameter already defined with '{name}'")
        elif name.lower() != name:
            return (False, f"Parameter {name}: name must be lowercase")
        elif ' ' in name:
            return (False, f"Parameter {name}: name must not contain spaces")

        if not isinstance(label, str):
            self._is_valid = False
            self._error_message = f"Parameter {name}: label must be a str"
            raise ValueError(self._error_message)

        if not isinstance(description, str):
            self._is_valid = False
            self._error_message = f"Parameter {name}: description must be a str"
            raise ValueError(self._error_message)

        if linked_visual_parameters:
            if not isinstance(linked_visual_parameters, dict):
                self._is_valid = False
                self._error_message = f"Parameter {name}: linked_visual_parameters must be a dict"
                raise ValueError(self._error_message)
            for key,value in linked_visual_parameters.items():
                if not isinstance(key, ParameterState):
                    self._is_valid = False
                    self._error_message = f"Parameter {name}: linked_visual_parameters dict key must be a ParameterState object"
                    raise ValueError(self._error_message)
                if not isinstance(value, VisualEnum):
                    self._is_valid = False
                    self._error_message = f"Parameter {name}: linked_visual_parameters dict value must be a valid VisualEnum"
                    raise ValueError(self._error_message)
                
        if parameter_group and not isinstance(parameter_group, str):
            self._is_valid = False
            self._error_message = f"Parameter {name}: parameter_group must be a str or None"
            raise ValueError(self._error_message)
        
        return (True, "")

    def _linked_names_valid(self) -> Tuple[bool, str]:
        for parameter in self._parameters:
            if isinstance(parameter, WorkflowInputObjectRef):
                linked_input_name = parameter.get_linked_input_name()
                if linked_input_name:
                    if linked_input_name == parameter.get_name():
                        return (False, f"Parameter '{parameter.get_name()}': cannot be is linked to itself")

                    linked_parameter = next((x for x in self._parameters if x.get_name() == linked_input_name), None)
                    if linked_parameter is None:
                        return (False, f"Parameter '{parameter.get_name()}': linked parameter '{linked_input_name}' is not defined in the workflow")
        return (True, "")
    
    def _linked_visual_parameters_valid(self) -> Tuple[bool, str]:
        for parameter in self._parameters:
            linked_visual_parameters_dict = parameter.get_linked_visual_parameters()
            if not linked_visual_parameters_dict:
                continue
            for param_state in linked_visual_parameters_dict.keys():
                linked_param_name = param_state.parameter_ref.name
                if linked_param_name not in [x.get_name() for x in self._parameters]:
                    return (False, f"Parameter '{parameter.get_name()}': linked visual parameter '{linked_param_name}' is not defined in the workflow")
                is_valid = param_state.is_valid()
                if not is_valid[0]:
                    return (False, f"Parameter '{parameter.get_name()}': linked visual parameter key '{param_state}' is not valid in the workflow {self._get_filepath()}. {is_valid[1]}")
        return (True, "")

class WorkflowInfo():
    def __init__(self, description: WorkflowDescription):
        self.is_valid = description.is_valid()
        self.script_type = description._get_script_type()
        self.filepath = description._get_filepath()
        self.name = description._get_name()
        self.working_path = os.environ['CEGAL_PWR_TASK_WORKING_PATH']

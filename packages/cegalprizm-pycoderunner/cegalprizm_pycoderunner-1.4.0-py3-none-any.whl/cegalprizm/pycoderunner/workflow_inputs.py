# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from typing import Dict, List

from .pycoderunner_pb2 import RenderNumberAsType, RenderEnumAsType
from .pycoderunner_pb2 import WellKnownWorkflowInput, EnumOption
from .pycoderunner_pb2 import BooleanWorkflowInput, IntegerWorkflowInput, DoubleWorkflowInput, StringWorkflowInput
from .pycoderunner_pb2 import EnumWorkflowInput, FileWorkflowInput, FolderWorkflowInput, ObjectRefWorkflowInput


class BaseWorkflowInput():

    def __init__(self, type: str, name: str, label: str, description: str, default_value, linked_visual_parameters, parameter_group: str = None):
        self._type = type
        self._name = name
        self._label = label
        self._description = description
        self._default_value = default_value
        self._parameter_group = parameter_group
        self._linked_visual_parameters = linked_visual_parameters

    def get_type(self):
        return self._type

    def get_name(self):
        return self._name

    def get_label(self):
        return self._label

    def get_description(self):
        return self._description

    def get_default_value(self):
        return self._default_value
    
    def get_parameter_group(self):
        return self._parameter_group or ""
    
    def get_linked_visual_parameters(self):
        return self._linked_visual_parameters
    
    def get_parsed_linked_visual_parameters(self) -> Dict[str, str]:
        linked_visual_parameters = {}
        if self._linked_visual_parameters:
            for key,value in self._linked_visual_parameters.items():
                new_key = key.as_string()
                linked_visual_parameters[new_key] = str(value.name).lower()
        return linked_visual_parameters
    
    def get_wellknown_workflow_input(self):
        input = WellKnownWorkflowInput()
        input.name = self.get_name()
        input.type = self.get_type()
        input.label = self.get_label()
        input.description = self.get_description()
        input.parameter_group = self.get_parameter_group()
        linked_vis_params = self.get_parsed_linked_visual_parameters()
        if linked_vis_params is not None:
            for key in linked_vis_params.keys():
                input.linked_visual_parameters[key] = linked_vis_params[key]
        return input


class WorkflowInputBoolean(BaseWorkflowInput):

    def __init__(self, name: str, label: str, description: str, default_value: bool, linked_visual_parameters, parameter_group: str = None):
        super().__init__("bool", name, label, description, default_value, linked_visual_parameters, parameter_group)

    def get_wellknown_workflow_input(self):
        input = BooleanWorkflowInput()
        input.default_value = self.get_default_value()

        workflow_input = super().get_wellknown_workflow_input()
        workflow_input.generic_input.Pack(input)
        return workflow_input


class WorkflowInputInteger(BaseWorkflowInput):

    def __init__(self, name: str, label: str, description: str, 
                 default_value: int, minimum_value: int, maximum_value: int, 
                 linked_visual_parameters,
                 render_as: RenderNumberAsType,
                 parameter_group: str = None):
        super().__init__("int", name, label, description, default_value, linked_visual_parameters, parameter_group)
        self._minimum_value = minimum_value
        self._maximum_value = maximum_value
        self._render_as = render_as

    def get_minimum_value(self):
        return self._minimum_value

    def get_maximum_value(self):
        return self._maximum_value

    def get_wellknown_workflow_input(self):
        input = IntegerWorkflowInput()
        input.default_value = self.get_default_value()
        input.minimum = self.get_minimum_value() or 0
        input.maximum = self.get_maximum_value() or 0
        input.has_minimum = self.get_minimum_value() is not None
        input.has_maximum = self.get_maximum_value() is not None
        input.render_as = self._render_as

        workflow_input = super().get_wellknown_workflow_input()
        workflow_input.generic_input.Pack(input)
        return workflow_input


class WorkflowInputDouble(BaseWorkflowInput):

    def __init__(self, name: str, label: str, description: str, 
                 default_value: float, minimum_value: float, maximum_value: float, 
                 measurement_name: str, display_symbol: str, 
                 linked_visual_parameters,
                 show_increment: bool, increment: float,
                 decimal_places: int,
                 render_as: RenderNumberAsType,
                 parameter_group: str = None):
        super().__init__("double", name, label, description, default_value, linked_visual_parameters, parameter_group)
        self._minimum_value = minimum_value
        self._maximum_value = maximum_value
        self._measurement_name = measurement_name
        self._display_symbol = display_symbol
        self._show_increment = show_increment
        self._increment = increment
        self._decimal_places = decimal_places
        self._render_as = render_as

    def get_minimum_value(self):
        return self._minimum_value

    def get_maximum_value(self):
        return self._maximum_value

    def get_measurement_name(self):
        return self._measurement_name

    def get_display_symbol(self):
        return self._display_symbol

    def get_show_increment(self):
        return self._show_increment
    
    def get_increment(self):
        return self._increment
    
    def get_decimal_places(self):
        return self._decimal_places
    
    def get_wellknown_workflow_input(self):
        input = DoubleWorkflowInput()
        input.default_value = self.get_default_value()
        input.minimum = self.get_minimum_value() or 0
        input.maximum = self.get_maximum_value() or 0
        input.has_minimum = self.get_minimum_value() is not None
        input.has_maximum = self.get_maximum_value() is not None
        input.measurement_name = self.get_measurement_name() or ""
        input.display_symbol = self.get_display_symbol() or ""
        input.render_as = self._render_as
        input.show_increment = self.get_show_increment()
        input.increment = self.get_increment() or 0
        input.decimal_places = self.get_decimal_places() or -1

        workflow_input = super().get_wellknown_workflow_input()
        workflow_input.generic_input.Pack(input)
        return workflow_input


class WorkflowInputString(BaseWorkflowInput):

    def __init__(self, name: str, label: str, description: str, default_value: str, linked_visual_parameters, parameter_group: str = None):
        super().__init__("string", name, label, description, default_value, linked_visual_parameters, parameter_group)

    def get_wellknown_workflow_input(self):
        input = StringWorkflowInput()
        input.default_value = self.get_default_value()

        workflow_input = super().get_wellknown_workflow_input()
        workflow_input.generic_input.Pack(input)
        return workflow_input


class WorkflowInputEnum(BaseWorkflowInput):

    def __init__(self, name: str, label: str, description: str, 
                 options: Dict[int, str], default_value: int, 
                 linked_visual_parameters: Dict[str, str],
                 render_as: RenderEnumAsType,
                 parameter_group: str = None):
        super().__init__("enum", name, label, description, default_value, linked_visual_parameters, parameter_group)
        self._options = options
        self._render_as = render_as

    def get_render_as(self):
        return str(self._render_as)
    
    def get_wellknown_workflow_input(self):
        input = EnumWorkflowInput()
        input.default_value = self.get_default_value()
        for key, value in self._options.items():
            enum_option = EnumOption()
            enum_option.key = key
            enum_option.value = value
            input.enum_options.append(enum_option)
        input.render_as = self._render_as

        workflow_input = super().get_wellknown_workflow_input()
        workflow_input.generic_input.Pack(input)
        return workflow_input


class WorkflowInputFile(BaseWorkflowInput):

    def __init__(self, name: str, label: str, description: str, file_extensions: str, 
                 linked_visual_parameters: Dict[str, str], 
                 select_multiple: bool, 
                 parameter_group: str = None):
        super().__init__("file", name, label, description, None, linked_visual_parameters, parameter_group)
        self._file_extensions = file_extensions
        self._select_multiple = select_multiple

    def get_file_extensions(self) -> bool:
        return self._file_extensions

    def get_select_multiple(self) -> bool:
        return self._select_multiple

    def get_wellknown_workflow_input(self):
        input = FileWorkflowInput()
        input.file_extensions = self.get_file_extensions()
        input.select_multiple = self.get_select_multiple()

        workflow_input = super().get_wellknown_workflow_input()
        workflow_input.generic_input.Pack(input)
        return workflow_input


class WorkflowInputFolder(BaseWorkflowInput):

    def __init__(self, name: str, label: str, description: str, default_value: str, linked_visual_parameters: Dict[str, str], parameter_group: str = None):
        super().__init__("folder", name, label, description, default_value, linked_visual_parameters, parameter_group)

    def get_wellknown_workflow_input(self):
        input = FolderWorkflowInput()
        input.default_value = self.get_default_value() or ""

        workflow_input = super().get_wellknown_workflow_input()
        workflow_input.generic_input.Pack(input)
        return workflow_input


class WorkflowInputObjectRef(BaseWorkflowInput):

    def __init__(self, name: str, label: str, description: str, 
                 object_name: str, template_names: List[str], measurement_name: str, select_multiple: bool, 
                 linked_input_name: str, 
                 linked_visual_parameters: Dict[str, str],
                 parameter_group: str = None):
        super().__init__("object_ref", name, label, description, None, linked_visual_parameters, parameter_group)
        self._object_name = object_name
        self._template_names = template_names
        self._measurement_name = measurement_name
        self._select_multiple = select_multiple
        self._linked_input_name = linked_input_name

    def get_object_name(self) -> str:
        return self._object_name

    def get_template_names(self) -> List[str]:
        return self._template_names

    def get_measurement_name(self) -> str:
        return self._measurement_name

    def get_select_multiple(self) -> bool:
        return self._select_multiple

    def get_linked_input_name(self) -> str:
        return self._linked_input_name

    def get_wellknown_workflow_input(self):
        input = ObjectRefWorkflowInput()
        input.object_name = self.get_object_name()
        template_names = self.get_template_names()
        if template_names:
            input.property_name = ';'.join(template_names)
        else:
            input.property_name = ""
        input.measurement_name = self.get_measurement_name() or ""
        input.select_multiple = self.get_select_multiple() or False
        input.linked_input_name = self.get_linked_input_name() or ""

        workflow_input = super().get_wellknown_workflow_input()
        workflow_input.generic_input.Pack(input)
        return workflow_input


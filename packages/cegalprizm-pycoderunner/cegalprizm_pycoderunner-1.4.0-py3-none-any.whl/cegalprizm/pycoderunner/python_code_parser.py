# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
from typing import List
from enum import Enum
import re

from . import logger
from .constants import _PWR_IDENTIFIER, _PWR_CLASS_NAME

class _DescriptionCode:
    def __init__(self, is_valid: bool, variable_name: str = None, code: str = None, error_message: str = None):
        self._is_valid = is_valid
        if (is_valid):
            self._variable_name = variable_name
            self._code = code
            self._error_message = ""
        else:
            self._variable_name = ""
            self._code = ""
            self._error_message = error_message

    def is_valid(self) -> bool:
        return self._is_valid

    def error_message(self) -> str:
        return self._error_message if not self._is_valid else ""

    def variable_name(self) -> str:
        return self._variable_name if self._is_valid else ""

    def code(self) -> str:
        return self._code if self._is_valid else ""

class _ParsedDescription:
    def __init__(self, 
                 description_code: _DescriptionCode = None,
                 pycoderunner_imports: List[str] = None, 
                 investigator_imports: List[str] = None, 
                 other_cegalprizm_imports: List[str] = None,
                 error_message: str = None):
        self._description_code = description_code if error_message is None else None
        self._pycoderunner_imports = pycoderunner_imports if error_message is None else []
        self._investigator_imports = investigator_imports if error_message is None else []
        self._other_cegalprizm_imports = other_cegalprizm_imports if error_message is None else []
        self._error_message = error_message

    def is_valid(self) -> bool:
        return self._error_message is None and self._description_code is not None and self._description_code.is_valid()
    
    def get_description_code(self) -> _DescriptionCode:
        return self._description_code if self._error_message is None else None

    def get_pycoderunner_imports(self) -> List[str]:
        return self._pycoderunner_imports if self.is_valid() else []

    def get_investigator_imports(self) -> List[str]:
        return self._investigator_imports if self.is_valid() else []

    def get_other_cegalprizm_imports(self) -> List[str]:
        return self._other_cegalprizm_imports if self.is_valid() else []

    def error_message(self) -> List[str]:
        if self._error_message is not None:
            return self._error_message
        if self._description_code is not None:
            return self._description_code.error_message()
        return ""


    def unlicensed(self) -> bool:
        return len(self.get_other_cegalprizm_imports()) == 0 and len(self.get_investigator_imports()) > 0
    
class _ImportPatternEnum(Enum):
    PYCODERUNNER = "pycoderunner"
    INVESTIGATOR = "investigator"
    OTHER_CEGALPRIZM = "other_cegalprizm"

class _PythonCodeParser():

    IMPORT_PATTERN = r'^\s*(import|from)\s'
    PYCODERUNNER_PATTERN = r'^\s*(import|from)\s.*cegalprizm\.pycoderunner.*'
    INVESTIGATOR_PATTERN = r'^\s*(import|from)\s.*cegalprizm\.investigator.*'
    OTHER_CEGALPRIZM_PATTERN = r'^\s*(import|from)\s.*cegalprizm(?!\.(investigator|pycoderunner|hub)).*'

    def __new__(cls):
        raise TypeError("This is a static class and cannot be instantiated.")

    @staticmethod
    def _get_import_pattern(pattern: _ImportPatternEnum) -> str:
        if pattern == _ImportPatternEnum.PYCODERUNNER:
            return _PythonCodeParser.PYCODERUNNER_PATTERN
        elif pattern == _ImportPatternEnum.INVESTIGATOR:
            return _PythonCodeParser.INVESTIGATOR_PATTERN
        elif pattern == _ImportPatternEnum.OTHER_CEGALPRIZM:
            return _PythonCodeParser.OTHER_CEGALPRIZM_PATTERN
        else:
            raise ValueError(f"Unknown import pattern: {pattern}")

    @staticmethod
    def _get_imports(code_lines: List[str], pattern: _ImportPatternEnum) -> List[str]:
        import_lines = []
        i = 0
        while i < len(code_lines):
            line = code_lines[i].strip()
            if re.match(_PythonCodeParser._get_import_pattern(pattern), line):
                full_import = line
                if line.endswith('(') or line.endswith('\\'):
                    j = i + 1
                    while j < len(code_lines) and ')' not in code_lines[j] and not re.match(_PythonCodeParser.IMPORT_PATTERN, code_lines[j]):
                        full_import += ' ' + code_lines[j].strip()
                        j += 1
                    if j < len(code_lines) and ')' in code_lines[j]:
                        full_import += ' ' + code_lines[j].strip()
                        i = j
                import_lines.append(full_import)
            i += 1
        return import_lines

    @staticmethod
    def _parse_description(identifier: str, class_name: str, filename: str, lines: List[str]) -> _DescriptionCode:
        count = 0
        start_description_line = -1
        stop_description_line = -1
        description_found = False
        description_invalid = False
        code_lines: List[str] = []
        variables: List[str] = []

        # Strips the newline character
        for line in lines:
            stripped_line = line.strip()
            if stripped_line == f"# Start: {identifier}":
                start_description_line = count
            if stripped_line == f"# End: {identifier}":
                stop_description_line = count
                break
            stripped_line = stripped_line.replace(" ", "")
            index = stripped_line.find(f"={class_name}(")
            if index > 0:
                description_found = True
                description_invalid = start_description_line == -1
                variables.append(stripped_line[0:index])

            if start_description_line != -1 and count > start_description_line and stop_description_line == -1:
                code_lines.append(line)
            count += 1

        if start_description_line == -1 and stop_description_line == -1 and not description_found:
            return None

        if start_description_line == -1 and stop_description_line == -1 and description_invalid:
            return _DescriptionCode(False, error_message=f'{filename}: {class_name} defined outside a {identifier} block')

        if start_description_line >= 0 and stop_description_line == -1:
            return _DescriptionCode(False, error_message=f'{filename}: End: {identifier} not valid')

        if start_description_line == -1 and stop_description_line >= 0:
            return _DescriptionCode(False, error_message=f'{filename}: Start: {identifier} not valid')

        if len(variables) == 0:
            return _DescriptionCode(False, error_message=f'{filename}: No {class_name} found within {identifier} block')

        if len(variables) > 1:
            return _DescriptionCode(False, error_message=f'{filename}: Multiple {class_name} defined within {identifier} block')

        for line in code_lines:
            stripped_line = line.strip().replace(" ", "")
            if len(stripped_line) == 0:
                continue

            if line.startswith("from") or line.startswith("import"):
                continue
            elif line.startswith(variables[0]):
                continue
            elif line.startswith(" "):
                continue
            else:
                logger.warning(f'{filename}:{line}')
                logger.warning(f'{filename}: {identifier} may contain unexpected code')
                logger.warning(f'Please ensure only the {class_name} is defined in within {identifier} block')
                break

        description_code = ""
        for line in code_lines:
            description_code += f"{line}\n"

        # logger.debug(description_code)

        return _DescriptionCode(True, variable_name=variables[0], code=description_code)

    @staticmethod
    def parse_workflow_description(filename: str, lines: List[str], identifier: str = _PWR_IDENTIFIER, class_name: str = _PWR_CLASS_NAME) -> _ParsedDescription:
        description: _DescriptionCode = None
        pycoderunner_imports = []
        investigator_imports = []
        other_cegalprizm_imports = []
        try:
            description = _PythonCodeParser._parse_description(identifier, class_name, filename, lines)
            pycoderunner_imports = _PythonCodeParser._get_imports(lines, _ImportPatternEnum.PYCODERUNNER)
            investigator_imports = _PythonCodeParser._get_imports(lines, _ImportPatternEnum.INVESTIGATOR)
            other_cegalprizm_imports = _PythonCodeParser._get_imports(lines, _ImportPatternEnum.OTHER_CEGALPRIZM)
        except Exception as error:
            description = _DescriptionCode(False, error_message=f"{error}: {error.args[0]}")
        return _ParsedDescription(description, pycoderunner_imports, investigator_imports, other_cegalprizm_imports)

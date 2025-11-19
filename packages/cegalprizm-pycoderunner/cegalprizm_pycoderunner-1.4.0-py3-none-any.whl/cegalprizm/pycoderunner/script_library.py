# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

import hashlib
import sys
from . import logger
from .script import Script

this = sys.modules[__name__]
this.script_dict = {}


def add_script(code: str):
    if code is None or len(code) == 0 or str.isspace(code):
        return (False, "code must not be None, empty or whitespace")

    try:
        function_id = hashlib.sha256(code.encode('utf-8')).hexdigest()
        if function_id in this.script_dict.keys():
            logger.debug("Script already exists")
            return (True, function_id)

        try:
            logger.debug(f"Compiling script\n{code}")
            script = Script(function_id, code)
            if script.is_error:
                return (False, script.error_message)
            this.script_dict[function_id] = script
            return (True, function_id)
        except Exception as error:
            error_message = f"Exception compiling script: {type(error)}: {error}: {error.args}"
            logger.error(error_message)
            return (False, error_message)

    except Exception:
        return (False, "Script not valid")

def get_script(function_id: str) -> Script:
    if function_id not in this.script_dict.keys():
        return None

    return this.script_dict[function_id]

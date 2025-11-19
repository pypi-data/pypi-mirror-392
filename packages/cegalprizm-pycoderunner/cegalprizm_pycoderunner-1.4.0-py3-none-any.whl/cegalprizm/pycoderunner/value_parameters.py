# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

import numpy as np
from google.protobuf.any_pb2 import Any

from . import logger
from .pycoderunner_pb2 import DoubleValuePayload, Double1DPayload, Double2DPayload
from .pycoderunner_pb2 import IntValuePayload, Int1DPayload, Int2DPayload
from .pycoderunner_pb2 import BoolValuePayload, Bool1DPayload
from .pycoderunner_pb2 import StringValuePayload, String1DPayload
from .pycoderunner_pb2 import PayloadDictionary, Payload


def get_value_from_payload(parameter):
    if parameter is None:
        return (False, None)
    return get_value(parameter.content_type, parameter.content)


def get_value(content_type: str, content: Any):
    if content_type == "DoubleValuePayload":
        input = DoubleValuePayload()
        content.Unpack(input)
        return (True, input.value)
    elif content_type == "Double1DPayload":
        input = Double1DPayload()
        content.Unpack(input)
        return (True, [x for x in input.values])
    elif content_type == "Double2DPayload":
        input = Double2DPayload()
        content.Unpack(input)
        val = []
        for x in input.values:
            val.append([y for y in x.values])
        return (True, val)
    elif content_type == "IntValuePayload":
        input = IntValuePayload()
        content.Unpack(input)
        return (True, input.value)
    elif content_type == "Int1DPayload":
        input = Int1DPayload()
        content.Unpack(input)
        return (True, [x for x in input.values])
    elif content_type == "Int2DPayload":
        input = Int2DPayload()
        content.Unpack(input)
        val = []
        for x in input.values:
            val.append([y for y in x.values])
        return (True, val)
    elif content_type == "BoolValuePayload":
        input = BoolValuePayload()
        content.Unpack(input)
        return (True, input.value)
    elif content_type == "Bool1DPayload":
        input = Bool1DPayload()
        content.Unpack(input)
        return (True, [x for x in input.values])
    elif content_type == "StringValuePayload":
        input = StringValuePayload()
        content.Unpack(input)
        return (True, input.value)
    elif content_type == "String1DPayload":
        input = String1DPayload()
        content.Unpack(input)
        return (True, [x for x in input.values])
    elif content_type == "DictionaryPayload":
        input = PayloadDictionary()
        content.Unpack(input)
        dict = get_dictionary(input)
        return (True, dict)
    else:
        return (False, None)

def get_dictionary(input):
    logger.debug(input)
    dict = {}
    for item in input.dict.items():
        input = get_value_from_payload(item[1])
        if input[0]:
            if input[1] is not None:
                dict[item[0]] = input[1]
    if len(dict) == 0:
        dict = None
    logger.debug(dict)
    return dict

def get_payload(payload_type: str, values):
    output = None
    if payload_type == "DoubleValuePayload":
        output = DoubleValuePayload()
        output.value = values
    elif payload_type == "Double1DPayload":
        output = Double1DPayload()
        for x in values:
            if (isinstance(x, np.ndarray)):
                output.values.append(x[0])
            else:
                output.values.append(x)
    elif payload_type == "Double2DPayload":
        output = Double2DPayload()
        for x in values:
            inner_tuple = get_payload("Double1DPayload", x)
            output.values.append(inner_tuple[1])
    elif payload_type == "IntValuePayload":
        output = IntValuePayload()
        output.value = values
    elif payload_type == "Int1DPayload":
        output = Int1DPayload()
        for x in values:
            if (isinstance(x, np.ndarray)):
                output.values.append(x[0])
            else:
                output.values.append(x)
    elif payload_type == "Int2DPayload":
        output = Int2DPayload()
        for x in values:
            inner_tuple = get_payload("Int1DPayload", x)
            output.values.append(inner_tuple[1])
    elif payload_type == "BoolValuePayload":
        output = BoolValuePayload()
        output.value = values
    elif payload_type == "Bool1DPayload":
        output = Bool1DPayload()
        for x in values:
            if (isinstance(x, np.ndarray)):
                output.values.append(x[0])
            else:
                output.values.append(x)
    elif payload_type == "StringValuePayload":
        output = StringValuePayload()
        output.value = values
    elif payload_type == "String1DPayload":
        output = String1DPayload()
        for x in values:
            if (isinstance(x, np.ndarray)):
                output.values.append(x[0])
            else:
                output.values.append(x)
    elif payload_type == "DictionaryPayload":
        output = PayloadDictionary()
        for item in values.items():
            value_content_type = None
            if (isinstance(item[1], list) and all(isinstance(x, bool) for x in item[1])):
                value_content_type = "Bool1DPayload"
            elif (isinstance(item[1], bool)):
                value_content_type = "BoolValuePayload"
            elif (isinstance(item[1], list) and all(isinstance(x, list) and all(isinstance(y, float) for y in x) for x in item[1])):
                value_content_type = "Double2DPayload"
            elif (isinstance(item[1], list) and all(isinstance(x, float) for x in item[1])):
                value_content_type = "Double1DPayload"
            elif (isinstance(item[1], float)):
                value_content_type = "DoubleValuePayload"
            elif (isinstance(item[1], list) and all(isinstance(x, list) and all(isinstance(y, int) for y in x) for x in item[1])):
                value_content_type = "Int2DPayload"
            elif (isinstance(item[1], list) and all(isinstance(x, int) for x in item[1])):
                value_content_type = "Int1DPayload"
            elif (isinstance(item[1], int)):
                value_content_type = "IntValuePayload"
            elif (isinstance(item[1], list) and all(isinstance(x, str) for x in item[1])):
                value_content_type = "String1DPayload"
            elif (isinstance(item[1], str)):
                value_content_type = "StringValuePayload"
            elif (isinstance(item[1], dict)):
                value_content_type = "DictionaryPayload"

            if value_content_type is not None:
                value_payload = get_payload(value_content_type, item[1])
                if value_payload is not None and value_payload[0]:
                    payload = Payload()
                    payload.content_type = value_content_type
                    payload.content.Pack(value_payload[1])
                    output.dict[item[0]].CopyFrom(payload)
            else:
                logger.warning(f"Unsupported item type for key {item[0]}: {type(item[1])}")

    if output is not None:
        return (True, output)
    else:
        logger.warning(f"Unsupported payload_type {payload_type}: {type(values)}")
        return (False, None)

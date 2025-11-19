# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from .constants import DEFAULT_NUM_OF_CONCURRENT_TASKS

_num_of_concurrent_tasks = DEFAULT_NUM_OF_CONCURRENT_TASKS

def set_num_of_concurrent_tasks(num_tasks: int):
    global _num_of_concurrent_tasks
    _num_of_concurrent_tasks = num_tasks

def get_num_of_concurrent_tasks() -> int:
    global _num_of_concurrent_tasks
    return _num_of_concurrent_tasks
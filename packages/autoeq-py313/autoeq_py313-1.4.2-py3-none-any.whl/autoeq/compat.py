# -*- coding: utf-8 -*-
"""
Python version compatibility utilities for AutoEQ.

Detects Python 3.14 free-threaded mode and provides optimal executor selection.
"""

import sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Type, Union

# Detect Python 3.14 free-threaded mode
IS_FREE_THREADED = (
    sys.version_info >= (3, 13) and
    hasattr(sys, '_is_gil_enabled') and
    callable(sys._is_gil_enabled) and
    not sys._is_gil_enabled()
)

# Python version info
IS_PY313_PLUS = sys.version_info >= (3, 13)
IS_PY314_PLUS = sys.version_info >= (3, 14)

def get_optimal_executor() -> Type[Union[ThreadPoolExecutor, ProcessPoolExecutor]]:
    """
    Returns the optimal executor class based on Python version and GIL status.

    Returns:
        ThreadPoolExecutor if running in Python 3.14+ free-threaded mode,
        ProcessPoolExecutor otherwise.

    Notes:
        - Free-threaded mode provides true parallelism without GIL
        - ThreadPoolExecutor has lower memory overhead (shared memory)
        - ProcessPoolExecutor is used as fallback for GIL-bound Python
    """
    if IS_FREE_THREADED:
        return ThreadPoolExecutor
    else:
        return ProcessPoolExecutor


def get_executor_info() -> dict:
    """
    Returns information about the current executor configuration.

    Returns:
        Dictionary with Python version, GIL status, and executor type.
    """
    return {
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'is_free_threaded': IS_FREE_THREADED,
        'is_py313_plus': IS_PY313_PLUS,
        'is_py314_plus': IS_PY314_PLUS,
        'executor_type': 'ThreadPoolExecutor' if IS_FREE_THREADED else 'ProcessPoolExecutor',
    }

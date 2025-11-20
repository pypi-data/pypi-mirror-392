# -*- coding: utf-8 -*-

from __future__ import annotations

import re

import numpy as np
import numpy.typing as npt
from scipy.special import expit


def generate_frequencies(f_min: float, f_max: float, f_step: float) -> npt.NDArray[np.float64]:
    """Generate logarithmically spaced frequency array.

    Args:
        f_min: Minimum frequency
        f_max: Maximum frequency
        f_step: Multiplicative step size

    Returns:
        Array of frequencies
    """
    frequencies = []
    f = f_min
    while f <= f_max:
        frequencies.append(f)
        f *= f_step
    return np.array(frequencies)


def log_tilt(f: npt.NDArray[np.float64], steepness: float) -> npt.NDArray[np.float64]:
    """Creates a tilt for equalization.

    Args:
        f: Frequency array
        steepness: Slope steepness in dB/octave

    Returns:
        Tilted data
    """
    # Center frequency in logarithmic scale
    c = 20.0 * np.sqrt(20000.0 / 20.0)
    # N octaves above center
    n_oct = np.log2(f / c)
    return n_oct * steepness


def smoothing_window_size(f: npt.NDArray[np.float64], octaves: float) -> int:
    """Calculates moving average window size in indices from octaves.

    Args:
        f: Frequency array
        octaves: Window size in octaves

    Returns:
        Window size in array indices (always odd number)
    """
    # Octaves to coefficient
    k = 2 ** octaves
    # Calculate average step size in frequencies
    steps = []
    for i in range(1, len(f)):
        steps.append(f[i] / f[i - 1])
    step_size = sum(steps) / len(steps)
    # Calculate window size in indices
    # step_size^x = k  --> x = ...
    n = np.log(k) / np.log(step_size)
    # Round to integer to be usable as index
    n = round(n)
    if not n % 2:
        n += 1
    return n


def log_f_sigmoid(
        f: npt.NDArray[np.float64],
        f_lower: float,
        f_upper: float,
        a_normal: float = 0.0,
        a_treble: float = 1.0
) -> npt.NDArray[np.float64]:
    f_center = np.sqrt(f_upper / f_lower) * f_lower
    half_range = np.log10(f_upper) - np.log10(f_center)
    f_center = np.log10(f_center)
    a = expit((np.log10(f) - f_center) / (half_range / 4))
    a = a * -(a_normal - a_treble) + a_normal
    return a


def log_log_gradient(f0: float, f1: float, g0: float, g1: float) -> float:
    """Calculates gradient (derivative) in dB per octave.

    Args:
        f0: Starting frequency
        f1: Ending frequency
        g0: Gain at f0
        g1: Gain at f1

    Returns:
        Gradient in dB per octave
    """
    octaves = np.log(f1 / f0) / np.log(2)
    gain = g1 - g0
    return gain / octaves


def is_file_name_allowed(name: str) -> bool:
    """Check if a file name is allowed on Windows and other systems.

    Args:
        name: File name to check

    Returns:
        True if the name is allowed, False otherwise
    """
    return not (
        # Prohibited file name characters, including ASCII control characters
        bool(re.search(r'[<>:"/\\\|\?\*\u0000-\u001F]', name))
        # Windows has some reserved file names
        or bool(re.match(r'(?:CON|PRN|AUX|NUL|COM1|COM2|COM3|COM4|COM5|COM6|COM7|COM8|COM9|LPT1|LPT2|LPT3|LPT4|LPT5|LPT6|LPT7|LPT8|LPT9)(?:\.[a-zA-Z0-9]+)?$', name))
        # Files on Windows cannot end in space or dot
        or bool(re.search(r'[ \.]$', name))
    )


def make_file_name_allowed(name: str) -> str:
    # Remove prohibited characters
    name = re.sub(r'[<>:"/\\\|\?\*\u0000-\u001F]', '', name)
    # Add suffix for reserved file names
    name = re.sub(
        r'(CON|PRN|AUX|NUL|COM1|COM2|COM3|COM4|COM5|COM6|COM7|COM8|COM9|LPT1|LPT2|LPT3|LPT4|LPT5|LPT6|LPT7|LPT8|LPT9)(\.[a-zA-Z0-9]+)?$',
        '\1-tmp\2',
        name)
    # Remove leading dot and space
    name = re.sub(r'[ \.]$', '', name)
    return name


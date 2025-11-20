"""
SP1000G Logic Analyzer Python API

This package provides Python bindings for the Ikalogic SP1000G Logic Analyzer.

Example:
    >>> from ikalogic import sp1000g
    >>> api = sp1000g.SP1000G(sp1000g.Model.SP1054G)
    >>> api.create_device_list()
    >>> print(f"Found {api.get_devices_count()} devices")
"""

__version__ = "0.1.0"

# Add the package directory to DLL search path on Windows
import os
import sys
if sys.platform == 'win32':
    # Add package directory to DLL search path for Python 3.8+
    if hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(os.path.dirname(__file__))
    else:
        # For Python 3.7 and earlier, add to PATH
        os.environ['PATH'] = os.path.dirname(__file__) + os.pathsep + os.environ.get('PATH', '')

# Import the C++ extension module
from . import _sp1000g_py

# Re-export everything from the C++ module for convenience
from ._sp1000g_py import *

# Make common classes available at package level
SP1000G = _sp1000g_py.SP1000G
DeviceDescriptor = _sp1000g_py.DeviceDescriptor
Settings = _sp1000g_py.Settings
TriggerDescription = _sp1000g_py.TriggerDescription

# Enums
Model = _sp1000g_py.Model
ErrorCode = _sp1000g_py.ErrorCode
TriggerType = _sp1000g_py.TriggerType
StateClkMode = _sp1000g_py.StateClkMode
TimebaseClk = _sp1000g_py.TimebaseClk
IOType = _sp1000g_py.IOType
Pull = _sp1000g_py.Pull

# Constants
CHANNELS_COUNT = _sp1000g_py.CHANNELS_COUNT
GROUPS_COUNT = _sp1000g_py.GROUPS_COUNT

__all__ = [
    'SP1000G',
    'DeviceDescriptor',
    'Settings',
    'TriggerDescription',
    'Model',
    'ErrorCode',
    'TriggerType',
    'StateClkMode',
    'TimebaseClk',
    'IOType',
    'Pull',
    'CHANNELS_COUNT',
    'GROUPS_COUNT',
]

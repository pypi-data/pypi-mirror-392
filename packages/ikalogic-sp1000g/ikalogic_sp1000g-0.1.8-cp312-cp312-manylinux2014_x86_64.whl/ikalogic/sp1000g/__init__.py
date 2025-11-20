"""
SP1000G Logic Analyzer Python API

This package provides Python bindings for the Ikalogic SP1000G Logic Analyzer.

Example:
    >>> from ikalogic import sp1000g
    >>> api = sp1000g.SP1000G(sp1000g.Model.SP1054G)
    >>> api.create_device_list()
    >>> print(f"Found {api.get_devices_count()} devices")
"""

# Get version from package metadata
try:
    from importlib.metadata import version
    __version__ = version("ikalogic-sp1000g")
except ImportError:
    # Fallback for Python < 3.8
    try:
        from importlib_metadata import version
        __version__ = version("ikalogic-sp1000g")
    except ImportError:
        __version__ = "unknown"

# Preload native libraries to ensure they can be found
import os
import sys
import ctypes

package_dir = os.path.dirname(__file__)

# Linux: Check if LD_LIBRARY_PATH includes our package directory
# If not, restart Python with the correct path
if sys.platform not in ['win32', 'darwin']:
    ld_path = os.environ.get('LD_LIBRARY_PATH', '')
    if package_dir not in ld_path.split(':'):
        # Need to restart Python with LD_LIBRARY_PATH set
        new_ld_path = package_dir + (':' + ld_path if ld_path else '')
        os.environ['LD_LIBRARY_PATH'] = new_ld_path
        
        # Re-execute Python with the new environment
        try:
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception:
            # If exec fails, continue anyway (might still work in some cases)
            pass

# Preload platform-specific libraries before importing the C++ module
if sys.platform == 'win32':
    # Windows: Add package directory to DLL search path
    if hasattr(os, 'add_dll_directory'):
        # Python 3.8+
        os.add_dll_directory(package_dir)
    else:
        # Python 3.7 and earlier, add to PATH
        os.environ['PATH'] = package_dir + os.pathsep + os.environ.get('PATH', '')
    
    # Preload Windows DLLs
    for dll in ['FTD3XX.dll', 'FTD3XXWU.dll', 'libsp1000g_api.dll', 'sp1000g_api.dll']:
        dll_path = os.path.join(package_dir, dll)
        if os.path.exists(dll_path):
            try:
                ctypes.CDLL(dll_path)
            except OSError:
                pass  # DLL might depend on other DLLs we haven't loaded yet
                
elif sys.platform == 'darwin':
    # macOS: Preload dylibs
    for dylib in ['libftd3xx.dylib', 'libsp1000g_api.dylib']:
        dylib_path = os.path.join(package_dir, dylib)
        if os.path.exists(dylib_path):
            try:
                ctypes.CDLL(dylib_path, mode=ctypes.RTLD_GLOBAL)
            except OSError:
                pass
else:
    # Linux: Preload .so files
    for so in ['libftd3xx.so', 'libsp1000g_api.so']:
        so_path = os.path.join(package_dir, so)
        if os.path.exists(so_path):
            try:
                ctypes.CDLL(so_path, mode=ctypes.RTLD_GLOBAL)
            except OSError:
                pass

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

"""Natural Language Processing Engine"""


# start delvewheel patch
def _delvewheel_patch_1_11_2():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'iknowpy.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-iknowpy-1.5.4')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-iknowpy-1.5.4')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_11_2()
del _delvewheel_patch_1_11_2
# end delvewheel patch

# provide useful error message when accidentally imported from source directory
import os
import inspect
file_directory = os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda: 0)))
if os.path.isfile(os.path.join(file_directory, 'SOURCE')):
    raise ImportError(
        f'You have imported the source package {file_directory} instead of the '
        'installed package, which is not allowed. This occurred because the '
        '`iknowpy\' package source is in the directory where the import '
        'occurred and took precedence over the installed package. If you tried '
        'importing `iknowpy\' from the Python interactive console, change your '
        'working directory and try again. If you tried importing `iknowpy\' '
        'within a Python script, move the script to a different directory.'
    )
del os, inspect, file_directory

# export public variables and classes
from .version import __version__
from .labels import Labels
from .engine import iKnowEngine, UserDictionary

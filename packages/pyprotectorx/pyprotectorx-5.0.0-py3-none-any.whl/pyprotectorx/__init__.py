"""PyProtectorX - PPX ENCRYPTION
Universal package for Python 3.11 and 3.12
Auto-detects Python version and loads appropriate core
"""
import sys

__version__ = "5.0.0"
__author__ = "Zain Alkhalil"
__all__ = ["dumps", "Run"]

if sys.version_info < (3, 11):
    raise ImportError(
        f"PyProtectorX requires Python 3.11 or 3.12\n"
        f"Current version: Python {sys.version_info.major}.{sys.version_info.minor}\n"
        f"Please upgrade Python"
    )

_py_version = f"{sys.version_info.major}{sys.version_info.minor}"

try:
    if sys.version_info >= (3, 12):
        from .core_312 import dumps, Run
    elif sys.version_info >= (3, 11):
        from .core_311 import dumps, Run
    else:
        raise ImportError(f"Unsupported Python {sys.version_info.major}.{sys.version_info.minor}")
except ImportError as e:
    available_cores = []
    import os
    pkg_dir = os.path.dirname(__file__)
    for f in os.listdir(pkg_dir):
        if f.startswith('core_') and f.endswith('.py'):
            available_cores.append(f.replace('core_', '').replace('.py', ''))
    
    raise ImportError(
        f"Failed to load core for Python {sys.version_info.major}.{sys.version_info.minor}\n"
        f"Available: {', '.join(available_cores) if available_cores else 'None'}\n"
        f"Try: pip install --force-reinstall pyprotectorx"
    ) from e

def get_version_info():
    return {
        'version': __version__,
        'author': __author__,
        'python': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'core': f"core_{_py_version}",
    }

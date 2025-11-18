"""PyProtectorX - Mobile Edition"""
import sys

__version__ = "5.1.0"
__author__ = "Zain Alkhalil"
__all__ = ["encrypt", "run", "protect"]

if sys.version_info < (3, 11):
    raise ImportError(
        f"❌ PyProtectorX requires Python 3.11+\n"
        f"Current: Python {sys.version_info.major}.{sys.version_info.minor}"
    )

# Auto-detect Python version and load appropriate core
_py_ver = f"{sys.version_info.major}{sys.version_info.minor}"

try:
    if sys.version_info >= (3, 12):
        from .core_312 import encrypt_code, run_encrypted
    elif sys.version_info >= (3, 11):
        from .core_311 import encrypt_code, run_encrypted
    else:
        raise ImportError(f"Unsupported Python {sys.version_info.major}.{sys.version_info.minor}")
except ImportError as e:
    raise ImportError(
        f"❌ Failed to load core for Python {sys.version_info.major}.{sys.version_info.minor}\n"
        f"Try: pip install --force-reinstall pyprotectorx"
    ) from e

def encrypt(source_code):
    """Encrypt Python source code"""
    if not isinstance(source_code, str):
        raise TypeError("Source must be string")
    return encrypt_code(source_code)

def run(encrypted_data):
    """Run encrypted code"""
    if not isinstance(encrypted_data, bytes):
        raise TypeError("Data must be bytes")
    return run_encrypted(encrypted_data)

def protect(input_file, output_file=None):
    """Protect Python file"""
    import base64
    from pathlib import Path
    
    inp = Path(input_file)
    if not inp.exists():
        raise FileNotFoundError(f"Not found: {input_file}")
    
    source = inp.read_text(encoding='utf-8')
    encrypted = encrypt(source)
    
    if output_file is None:
        output_file = inp.with_stem(inp.stem + ".protected")
    else:
        output_file = Path(output_file)
    
    b64 = base64.b64encode(encrypted).decode('ascii')
    
    code = f"""#!/usr/bin/env python3
# Protected by PyProtectorX v{__version__}
import sys
if sys.version_info < (3, 11):
    print("❌ Python 3.11+ required!")
    sys.exit(1)

DATA = "{b64}"

def main():
    try:
        from pyprotectorx import run
        import base64
        run(base64.b64decode(DATA))
    except ImportError:
        print("❌ PyProtectorX not installed!")
        print("Install: pip install pyprotectorx")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
    
    output_file.write_text(code, encoding='utf-8')
    try:
        os.chmod(output_file, 0o755)
    except:
        pass
    
    return str(output_file)

def info():
    """Show info"""
    return {
        'version': __version__,
        'author': __author__,
        'python': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }

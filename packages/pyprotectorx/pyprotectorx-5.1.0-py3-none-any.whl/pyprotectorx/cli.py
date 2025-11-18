"""PyProtectorX CLI"""
import sys
import argparse
from pathlib import Path

if sys.version_info < (3, 11):
    print("❌ Python 3.11+ required!")
    sys.exit(1)

from . import protect, __version__

def main():
    parser = argparse.ArgumentParser(
        description=f'PyProtectorX v{__version__}',
        epilog="Example: pyprotectorx script.py"
    )
    
    parser.add_argument('input', nargs='?', help='Python file')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('--version', action='version', version=f'v{__version__}')
    
    args = parser.parse_args()
    
    if not args.input:
        parser.print_help()
        return
    
    inp = Path(args.input)
    if not inp.exists():
        print(f"❌ Not found: {inp}")
        sys.exit(1)
    
    try:
        src = inp.read_text(encoding='utf-8')
        compile(src, str(inp), 'exec')
    except SyntaxError as e:
        print(f"❌ Syntax error: Line {e.lineno}: {e.msg}")
        sys.exit(1)
    
    try:
        print(f"🔒 Protecting {inp.name}...")
        out = protect(str(inp), args.output)
        print(f"✓ {Path(out).name} ({Path(out).stat().st_size:,} bytes)")
    except Exception as e:
        print(f"❌ {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

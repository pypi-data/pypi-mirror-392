"""PyProtectorX CLI"""
import sys,base64,argparse
from pathlib import Path
if sys.version_info<(3,11):print(f"❌ Python 3.11+ required!");sys.exit(1)
from . import dumps,Run,__version__ as V,__author__ as A
C="PPX ENCRYPTION"
def cpf(e,o):
    b=base64.b64encode(e).decode('ascii')
    c=f"""#!/usr/bin/env python3
# Protected by {C} v{V}
DataEncoded="{b}"
def Run():
    import sys
    if sys.version_info<(3,11):print("❌ Python 3.11+ required!");sys.exit(1)
    try:
        from pyprotectorx import Run as PPXRun
        import base64
        PPXRun(base64.b64decode(DataEncoded))
    except ImportError:print("❌ PyProtectorX not installed!");sys.exit(1)
    except Exception as e:print(f"❌ {{e}}");sys.exit(1)
if __name__=="__main__":Run()
"""
    o.write_text(c,encoding='utf-8')
    try:os.chmod(o,0o755)
    except:pass
def main():
    p=argparse.ArgumentParser(description=f'PyProtectorX v{V}')
    p.add_argument('--version',action='version',version=f'PyProtectorX {V}')
    s=p.add_subparsers(dest='command')
    e=s.add_parser('encrypt',help='Encrypt Python file')
    e.add_argument('input',type=str,help='Input file')
    e.add_argument('-o','--output',type=str,help='Output file')
    a=p.parse_args()
    if not a.command:p.print_help();return
    if a.command=='encrypt':
        i=Path(a.input)
        if not i.exists():print(f"❌ Not found: {i}");sys.exit(1)
        try:src=i.read_text();compile(src,str(i),'exec')
        except SyntaxError as se:print(f"❌ Syntax error: {se}");sys.exit(1)
        try:
            print("🔒 Encrypting...");enc=dumps(src)
            o=Path(a.output)if a.output else i.with_suffix('.protected.py')
            cpf(enc,o);print(f"✓ {o} ({len(enc)} bytes)")
        except Exception as ex:print(f"❌ {ex}");sys.exit(1)
if __name__=='__main__':main()

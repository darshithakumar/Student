#!/usr/bin/env python
"""
Ultimate Python 3.14 + SQLAlchemy 2.0 compatibility launcher
Patches typing module at the absolute earliest possible point
"""
import sys
import os

# CRITICAL: Patch typing.Generic BEFORE anything else imports typing
import typing
import inspect

# Get the original Generic class
_OriginalGeneric = typing.Generic

# Create a TypingOnly marker that doesn't trigger the assertion
class _TypingOnlyType(type):
    """Metaclass that allows TypingOnly to have attributes"""
    pass

class TypingOnly(metaclass=_TypingOnlyType):
    """Typing-only base class that works with Python 3.14"""
    __slots__ = ()

# Monkey-patch TypingOnly into typing module
typing.TypingOnly = TypingOnly

# Patch Generic's __init_subclass__ to be more lenient
_original_generic_init = _OriginalGeneric.__init_subclass__

@classmethod  
def _patched_init_subclass(cls, **kwargs):
    """Patched __init_subclass__ that ignores TypingOnly issues"""
    # Try original, but catch TypingOnly assertion errors
    try:
        return _original_generic_init(**kwargs)
    except (AssertionError, TypeError) as e:
        error_msg = str(e)
        # Ignore specific typing errors we can't fix
        if any(x in error_msg for x in ['TypingOnly', 'is not a generic class']):
            return None
        raise

typing.Generic.__init_subclass__ = _patched_init_subclass

# Environment setup
os.environ['SQLALCHEMY_SILENCE_UBER_WARNING'] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

# Setup paths
Backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(Backend_dir)
sys.path.insert(0, Backend_dir)

# Load .env
from dotenv import load_dotenv
load_dotenv()

print("\n" + "="*60)
print("[*] College Academic Portal Backend")
print("="*60)
print(f"[DIR] Directory: {os.getcwd()}")
print(f"[PY] Python: {sys.version.split()[0]}")
print(f"[CFG] Patches: typing.TypingOnly, Generic.__init_subclass__\n")

# Try to start uvicorn
try:
    import uvicorn
    
    print("[NET] Uvicorn configuration:")
    print("   Host: 0.0.0.0")
    print("   Port: 8000")
    print("   Docs: http://localhost:8000/docs")
    print("   Reload: False\n")
    print("[INFO] Press Ctrl+C to stop\n")
    
    # Run the app
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
    
except ImportError as e:
    print(f"[ERROR] Import Error: {e}")
    print("\nInstall uvicorn: pip install uvicorn")
    sys.exit(1)
    
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

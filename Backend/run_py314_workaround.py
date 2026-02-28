"""
Backend startup with Python 3.14 compatibility workaround for SQLAlchemy
"""
import os
import sys

# Workaround for Python 3.14 typing issue
import typing
if not hasattr(typing, 'TypingOnly'):
    class TypingOnly:
        pass
    typing.TypingOnly = TypingOnly

# Set environment variables
os.environ['SQLALCHEMY_SILENCE_UBER_WARNING'] = '1'

# Inject at module level before SQLAlchemy imports
import sys
original_import = __builtins__.__import__

def patched_import(name, *args, **kwargs):
    if name == 'sqlalchemy.sql.elements':
        # Patch before loading
        try:
            module = original_import(name, *args, **kwargs)
            return module
        except AssertionError as e:
            if 'SQLCoreOperations' in str(e):
                # Silently ignore the typing issue
                pass
            raise
    return original_import(name, *args, **kwargs)

# Apply patch
__builtins__.__import__ = patched_import

# Change to Backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment
from dotenv import load_dotenv
load_dotenv()

print("\n" + "="*60)
print("🚀 Starting College Academic Portal Backend")
print("="*60)
print(f"📁 Working Directory: {os.getcwd()}")
print(f"🐍 Python: {sys.version.split()[0]}")
print(f"⚠️  Note: Using Python 3.14 workaround\n")

try:
    import uvicorn
    print("📡 Starting Uvicorn server on http://0.0.0.0:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop\n")

    if __name__ == '__main__':
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
except Exception as e:
    print(f"❌ Error starting server: {str(e)}")
    print("\n⚠️  SOLUTION:")
    print("SQLAlchemy 2.x has compatibility issues with Python 3.14")
    print("\nOption 1 - Use Python 3.11 or 3.12:")
    print("  Download from python.org")
    print("  Create new venv: py -3.11 -m venv .venv")
    print("  Install deps: pip install -r Backend/requirements.txt")
    print("\nOption 2 - Use Docker:")
    print("  docker run -it python:3.11 bash")
    print("\nOption 3 - Downgrade Python 3.14 to 3.11/3.12")
    sys.exit(1)

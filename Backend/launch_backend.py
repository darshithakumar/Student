"""
Backend launcher with aggressive Python 3.14 SQLAlchemy compatibility patches
"""
import sys
import os
from pathlib import Path

# Step 1: Patch typing module BEFORE any other imports
import typing

# Create a TypingOnly class that passes Python 3.14's checks
class TypingOnly:
    """Marker class for typing-only bases"""
    __slots__ = ()
    
    def __init_subclass__(cls, **kwargs):
        # Allow subclasses to have attributes despite being TypingOnly
        super().__init_subclass__(**kwargs)

# Ensure TypingOnly is available
if not hasattr(typing, 'TypingOnly'):
    typing.TypingOnly = TypingOnly
else:
    # Replace the existing one with our patched version
    typing.TypingOnly = TypingOnly

# Step 2: Monkey-patch Generic to be more lenient
original_generic_init_subclass = typing.Generic.__init_subclass__

def patched_generic_init_subclass(cls, **kwargs):
    """Patched __init_subclass__ that's lenient about TypingOnly"""
    try:
        return original_generic_init_subclass(**kwargs)
    except AssertionError as e:
        if 'TypingOnly' in str(e):
            # Silently ignore TypingOnly assertion errors
            return None
        raise

typing.Generic.__init_subclass__ = classmethod(patched_generic_init_subclass)

# Step 3: Set environment variables
os.environ['SQLALCHEMY_SILENCE_UBER_WARNING'] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

# Step 4: Setup paths
Backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(Backend_dir)
sys.path.insert(0, Backend_dir)

# Step 5: Load environment
from dotenv import load_dotenv
load_dotenv()

print("\n" + "="*60)
print("🚀 Starting College Academic Portal Backend")
print("="*60)
print(f"📁 Working Directory: {os.getcwd()}")
print(f"🐍 Python: {sys.version.split()[0]}")
print(f"⚙️  Patches Applied: TypingOnly compatibility\n")

# Step 6: Try to import and start server
try:
    # Test imports with patches
    print("🔍 Testing SQLAlchemy import...")
    import sqlalchemy
    print(f"✅ SQLAlchemy {sqlalchemy.__version__} loaded successfully")
    
    print("🔍 Testing database connection...")
    from sqlalchemy import inspect
    from app.database import engine
    
    with engine.connect() as conn:
        print("✅ Database connection successful!")
    
    # Start the server
    print("\n📡 Starting Uvicorn server on http://0.0.0.0:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop\n")
    
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

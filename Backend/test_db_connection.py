#!/usr/bin/env python
"""Test PostgreSQL database connection"""
import sys
import os

# CRITICAL: Patch typing BEFORE anything else imports typing
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
    try:
        return _original_generic_init(**kwargs)
    except (AssertionError, TypeError) as e:
        error_msg = str(e)
        if any(x in error_msg for x in ['TypingOnly', 'is not a generic class']):
            return None
        raise

typing.Generic.__init_subclass__ = _patched_init_subclass

# Load environment
from dotenv import load_dotenv
load_dotenv()

print("[TEST] PostgreSQL Connection Test")
print("=" * 60)

# Test database URL
db_url = os.getenv("DATABASE_URL")
print(f"[CONFIG] DATABASE_URL: {db_url}")

try:
    # Try to import and create engine
    from sqlalchemy import create_engine, text
    
    print("[IMPORT] SQLAlchemy imported successfully")
    
    # Create engine
    engine = create_engine(
        db_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False
    )
    
    print("[ENGINE] Engine created successfully")
    
    # Test connection
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("[SUCCESS] Database connection successful!")
        print(f"[RESULT] Query result: {result.fetchone()}")
    
    # Try to create tables
    from app.models import Base
    print("[MODELS] Models imported successfully")
    
    Base.metadata.create_all(bind=engine)
    print("[SUCCESS] Tables created/verified successfully!")
    
    print("\n" + "=" * 60)
    print("[✓] Database is ready to use!")
    print("=" * 60)
    
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

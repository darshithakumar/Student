"""
Backend startup script - sets up environment and starts uvicorn server
"""
import sys
import os

# Ensure we're in the Backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment
from dotenv import load_dotenv
load_dotenv()

print("\n" + "="*60)
print("🚀 Starting College Academic Portal Backend")
print("="*60)
print(f"📁 Working Directory: {os.getcwd()}")
print(f"🐍 Python: {sys.executable}")
print(f"📝 Python Path: {sys.path[:2]}")

# Check database connection
try:
    print("\n🔗 Checking database connection...")
    from sqlalchemy import inspect
    from app.database import engine
    
    with engine.connect() as conn:
        print("✅ Database connection successful!")
except Exception as e:
    print(f"⚠️  Database connection warning: {str(e)}")
    print("   Note: Database will be created on first request if it doesn't exist")

# Start uvicorn
print("\n📡 Starting Uvicorn server on http://0.0.0.0:8000")
print("📚 API Docs: http://localhost:8000/docs")
print("🛑 Press Ctrl+C to stop\n")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disabled reload on Windows multiprocessing issue
        log_level="info"
    )

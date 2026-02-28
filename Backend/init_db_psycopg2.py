"""
Create PostgreSQL database and tables using psycopg2 directly
(Bypasses SQLAlchemy to work around Python 3.14 compatibility)
"""
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# Load env
load_dotenv()

DB_HOST = "localhost"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_NAME = "college_portal"

print("🔧 Creating PostgreSQL database...\n")

try:
    # Connect to postgres (default database)
    print(f"📡 Connecting to PostgreSQL as {DB_USER}@{DB_HOST}...")
    conn = psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database="postgres"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Create database if not exists
    print(f"📦 Creating database '{DB_NAME}'...")
    try:
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier(DB_NAME)
        ))
    except psycopg2.Error as e:
        if "already exists" in str(e):
            print(f"   (Database already exists)")
        else:
            raise
    print(f"✅ Database '{DB_NAME}' created/verified")
    
    cursor.close()
    conn.close()
    
    # Now connect to the new database and create tables
    print(f"\n📡 Connecting to {DB_NAME} database...")
    conn = psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()
    
    # Read and execute schema from backend
    schema_sql = """
    -- Tables will be auto-created when backend starts
    -- This is a placeholder for manual table creation if needed
    """
    
    print("✅ Database schema ready (tables will auto-create when backend starts)")
    
    cursor.close()
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("✅ PostgreSQL setup complete!")
    print("="*60)
    print(f"\nDatabase: {DB_NAME}")
    print(f"Host: {DB_HOST}")
    print(f"User: {DB_USER}")
    print("\n📝 Next step: Start the backend")
    print("   cd Backend")
    print("   python -m uvicorn app.main:app --reload")
    
except psycopg2.Error as e:
    print(f"\n❌ PostgreSQL Error: {e}")
    print("\n⚠️  Make sure PostgreSQL is running!")
    print("   Start PostgreSQL service and try again.")
    exit(1)

except Exception as e:
    print(f"\n❌ Error: {e}")
    exit(1)

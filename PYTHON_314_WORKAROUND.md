# ⚠️ PYTHON 3.14 COMPATIBILITY WORKAROUND

Due to Python 3.14's strict typing validation, SQLAlchemy has compatibility issues. Here's the complete manual setup:

## OPTION 1: Manual PostgreSQL Setup (Recommended)

### Step 1: Install PostgreSQL
If not already installed:
- Download: https://www.postgresql.org/download/windows/
- Install with default settings
- Default user: `postgres`
- Default password: `postgres` (or use your own)

### Step 2: Create Database
Open PowerShell and run:

```powershell
# Start PostgreSQL service
Start-Service postgresql-x64-*

# Create database using psql
psql -U postgres -c "CREATE DATABASE college_portal;"

# Verify it was created
psql -U postgres -c "\l"
```

### Step 3: Update .env File
Edit `Backend\.env` with your PostgreSQL credentials:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/college_portal
SECRET_KEY=college-portal-2024-super-secret-key-min-32-chars-change-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DEBUG=True
ENVIRONMENT=development
```

### Step 4: Start Backend (Tables Auto-Create)
```powershell
cd d:\Clg\Backend
& 'd:\Clg\.venv\Scripts\python.exe' -m uvicorn app.main:app --reload
```

FastAPI will automatically create all tables on first run!

---

## OPTION 2: Use Python 3.11 or 3.12

If you have Python 3.11 or 3.12 installed:

### Step 1: Create New Virtual Environment
```powershell
cd d:\Clg
# Remove old venv
Remove-Item -Recurse .venv

# Create new venv with Python 3.12
py -3.12 -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1
```

### Step 2: Install Packages
```powershell
pip install -r Backend\requirements.txt
```

### Step 3: Run Database Setup
```powershell
cd Backend
python setup_db.py
```

---

## OPTION 3: Frontend-Only Setup (Skip Database for Now)

If you just want to build and test the frontend:

```powershell
cd d:\Clg
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173` and can test API with backend running separately.

---

## ✅ WHAT TO DO NOW

**Recommended path forward:**

1. **Use OPTION 1** (Manual PostgreSQL setup) - Most reliable
   - Takes 5 minutes
   - No Python version issues
   - Database will auto-create tables on server start

2. **Start Backend Server**
   ```powershell
   cd d:\Clg\Backend
   & 'd:\Clg\.venv\Scripts\python.exe' -m uvicorn app.main:app --reload
   ```

3. **Access API Documentation**
   - Open browser: `http://localhost:8000/docs`
   - Test endpoints directly in Swagger UI
   - Use test credentials:
     - Email: `john.doe@college.edu`
     - Password: `TestPassword123!`

4. **Initialize Frontend** (Next step)
   ```powershell
   cd d:\Clg
   npm create vite@latest frontend -- --template react
   ```

---

## 📚 Complete Flow

```
PostgreSQL Running
    ↓
.env Configured  
    ↓
Backend Started (uvicorn)
    ↓
Tables Auto-Created (SQLAlchemy)
    ↓
Test Student Auto-Seeded (if needed)
    ↓
API Ready at http://localhost:8000
    ↓
Frontend Connects to API
```

---

## 🧪 Test Backend is Running

```powershell
# Health check
Invoke-WebRequest -Uri "http://localhost:8000/"

# Swagger UI
Start-Process "http://localhost:8000/docs"
```

---

Help! I'll provide direct commands.

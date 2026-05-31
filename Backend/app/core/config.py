import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is missing! Please set it securely.")
    
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

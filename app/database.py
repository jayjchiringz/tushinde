import os
import socket
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv # type: ignore

# -------------------------------
# 🔧 Load .env from root
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)
# -------------------------------


# -------------------------------
# 🔌 Get DB URL from environment
# -------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

def is_postgres_reachable(host: str, port: int = 5432, timeout: int = 3) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket().connect((host, port))
        return True
    except socket.error:
        return False
# -------------------------------


# -------------------------------
# 🔁 Fallback Logic
# -------------------------------
if not DATABASE_URL or "localhost" in DATABASE_URL or "supabase" in DATABASE_URL:
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(DATABASE_URL)
        hostname = parsed_url.hostname or "localhost"

        if not is_postgres_reachable(hostname):
            raise ConnectionError(f"Database host {hostname} not reachable.")
    except Exception as e:
        print(f"[⚠️ DB FALLBACK] {e}")
        DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'app', 'db.sqlite3')}"
        print(f"[ℹ️ USING SQLITE] {DATABASE_URL}")
# -------------------------------


# -------------------------------
# 🛠️ SQLAlchemy Engine
# -------------------------------
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# -------------------------------

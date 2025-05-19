import os
import socket
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv # type: ignore
from urllib.parse import urlparse

# -------------------------------
# 🔧 Load environment
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)

# -------------------------------
# 🔍 Get initial DATABASE_URL
# -------------------------------
raw_url = os.getenv("DATABASE_URL", "").strip()
fallback_sqlite = f"sqlite:///{os.path.join(BASE_DIR, 'app', 'db.sqlite3')}"

# -------------------------------
# 🧠 Function: Check remote DB reachability
# -------------------------------
def is_host_reachable(url: str, timeout: int = 3) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme != "postgresql":
            return True  # non-network db (e.g. SQLite) is fine

        host = parsed.hostname
        port = parsed.port or 5432
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception as e:
        print(f"[❌ DB UNREACHABLE] {e}")
        return False

# -------------------------------
# 🔁 Apply fallback if needed
# -------------------------------
if not raw_url or not is_host_reachable(raw_url):
    print(f"[⚠️ FALLBACK] Switching to SQLite DB at {fallback_sqlite}")
    DATABASE_URL = fallback_sqlite
else:
    DATABASE_URL = raw_url

# -------------------------------
# 🛠️ SQLAlchemy setup
# -------------------------------
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

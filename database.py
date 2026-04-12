import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "3306")
DB_NAME     = os.getenv("DB_NAME", "kentech_roi")
DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def wait_for_db(retries: int = 10, delay: int = 3) -> None:
    """Attend que MySQL accepte les connexions (utile en Docker)."""
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"[DB] Connecté à MySQL ({DB_HOST}:{DB_PORT}/{DB_NAME})")
            return
        except Exception as e:
            print(f"[DB] Tentative {attempt}/{retries} — {type(e).__name__}: {e}")
            if attempt < retries:
                time.sleep(delay)
    raise RuntimeError("Impossible de se connecter à MySQL après plusieurs tentatives.")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.settings import settings

# SQLAlchemy engine
engine = create_engine(settings.APP_DB_URL, echo=False, future=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model class
Base = declarative_base()

def get_db():
    """Database session dependency for routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

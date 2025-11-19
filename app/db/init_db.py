from app.core.db_connection import Base, engine
from app.db import models  # noqa: F401 (import models to register them)


def init_db():
    """Creates internal DB tables if they don't exist."""
    Base.metadata.create_all(bind=engine)

import uuid
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.types import JSON
from sqlalchemy.sql import func
from app.core.db_connection import Base


class DBConfig(Base):
    __tablename__ = "db_config"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    db_type = Column(String, nullable=False)
    connection_string = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DQReport(Base):
    __tablename__ = "dq_reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    run_mode = Column(String, default="manual")
    severity_counts = Column(JSON)
    report_markdown = Column(Text)
    report_html = Column(Text)
    report_json = Column(JSON)
    run_metadata = Column(JSON)
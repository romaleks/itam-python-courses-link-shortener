import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def _uuid4_as_str() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(UTC)


class Link(Base):
    __tablename__ = "link"

    id = Column(Text, default=_uuid4_as_str, primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    short_link = Column(Text, nullable=False, unique=True)
    real_link = Column(Text, nullable=False)


class LinkUsage(Base):
    __tablename__ = 'link_usage'

    id = Column(Text, default=_uuid4_as_str, primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    link_id = Column(Text, nullable=False)
    ip_address = Column(Text, nullable=True)
    user_agent = Column(Text, nullable=True)
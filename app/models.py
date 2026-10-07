from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    event_name = Column(String, nullable=False)
    issuer_name = Column(String, nullable=False)

    status = Column(
        String,
        nullable=False,
        default="PENDING"
    )

    total_recipients = Column(Integer, nullable=False)
    successful_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    failed_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    recipients = relationship(
        "Recipient",
        back_populates="job",
        cascade="all, delete-orphan"
    )


class Recipient(Base):
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=False
    )

    name = Column(String, nullable=False)
    email = Column(String, nullable=False)

    status = Column(
        String,
        nullable=False,
        default="PENDING"
    )

    certificate_path = Column(
        String,
        nullable=True
    )

    error_message = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    job = relationship(
        "Job",
        back_populates="recipients"
    )
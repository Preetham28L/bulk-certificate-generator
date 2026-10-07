from pathlib import Path
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from . import models
from .database import Base, engine, get_db
from .schemas import JobCreate
from services.job_processor import process_job


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Bulk Certificate Generator",
    description="API for generating certificates in bulk",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Bulk Certificate Generator API is running"
    }


@app.post("/jobs")
def create_job(
    job_data: JobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job = models.Job(
        event_name=job_data.event_name,
        issuer_name=job_data.issuer_name,
        total_recipients=len(job_data.recipients),
        status="PENDING",
    )

    db.add(job)
    db.flush()

    for recipient_data in job_data.recipients:
        recipient = models.Recipient(
            job_id=job.id,
            name=recipient_data.name,
            email=recipient_data.email,
            status="PENDING",
        )

        db.add(recipient)

    db.commit()
    db.refresh(job)

    background_tasks.add_task(
        process_job,
        job.id,
    )

    return {
        "job_id": job.id,
        "status": job.status,
        "total_recipients": job.total_recipients,
    }
@app.get("/jobs/{job_id}")
def get_job_status(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = (
        db.query(models.Job)
        .filter(models.Job.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    pending_count = (
        db.query(models.Recipient)
        .filter(
            models.Recipient.job_id == job_id,
            models.Recipient.status.in_(
                ["PENDING", "PROCESSING"]
            )
        )
        .count()
    )

    return {
        "job_id": job.id,
        "event_name": job.event_name,
        "issuer_name": job.issuer_name,
        "status": job.status,
        "total_recipients": job.total_recipients,
        "successful_count": job.successful_count,
        "failed_count": job.failed_count,
        "pending_count": pending_count,
        "created_at": job.created_at,
        "completed_at": job.completed_at,
    }
@app.get("/jobs/{job_id}/certificates")
def list_certificates(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = (
        db.query(models.Job)
        .filter(models.Job.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    recipients = (
        db.query(models.Recipient)
        .filter(
            models.Recipient.job_id == job_id,
            models.Recipient.status == "SUCCESS"
        )
        .all()
    )

    return {
        "job_id": job.id,
        "total_certificates": len(recipients),
        "certificates": [
            {
                "recipient_id": recipient.id,
                "recipient_name": recipient.name,
                "status": recipient.status,
                "certificate_path": recipient.certificate_path,
            }
            for recipient in recipients
        ],
    }
@app.get("/certificates/{recipient_id}")
def download_certificate(
    recipient_id: int,
    db: Session = Depends(get_db),
):
    recipient = (
        db.query(models.Recipient)
        .filter(models.Recipient.id == recipient_id)
        .first()
    )

    if not recipient:
        raise HTTPException(
            status_code=404,
            detail="Recipient not found"
        )

    if recipient.status != "SUCCESS":
        raise HTTPException(
            status_code=404,
            detail="Certificate has not been generated"
        )

    if not recipient.certificate_path:
        raise HTTPException(
            status_code=404,
            detail="Certificate file not found"
        )

    certificate_file = Path(recipient.certificate_path)

    if not certificate_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Certificate file not found"
        )

    return FileResponse(
        path=certificate_file,
        media_type="application/pdf",
        filename=f"{recipient.name}_certificate.pdf",
    )
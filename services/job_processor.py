from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config import CERTIFICATE_DIR
from app.database import SessionLocal
from app.models import Job, Recipient
from services.certificate_generator import generate_certificate

def process_job(job_id: int):
    db: Session = SessionLocal()

    try:
        job = db.query(Job).filter(Job.id == job_id).first()

        if not job:
            return

        job.status = "PROCESSING"
        db.commit()

        recipients = (
            db.query(Recipient)
            .filter(Recipient.job_id == job_id)
            .all()
        )

        for recipient in recipients:
            try:
                recipient.status = "PROCESSING"
                db.commit()

                output_path = (
                    CERTIFICATE_DIR
                    / f"job_{job.id}"
                    / f"recipient_{recipient.id}.pdf"
                    )

                generate_certificate(
                    recipient_name=recipient.name,
                    event_name=job.event_name,
                    issuer_name=job.issuer_name,
                    output_path=str(output_path),
                )

                recipient.status = "SUCCESS"
                recipient.certificate_path = str(output_path)

                job.successful_count += 1

            except Exception as error:
                recipient.status = "FAILED"
                recipient.error_message = str(error)

                job.failed_count += 1

            db.commit()

        job.status = (
            "COMPLETED_WITH_ERRORS"
            if job.failed_count > 0
            else "COMPLETED"
        )

        job.completed_at = datetime.now(timezone.utc)

        db.commit()

    finally:
        db.close()